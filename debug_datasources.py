#!/usr/bin/env python3
"""
Debug script to understand why datasources count is 44 instead of 1
"""
import sys
sys.path.append('.')

from src.parsers.twbx_parser import TWBXParser
from src.parsers.data_source_detector import DataSourceDetector

def debug_datasources():
    """Debug datasource parsing"""
    
    print("🔍 DEBUG: Datasource Parsing Analysis")
    print("="*60)
    
    # Parse workbook
    parser = TWBXParser()
    workbook = parser.parse('SuperStore Business Dashboard 2025 _ VOTD _ VizOfTheDay.twbx')
    
    print(f"📊 Raw datasources count: {len(workbook.datasources)}")
    print()
    
    # Analyze each datasource entry
    print("🔍 Analyzing each datasource entry:")
    for i, ds in enumerate(workbook.datasources):
        print(f"  {i+1}. Name: '{ds.get('name', 'NO_NAME')}'")
        print(f"     Caption: '{ds.get('caption', 'NO_CAPTION')}'")
        print(f"     Inline: {ds.get('inline', False)}")
        print(f"     Connections: {len(ds.get('connections', []))}")
        print(f"     Columns: {len(ds.get('columns', []))}")
        
        # Show connection details
        if ds.get('connections'):
            conn = ds['connections'][0]
            print(f"     Connection class: {conn.get('class', 'NO_CLASS')}")
        
        print()
    
    # Now apply the detector's filtering
    detector = DataSourceDetector()
    unique_sources = detector._get_unique_sources(workbook.datasources)
    
    print(f"🔍 After filtering: {len(unique_sources)} unique sources")
    print()
    
    # Show what got filtered out
    print("📋 What got filtered out:")
    print("   • Parameters datasources")
    print("   • Datasources without connections")
    print("   • Duplicate name/caption combinations")
    print()
    
    # Show the filtering logic
    print("🔧 Filtering logic:")
    seen_names = set()
    filtered_out = []
    
    for i, ds in enumerate(workbook.datasources):
        name = ds.get('name', '')
        caption = ds.get('caption', '')
        
        # Check if it's parameters
        if name == 'Parameters' or caption == 'Parameters':
            filtered_out.append(f"  {i+1}. '{name}' - Parameters")
            continue
        
        # Check if it has connections
        if not ds.get('connections'):
            filtered_out.append(f"  {i+1}. '{name}' - No connections")
            continue
        
        # Check for duplicates
        key = f"{name}_{caption}"
        if key in seen_names:
            filtered_out.append(f"  {i+1}. '{name}' - Duplicate")
            continue
        
        seen_names.add(key)
        print(f"  ✓ {i+1}. '{name}' - Kept")
    
    print()
    print("❌ Filtered out:")
    for item in filtered_out:
        print(item)
    
    # Show the actual problem
    print()
    print("🎯 THE PROBLEM:")
    print("   • TWBXParser._extract_datasources() finds ALL datasource XML elements")
    print("   • This includes calculated fields, parameters, and other non-data sources")
    print("   • The count shown in the app (44) is the raw count before filtering")
    print("   • The DataSourceDetector correctly filters to 1 actual data source")
    print()
    
    print("🔧 THE SOLUTION:")
    print("   • Use DataSourceDetector.detect_data_sources() instead of raw datasources")
    print("   • Update app.py to show len(detected_sources) instead of len(workbook.datasources)")
    print("   • This will show the correct count of actual data sources")

if __name__ == "__main__":
    debug_datasources()