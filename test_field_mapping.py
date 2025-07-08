#!/usr/bin/env python3
"""
Test script for field mapping functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.field_mapper import FieldMapper, FieldMapping
from dataclasses import dataclass

@dataclass
class MockCalculation:
    """Mock calculation for testing"""
    name: str
    formula: str
    calculation_type: str = "basic"
    data_type: str = "real"
    dependencies: list = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class MockWorkbook:
    """Mock workbook structure for testing"""
    calculations: dict
    datasources: list
    parameters: list

def test_field_mapping():
    """Test field mapping functionality"""
    print("🧪 Testing Field Mapping System")
    print("=" * 50)
    
    # Create test data
    calculations = {
        "[2022_(copy)_(copy)_780248699807363141]": MockCalculation(
            "[2022_(copy)_(copy)_780248699807363141]",
            "SUM([Sales])",
            "basic",
            "real"
        ),
        "[Order Date]": MockCalculation(
            "[Order Date]",
            "[Order Date]",
            "dimension",
            "date"
        ),
        "[Customer-Name]": MockCalculation(
            "[Customer-Name]",
            "[Customer Name]",
            "dimension",
            "string"
        ),
        "[Profit Margin %]": MockCalculation(
            "[Profit Margin %]",
            "[Profit] / [Sales]",
            "basic",
            "real"
        )
    }
    
    workbook = MockWorkbook(
        calculations=calculations,
        datasources=[],
        parameters=[]
    )
    
    # Test field mapper
    mapper = FieldMapper()
    
    print("1. Testing field extraction...")
    fields = mapper.extract_fields_from_workbook(workbook)
    print(f"   ✓ Extracted {len(fields)} fields")
    
    print("\n2. Testing field mappings...")
    for field in fields:
        print(f"   Tableau: {field.tableau_field}")
        print(f"   Display: {field.display_name}")
        print(f"   Python:  {field.python_name}")
        print(f"   Valid:   {'✓' if field.is_valid else '✗'}")
        if not field.is_valid:
            print(f"   Error:   {field.validation_error}")
        print()
    
    print("3. Testing validation...")
    valid_count, invalid_count = mapper.validate_all_mappings()
    print(f"   ✓ Valid mappings: {valid_count}")
    print(f"   ✗ Invalid mappings: {invalid_count}")
    
    print("\n4. Testing updates...")
    # Try to update a mapping
    test_field = "[2022_(copy)_(copy)_780248699807363141]"
    success = mapper.update_mapping(test_field, "sales_2022_copy", "Sales 2022 (Copy)")
    print(f"   Update result: {'✓' if success else '✗'}")
    
    updated_mapping = mapper.get_mapping(test_field)
    if updated_mapping:
        print(f"   Updated Python name: {updated_mapping.python_name}")
        print(f"   Updated display label: {updated_mapping.display_label}")
    
    print("\n5. Testing export/import...")
    # Export mappings
    json_data = mapper.export_mappings()
    print(f"   ✓ Exported {len(json_data)} characters of JSON")
    
    # Create new mapper and import
    new_mapper = FieldMapper()
    import_success = new_mapper.import_mappings(json_data)
    print(f"   Import result: {'✓' if import_success else '✗'}")
    
    # Verify import worked
    imported_mapping = new_mapper.get_mapping(test_field)
    if imported_mapping:
        print(f"   Imported Python name: {imported_mapping.python_name}")
    
    print("\n6. Testing summary stats...")
    stats = mapper.get_summary_stats()
    print(f"   Total fields: {stats['total_fields']}")
    print(f"   Valid mappings: {stats['valid_mappings']}")
    print(f"   Invalid mappings: {stats['invalid_mappings']}")
    print(f"   Validation rate: {stats['validation_rate']:.1f}%")
    print(f"   Field types: {stats['field_types']}")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    test_field_mapping()