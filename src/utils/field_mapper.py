"""
Field Mapping System - Maps Tableau field names to Python-compatible variable names
"""
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import keyword

logger = logging.getLogger(__name__)


@dataclass
class FieldMapping:
    """Represents a mapping between Tableau field and Python variable"""
    tableau_field: str  # Original Tableau field name (e.g., "[2022_(copy)_(copy)_780248699807363141]")
    display_name: str   # Human-readable display name (e.g., "2022 (copy) (copy)")
    python_name: str    # Python-compatible variable name (e.g., "sales_2022_copy")
    display_label: str  # User-friendly label for UI (e.g., "Sales 2022 (Copy)")
    field_type: str     # Type: 'calculation', 'dimension', 'measure', 'parameter'
    data_type: str      # Data type: 'string', 'integer', 'real', 'boolean', 'date'
    is_valid: bool = True  # Whether the python_name is valid
    validation_error: Optional[str] = None


class FieldMapper:
    """Manages field mappings for Tableau to Python conversion"""
    
    def __init__(self):
        self.mappings: Dict[str, FieldMapping] = {}
        self.reserved_names = set(keyword.kwlist + ['data', 'df', 'result', 'value', 'index'])
    
    def extract_fields_from_workbook(self, workbook_structure: Any) -> List[FieldMapping]:
        """Extract all field names from workbook structure"""
        fields = []
        
        # Extract from calculations
        for calc_name, calculation in workbook_structure.calculations.items():
            # Clean up the display name
            display_name = self._clean_display_name(calc_name)
            
            # Generate Python-compatible name
            python_name = self._generate_python_name(calc_name)
            
            # Create mapping
            mapping = FieldMapping(
                tableau_field=calc_name,
                display_name=display_name,
                python_name=python_name,
                display_label=display_name,
                field_type='calculation',
                data_type=calculation.data_type,
            )
            
            # Validate the Python name
            self._validate_python_name(mapping)
            
            fields.append(mapping)
            self.mappings[calc_name] = mapping
        
        # Extract from datasources (dimensions and measures)
        for datasource in workbook_structure.datasources:
            fields.extend(self._extract_datasource_fields(datasource))
        
        # Extract from parameters
        for param in workbook_structure.parameters:
            param_name = param.get('name', '')
            if param_name:
                display_name = self._clean_display_name(param_name)
                python_name = self._generate_python_name(param_name)
                
                mapping = FieldMapping(
                    tableau_field=param_name,
                    display_name=display_name,
                    python_name=python_name,
                    display_label=display_name,
                    field_type='parameter',
                    data_type=param.get('datatype', 'string'),
                )
                
                self._validate_python_name(mapping)
                fields.append(mapping)
                self.mappings[param_name] = mapping
        
        logger.info(f"Extracted {len(fields)} fields from workbook")
        return fields
    
    def _extract_datasource_fields(self, datasource: Dict[str, Any]) -> List[FieldMapping]:
        """Extract fields from a datasource"""
        fields = []
        
        # Extract from column instances (dimensions and measures)
        for col_inst in datasource.get('column_instances', []):
            field_name = col_inst.get('name', '')
            if field_name:
                display_name = self._clean_display_name(field_name)
                python_name = self._generate_python_name(field_name)
                
                # Determine field type
                field_type = 'dimension' if col_inst.get('type') == 'discrete' else 'measure'
                
                mapping = FieldMapping(
                    tableau_field=field_name,
                    display_name=display_name,
                    python_name=python_name,
                    display_label=display_name,
                    field_type=field_type,
                    data_type=col_inst.get('datatype', 'string'),
                )
                
                self._validate_python_name(mapping)
                fields.append(mapping)
                self.mappings[field_name] = mapping
        
        return fields
    
    def _clean_display_name(self, tableau_name: str) -> str:
        """Clean up Tableau field name for display"""
        # Remove brackets and quotes
        cleaned = tableau_name.strip('[]"\'')
        
        # Handle special patterns like long IDs
        if re.match(r'^\d{4}_\(copy\)_\(copy\)_\d+$', cleaned):
            # Extract year from pattern like "2022_(copy)_(copy)_780248699807363141"
            year_match = re.match(r'^(\d{4})_\(copy\)_\(copy\)_\d+$', cleaned)
            if year_match:
                year = year_match.group(1)
                return f"{year} (copy) (copy)"
        
        # Replace underscores with spaces
        cleaned = cleaned.replace('_', ' ')
        
        # Remove excessive parentheses and clean up
        cleaned = re.sub(r'\s*\(copy\)\s*', ' (copy)', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _generate_python_name(self, tableau_name: str) -> str:
        """Generate Python-compatible variable name"""
        # Remove brackets and quotes
        cleaned = tableau_name.strip('[]"\'')
        
        # Handle special patterns
        if re.match(r'^\d{4}_\(copy\)_\(copy\)_\d+$', cleaned):
            # Extract year from pattern like "2022_(copy)_(copy)_780248699807363141"
            year_match = re.match(r'^(\d{4})_\(copy\)_\(copy\)_\d+$', cleaned)
            if year_match:
                year = year_match.group(1)
                return f"value_{year}_copy"
        
        # Convert to snake_case
        # Replace spaces and special chars with underscores
        python_name = re.sub(r'[^\w\s]', '_', cleaned)
        python_name = re.sub(r'\s+', '_', python_name)
        python_name = python_name.lower()
        
        # Remove multiple underscores
        python_name = re.sub(r'_+', '_', python_name)
        
        # Remove leading/trailing underscores
        python_name = python_name.strip('_')
        
        # Ensure it doesn't start with a digit
        if python_name and python_name[0].isdigit():
            python_name = f"field_{python_name}"
        
        # Ensure it's not empty
        if not python_name:
            python_name = "unnamed_field"
        
        # Handle reserved words
        if python_name in self.reserved_names:
            python_name = f"{python_name}_field"
        
        return python_name
    
    def _validate_python_name(self, mapping: FieldMapping) -> None:
        """Validate that the Python name is a valid identifier"""
        python_name = mapping.python_name
        
        # Check if it's a valid identifier
        if not python_name.isidentifier():
            mapping.is_valid = False
            mapping.validation_error = f"'{python_name}' is not a valid Python identifier"
            return
        
        # Check if it's a reserved keyword
        if python_name in keyword.kwlist:
            mapping.is_valid = False
            mapping.validation_error = f"'{python_name}' is a Python reserved keyword"
            return
        
        # Check for common conflicts
        if python_name in self.reserved_names:
            mapping.is_valid = False
            mapping.validation_error = f"'{python_name}' conflicts with common variable names"
            return
        
        # Check for duplicates
        for existing_name, existing_mapping in self.mappings.items():
            if (existing_name != mapping.tableau_field and 
                existing_mapping.python_name == python_name):
                mapping.is_valid = False
                mapping.validation_error = f"'{python_name}' already used for field '{existing_name}'"
                return
        
        mapping.is_valid = True
        mapping.validation_error = None
    
    def update_mapping(self, tableau_field: str, python_name: str, display_label: str) -> bool:
        """Update an existing mapping"""
        if tableau_field not in self.mappings:
            return False
        
        mapping = self.mappings[tableau_field]
        old_python_name = mapping.python_name
        
        # Update the mapping
        mapping.python_name = python_name
        mapping.display_label = display_label
        
        # Validate the new name
        self._validate_python_name(mapping)
        
        # If validation failed, revert the change
        if not mapping.is_valid:
            mapping.python_name = old_python_name
            return False
        
        return True
    
    def get_mapping(self, tableau_field: str) -> Optional[FieldMapping]:
        """Get mapping for a specific field"""
        return self.mappings.get(tableau_field)
    
    def get_all_mappings(self) -> List[FieldMapping]:
        """Get all field mappings"""
        return list(self.mappings.values())
    
    def get_valid_mappings(self) -> List[FieldMapping]:
        """Get only valid field mappings"""
        return [mapping for mapping in self.mappings.values() if mapping.is_valid]
    
    def get_invalid_mappings(self) -> List[FieldMapping]:
        """Get only invalid field mappings"""
        return [mapping for mapping in self.mappings.values() if not mapping.is_valid]
    
    def export_mappings(self) -> str:
        """Export mappings to JSON string"""
        data = {
            'mappings': [asdict(mapping) for mapping in self.mappings.values()],
            'version': '1.0'
        }
        return json.dumps(data, indent=2)
    
    def import_mappings(self, json_data: str) -> bool:
        """Import mappings from JSON string"""
        try:
            data = json.loads(json_data)
            
            # Clear existing mappings
            self.mappings.clear()
            
            # Import mappings
            for mapping_data in data.get('mappings', []):
                mapping = FieldMapping(**mapping_data)
                self.mappings[mapping.tableau_field] = mapping
            
            # Re-validate all mappings
            for mapping in self.mappings.values():
                self._validate_python_name(mapping)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to import mappings: {e}")
            return False
    
    def get_python_name_for_field(self, tableau_field: str) -> str:
        """Get the Python name for a Tableau field (for code generation)"""
        mapping = self.mappings.get(tableau_field)
        if mapping and mapping.is_valid:
            return mapping.python_name
        
        # Fallback to auto-generated name
        return self._generate_python_name(tableau_field)
    
    def get_display_label_for_field(self, tableau_field: str) -> str:
        """Get the display label for a Tableau field"""
        mapping = self.mappings.get(tableau_field)
        if mapping:
            return mapping.display_label
        
        # Fallback to cleaned display name
        return self._clean_display_name(tableau_field)
    
    def validate_all_mappings(self) -> Tuple[int, int]:
        """Validate all mappings and return (valid_count, invalid_count)"""
        valid_count = 0
        invalid_count = 0
        
        for mapping in self.mappings.values():
            self._validate_python_name(mapping)
            if mapping.is_valid:
                valid_count += 1
            else:
                invalid_count += 1
        
        return valid_count, invalid_count
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics about the mappings"""
        total = len(self.mappings)
        valid = sum(1 for m in self.mappings.values() if m.is_valid)
        invalid = total - valid
        
        field_types = {}
        for mapping in self.mappings.values():
            field_types[mapping.field_type] = field_types.get(mapping.field_type, 0) + 1
        
        return {
            'total_fields': total,
            'valid_mappings': valid,
            'invalid_mappings': invalid,
            'field_types': field_types,
            'validation_rate': (valid / total * 100) if total > 0 else 0
        }