#!/usr/bin/env python3
"""
Test script to verify the datasource count fix
"""
import sys
sys.path.append('.')

from src.parsers.twbx_parser import TWBXParser
from src.parsers.data_source_detector import DataSourceDetector

def test_datasource_count_fix():
    """Test that data source count is now correct"""
    
    print("🧪 Testing Data Source Count Fix")
    print("="*50)
    
    # Parse workbook
    parser = TWBXParser()
    workbook = parser.parse('SuperStore Business Dashboard 2025 _ VOTD _ VizOfTheDay.twbx')
    
    # Check raw datasources count (should be much lower now)
    raw_count = len(workbook.datasources)
    print(f"📊 Raw datasources from parser: {raw_count}")
    
    # Apply data source detection
    detector = DataSourceDetector()
    detected_sources = detector.detect_data_sources(workbook)
    detected_count = len(detected_sources)
    print(f"🔍 Detected actual data sources: {detected_count}")
    
    # Verify the fix
    print("\n🎯 VERIFICATION:")
    if raw_count <= 5 and detected_count == 1:
        print("✅ SUCCESS: Data source counting is now correct!")
        print(f"   • Raw parser count reduced from 65 to {raw_count}")
        print(f"   • Detected actual data sources: {detected_count}")
        print("   • The app will now show the correct count of 1 data source")
    else:
        print("❌ ISSUE: Data source counting may still have problems")
        print(f"   • Raw parser count: {raw_count} (should be ≤ 5)")
        print(f"   • Detected count: {detected_count} (should be 1)")
    
    print("\n📋 DETECTED DATA SOURCES:")
    for i, source in enumerate(detected_sources, 1):
        print(f"   {i}. {source.caption} ({source.connection_type})")
        print(f"      Used in {len(source.worksheets_using)} worksheets")
        if source.embedded_file:
            print(f"      File: {source.embedded_file}")
    
    print("\n🔧 WHAT WAS FIXED:")
    print("   • TWBXParser now deduplicates datasources during parsing")
    print("   • Only datasources with actual connections are kept")
    print("   • DataSourceDetector provides more robust filtering")
    print("   • App.py now uses detected_sources count instead of raw count")
    print("   • Result: Shows 1 data source instead of 44+")

if __name__ == "__main__":
    test_datasource_count_fix()