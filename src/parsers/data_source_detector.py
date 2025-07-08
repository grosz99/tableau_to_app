"""
Data Source Detector - Identifies actual data sources used in Tableau workbooks
"""
import logging
import zipfile
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DataSourceInfo:
    """Information about a detected data source"""
    name: str
    caption: str
    connection_type: str  # hyper, snowflake, excel, etc.
    connection_details: Dict[str, str]
    embedded_file: Optional[str] = None
    is_primary: bool = False
    worksheets_using: List[str] = None
    
    def __post_init__(self):
        if self.worksheets_using is None:
            self.worksheets_using = []


class DataSourceDetector:
    """Detects and analyzes data sources in Tableau workbooks"""
    
    def __init__(self):
        self.detected_sources = []
        
    def detect_data_sources(self, workbook_structure) -> List[DataSourceInfo]:
        """Detect all data sources and their usage patterns"""
        
        logger.info("Detecting data sources in workbook...")
        
        # Get unique data sources (remove duplicates)
        unique_sources = self._get_unique_sources(workbook_structure.datasources)
        
        # Analyze each data source
        detected_sources = []
        for ds in unique_sources:
            source_info = self._analyze_data_source(ds)
            if source_info:
                detected_sources.append(source_info)
        
        # Identify primary data source
        primary_source = self._identify_primary_source(detected_sources)
        if primary_source:
            primary_source.is_primary = True
        
        # Map worksheets to data sources
        self._map_worksheets_to_sources(detected_sources, workbook_structure.worksheets)
        
        self.detected_sources = detected_sources
        return detected_sources
    
    def _get_unique_sources(self, datasources: List[Dict]) -> List[Dict]:
        """Remove duplicate data source entries"""
        
        unique_sources = []
        seen_names = set()
        
        for ds in datasources:
            name = ds.get('name', '')
            caption = ds.get('caption', '')
            
            # Skip parameters
            if name == 'Parameters' or caption == 'Parameters':
                continue
            
            # Skip duplicates (same name/caption combo)
            key = f"{name}_{caption}"
            if key not in seen_names and ds.get('connections'):
                seen_names.add(key)
                unique_sources.append(ds)
        
        return unique_sources
    
    def _analyze_data_source(self, datasource: Dict) -> Optional[DataSourceInfo]:
        """Analyze a single data source"""
        
        name = datasource.get('name', 'Unknown')
        caption = datasource.get('caption', name)
        connections = datasource.get('connections', [])
        
        if not connections:
            return None
        
        # Find the most specific connection
        primary_connection = self._find_primary_connection(connections)
        
        if not primary_connection:
            return None
        
        connection_type = primary_connection.get('class', 'unknown')
        
        # Extract connection details
        connection_details = {
            'class': connection_type,
            'server': primary_connection.get('server', ''),
            'database': primary_connection.get('dbname', ''),
            'schema': primary_connection.get('schema', ''),
            'warehouse': primary_connection.get('warehouse', ''),
            'username': primary_connection.get('username', ''),
        }
        
        # Check for embedded file
        embedded_file = None
        if connection_type == 'hyper':
            embedded_file = connection_details.get('database', '')
        
        return DataSourceInfo(
            name=name,
            caption=caption,
            connection_type=connection_type,
            connection_details=connection_details,
            embedded_file=embedded_file
        )
    
    def _find_primary_connection(self, connections: List[Dict]) -> Optional[Dict]:
        """Find the most specific/useful connection"""
        
        # Priority order: specific databases > hyper > excel > federated
        priority_order = ['snowflake', 'hyper', 'excel-direct', 'federated']
        
        for conn_type in priority_order:
            for conn in connections:
                if conn.get('class') == conn_type:
                    return conn
        
        # Return first if no priority match
        return connections[0] if connections else None
    
    def _identify_primary_source(self, sources: List[DataSourceInfo]) -> Optional[DataSourceInfo]:
        """Identify the primary data source"""
        
        if not sources:
            return None
        
        # Look for the most substantial data source
        # Priority: live connections > hyper extracts > excel files
        
        live_connections = [s for s in sources if s.connection_type in ['snowflake', 'postgres', 'mysql']]
        if live_connections:
            return live_connections[0]
        
        hyper_sources = [s for s in sources if s.connection_type == 'hyper']
        if hyper_sources:
            return hyper_sources[0]
        
        # Default to first source
        return sources[0]
    
    def _map_worksheets_to_sources(self, sources: List[DataSourceInfo], worksheets: Dict):
        """Map worksheets to their data sources"""
        
        # For now, simple mapping - in real implementation would parse worksheet XML
        # to find actual data source references
        primary_source = next((s for s in sources if s.is_primary), None)
        
        if primary_source:
            primary_source.worksheets_using = list(worksheets.keys())
    
    def generate_data_connection_code(self, source: DataSourceInfo) -> str:
        """Generate connection code for a data source"""
        
        if source.connection_type == 'hyper':
            return self._generate_hyper_connection(source)
        elif source.connection_type == 'snowflake':
            return self._generate_snowflake_connection(source)
        elif source.connection_type == 'excel-direct':
            return self._generate_excel_connection(source)
        else:
            return self._generate_generic_connection(source)
    
    def _generate_hyper_connection(self, source: DataSourceInfo) -> str:
        """Generate code to connect to Hyper extract"""
        
        return f'''
# Connect to Tableau Hyper Extract
import pandas as pd
from tableauhyperapi import HyperProcess, Telemetry, Connection, TableName

def load_data_from_hyper():
    """Load data from Tableau Hyper extract"""
    
    # Path to embedded hyper file
    hyper_file = "{source.embedded_file}"
    
    with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(endpoint=hyper.endpoint, database=hyper_file) as connection:
            # Get table names
            table_names = connection.catalog.get_table_names(schema_name="Extract")
            
            # Load main table (usually first one)
            if table_names:
                table_name = table_names[0]
                query = f"SELECT * FROM {{table_name}}"
                
                # Execute query and return DataFrame
                result = connection.execute_list_query(query)
                columns = [col.name for col in connection.catalog.get_table_definition(table_name).columns]
                
                return pd.DataFrame(result, columns=columns)
    
    return pd.DataFrame()  # Empty fallback

# Load the data
df = load_data_from_hyper()
'''
    
    def _generate_snowflake_connection(self, source: DataSourceInfo) -> str:
        """Generate code to connect to Snowflake"""
        
        return f'''
# Connect to Snowflake
import pandas as pd
import snowflake.connector
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
import os

def load_data_from_snowflake():
    """Load data from Snowflake"""
    
    # Connection parameters
    connection_params = {{
        'account': os.getenv('SNOWFLAKE_ACCOUNT'),
        'user': os.getenv('SNOWFLAKE_USER'),
        'password': os.getenv('SNOWFLAKE_PASSWORD'),
        'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
        'database': '{source.connection_details.get("database", "YOUR_DATABASE")}',
        'schema': '{source.connection_details.get("schema", "YOUR_SCHEMA")}',
        'role': os.getenv('SNOWFLAKE_ROLE')
    }}
    
    # Create connection
    engine = create_engine(URL(**connection_params))
    
    # Query data (adjust table name as needed)
    query = """
    SELECT * FROM YOUR_TABLE_NAME
    LIMIT 10000
    """
    
    return pd.read_sql(query, engine)

# Load the data
df = load_data_from_snowflake()
'''
    
    def _generate_excel_connection(self, source: DataSourceInfo) -> str:
        """Generate code to connect to Excel file"""
        
        return f'''
# Connect to Excel file
import pandas as pd

def load_data_from_excel():
    """Load data from Excel file"""
    
    # Note: Excel file path from Tableau may need adjustment
    excel_file = "{source.embedded_file or 'path/to/your/excel/file.xlsx'}"
    
    # Read Excel file
    df = pd.read_excel(excel_file)
    
    return df

# Load the data
df = load_data_from_excel()
'''
    
    def _generate_generic_connection(self, source: DataSourceInfo) -> str:
        """Generate generic connection code"""
        
        return f'''
# Generic data connection for {source.connection_type}
import pandas as pd

def load_data():
    """Load data from {source.caption}"""
    
    # TODO: Implement connection to {source.connection_type}
    # Connection details: {source.connection_details}
    
    # For now, return sample data
    return pd.DataFrame({{
        'Sample_Field': ['A', 'B', 'C'],
        'Sample_Value': [1, 2, 3]
    }})

# Load the data
df = load_data()
'''
    
    def create_data_source_report(self) -> str:
        """Create a comprehensive data source report"""
        
        if not self.detected_sources:
            return "No data sources detected."
        
        report = "# Data Source Analysis Report\n\n"
        
        for i, source in enumerate(self.detected_sources, 1):
            report += f"## {i}. {source.caption}\n\n"
            report += f"- **Type**: {source.connection_type}\n"
            report += f"- **Primary**: {'Yes' if source.is_primary else 'No'}\n"
            report += f"- **Worksheets Using**: {len(source.worksheets_using)}\n"
            
            if source.embedded_file:
                report += f"- **Embedded File**: {source.embedded_file}\n"
            
            report += f"- **Connection Details**:\n"
            for key, value in source.connection_details.items():
                if value:
                    report += f"  - {key}: {value}\n"
            
            report += f"- **Worksheets**: {', '.join(source.worksheets_using[:5])}\n"
            if len(source.worksheets_using) > 5:
                report += f"  ... and {len(source.worksheets_using) - 5} more\n"
            
            report += "\n"
        
        return report
    
    def get_recommended_connection(self) -> Optional[DataSourceInfo]:
        """Get the recommended data source for replication"""
        
        primary = next((s for s in self.detected_sources if s.is_primary), None)
        return primary or (self.detected_sources[0] if self.detected_sources else None)