# Field Mapping Guide

## Overview

The Field Mapping system solves the critical problem of Tableau field names that cannot be used as Python variable names. For example, a Tableau field named `[2022_(copy)_(copy)_780248699807363141]` cannot be used directly in Python code.

## Features

### 1. Automatic Field Extraction
- Extracts all field names from Tableau workbooks
- Identifies calculations, dimensions, measures, and parameters
- Processes both raw XML field names and display names

### 2. Python Name Generation
- Automatically generates Python-compatible variable names
- Handles special patterns like cryptic IDs with timestamps
- Converts to snake_case format
- Avoids Python reserved keywords and common conflicts

### 3. User-Guided Mapping Interface
- **Field Overview**: Shows total fields, validation status, and field type breakdown
- **Filtering**: Filter by field type, validation status, or search by name
- **Editable Mappings**: Edit Python variable names and display labels
- **Real-time Validation**: Ensures all names are valid Python identifiers
- **Bulk Operations**: Regenerate all names, export/import mappings

### 4. Validation System
- Validates Python identifiers
- Checks for reserved keywords
- Prevents name conflicts
- Blocks code generation if invalid mappings exist

## Usage Workflow

1. **Upload & Analyze**: Upload your Tableau workbook and analyze it
2. **Field Mapping**: Navigate to the "Field Mapping" tab
3. **Review Fields**: Check which fields have invalid Python names (marked with ❌)
4. **Edit Mappings**: Click on invalid fields to edit their Python names and display labels
5. **Validate**: Ensure all mappings are valid (✅) before proceeding
6. **Generate**: Proceed to generate the Streamlit application

## Field Types

- **Calculations**: Computed fields with formulas
- **Dimensions**: Categorical fields used for grouping
- **Measures**: Numeric fields used for aggregation
- **Parameters**: User-configurable values

## Example Mappings

| Tableau Field | Display Name | Python Name | Display Label |
|---------------|--------------|-------------|---------------|
| `[2022_(copy)_(copy)_780248699807363141]` | "2022 (copy) (copy)" | `sales_2022_copy` | "Sales 2022 (Copy)" |
| `[Order Date]` | "Order Date" | `order_date` | "Order Date" |
| `[Customer-Name]` | "Customer Name" | `customer_name` | "Customer Name" |
| `[Profit Margin %]` | "Profit Margin %" | `profit_margin_pct` | "Profit Margin %" |

## Import/Export

### Export Mappings
- Download field mappings as JSON file
- Useful for backup and sharing between projects
- Includes all field metadata and validation status

### Import Mappings
- Upload previously exported JSON mapping files
- Automatically validates imported mappings
- Overwrites existing mappings

## Best Practices

1. **Meaningful Names**: Use descriptive, business-friendly variable names
2. **Consistent Naming**: Follow consistent naming conventions (snake_case)
3. **Avoid Conflicts**: Don't use names that might conflict with Python built-ins
4. **Document Complex Fields**: Use clear display labels for complex calculations
5. **Export Mappings**: Save mappings for reuse in similar projects

## Error Handling

The system provides clear error messages for:
- Invalid Python identifiers
- Reserved keyword conflicts
- Duplicate variable names
- Empty or malformed names

## Technical Details

### FieldMapper Class
- **Location**: `src/utils/field_mapper.py`
- **Purpose**: Core logic for field extraction and validation
- **Key Methods**:
  - `extract_fields_from_workbook()`: Extract all fields from workbook
  - `validate_python_name()`: Validate Python identifiers
  - `export_mappings()` / `import_mappings()`: JSON serialization

### Integration
- **StreamlitGenerator**: Uses mappings to generate proper Python code
- **Session State**: Maintains mappings across tab navigation
- **Validation**: Prevents code generation with invalid mappings

## Future Enhancements

- Auto-suggestions for field names based on context
- Pattern-based bulk renaming
- Integration with data dictionary/schema
- Field usage analytics
- Custom naming conventions per organization