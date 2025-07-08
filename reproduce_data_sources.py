#!/usr/bin/env python3
"""
Data Source Reproduction Analysis - Shows how to properly detect and use data sources
"""
import sys
sys.path.append('.')

from src.parsers.twbx_parser import TWBXParser
from src.parsers.data_source_detector import DataSourceDetector

def analyze_data_sources(twbx_file):
    """Comprehensive data source analysis"""
    
    print("🔍 Data Source Detection & Reproduction Analysis")
    print("="*60)
    
    # Parse workbook
    parser = TWBXParser()
    workbook = parser.parse(twbx_file)
    
    # Detect data sources
    detector = DataSourceDetector()
    sources = detector.detect_data_sources(workbook)
    
    print(f"📊 Dashboard: {twbx_file}")
    print(f"📈 Worksheets: {len(workbook.worksheets)}")
    print(f"🗃️ Data Sources Found: {len(sources)}")
    print()
    
    # Show current issue
    print("❌ CURRENT ISSUE:")
    print("   • System assumes Snowflake connection")
    print("   • Ignores embedded Hyper files")
    print("   • Doesn't detect actual data sources")
    print()
    
    # Show what we actually found
    print("✅ ACTUAL DATA SOURCES:")
    for i, source in enumerate(sources, 1):
        print(f"   {i}. {source.caption}")
        print(f"      Type: {source.connection_type}")
        print(f"      Primary: {'Yes' if source.is_primary else 'No'}")
        print(f"      File: {source.embedded_file or 'N/A'}")
        print(f"      Worksheets: {len(source.worksheets_using)}")
        print()
    
    # Show recommended approach
    recommended = detector.get_recommended_connection()
    if recommended:
        print("🎯 RECOMMENDED APPROACH:")
        print(f"   • Use: {recommended.caption} ({recommended.connection_type})")
        print(f"   • Source: {recommended.embedded_file}")
        print(f"   • Feeds: {len(recommended.worksheets_using)} worksheets")
        print()
        
        # Show connection code
        print("🔧 GENERATED CONNECTION CODE:")
        connection_code = detector.generate_data_connection_code(recommended)
        print(connection_code)
        print()
    
    # Show how to fix the system
    print("🔄 HOW TO FIX THE SYSTEM:")
    print("   1. Detect actual data sources (not assume Snowflake)")
    print("   2. Generate appropriate connection code")
    print("   3. Extract embedded data when available")
    print("   4. Map worksheets to their actual data sources")
    print("   5. Validate against the correct source")
    print()
    
    # Create data source report
    report = detector.create_data_source_report()
    print("📋 DETAILED REPORT:")
    print(report)

def show_connection_strategies():
    """Show different connection strategies"""
    
    print("🔧 CONNECTION STRATEGIES BY SOURCE TYPE:")
    print("="*50)
    
    strategies = {
        "Hyper Extract": {
            "description": "Tableau's embedded data format",
            "approach": "Extract and convert to DataFrame",
            "libraries": ["tableauhyperapi", "pandas"],
            "pros": ["Complete data", "No external dependencies"],
            "cons": ["Requires Hyper API", "Static snapshot"]
        },
        "Snowflake": {
            "description": "Live database connection",
            "approach": "Connect with credentials",
            "libraries": ["snowflake-connector-python", "pandas"],
            "pros": ["Live data", "Scalable"],
            "cons": ["Requires credentials", "Network dependency"]
        },
        "Excel Files": {
            "description": "Excel workbooks",
            "approach": "Read with pandas",
            "libraries": ["pandas", "openpyxl"],
            "pros": ["Simple", "Portable"],
            "cons": ["Limited size", "Static data"]
        },
        "CSV Files": {
            "description": "Comma-separated values",
            "approach": "Direct pandas import",
            "libraries": ["pandas"],
            "pros": ["Universal", "Simple"],
            "cons": ["No schemas", "Static data"]
        }
    }
    
    for source_type, info in strategies.items():
        print(f"📊 {source_type}:")
        print(f"   Description: {info['description']}")
        print(f"   Approach: {info['approach']}")
        print(f"   Libraries: {', '.join(info['libraries'])}")
        print(f"   Pros: {', '.join(info['pros'])}")
        print(f"   Cons: {', '.join(info['cons'])}")
        print()

def main():
    """Main analysis"""
    
    # Analyze SuperStore dashboard
    analyze_data_sources('SuperStore Business Dashboard 2025 _ VOTD _ VizOfTheDay.twbx')
    
    # Show connection strategies
    show_connection_strategies()
    
    print("🎯 SOLUTION SUMMARY:")
    print("="*50)
    print("✅ The system CAN detect actual data sources")
    print("✅ We have code to generate appropriate connections")
    print("✅ Works with Hyper, Snowflake, Excel, CSV")
    print("✅ Maps worksheets to their data sources")
    print()
    print("❌ CURRENT LIMITATION:")
    print("   • Validation hardcoded to Snowflake")
    print("   • Should use detected sources instead")
    print()
    print("🚀 NEXT STEPS:")
    print("   1. Integrate data source detection into main app")
    print("   2. Generate connection code based on detected sources")
    print("   3. Update validation to use actual data sources")
    print("   4. Test with different dashboard types")

if __name__ == "__main__":
    main()