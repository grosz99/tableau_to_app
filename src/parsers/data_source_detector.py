"""
Data Source Detector - Identifies actual data sources used in Tableau workbooks
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

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
        
        # Extract connection details (safely)
        connection_details = {
            'class': connection_type,
            'server': primary_connection.get('server', ''),
            'database': primary_connection.get('dbname', ''),
            'schema': primary_connection.get('schema', ''),
            'warehouse': primary_connection.get('warehouse', ''),
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
        
        # Simple mapping - primary source feeds all worksheets
        primary_source = next((s for s in sources if s.is_primary), None)
        
        if primary_source:
            primary_source.worksheets_using = list(worksheets.keys())
    
    def get_recommended_connection(self) -> Optional[DataSourceInfo]:
        """Get the recommended data source for replication"""
        
        primary = next((s for s in self.detected_sources if s.is_primary), None)
        return primary or (self.detected_sources[0] if self.detected_sources else None)