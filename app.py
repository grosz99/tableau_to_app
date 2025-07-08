"""
Intelligent Tableau Dashboard Converter - Main Streamlit Application
"""
import streamlit as st
import pandas as pd
import zipfile
import io
import os
import json
import logging
from pathlib import Path
from datetime import datetime
import traceback

# Import our modules
from src.parsers.twbx_parser import TWBXParser, WorkbookStructure
from src.parsers.data_source_detector import DataSourceDetector
from src.translators.formula_translator import TableauFormulaTranslator
from src.validation.snowflake_validator import SnowflakeValidator, SuperstoreMetrics
from src.agents.extraction_agent import ExtractionAgent
from src.generators.streamlit_generator import StreamlitGenerator
from src.utils.field_mapper import FieldMapper, FieldMapping

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Tableau Dashboard Converter",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        height: 3rem;
        font-weight: 600;
    }
    .upload-box {
        border: 2px dashed #ccc;
        border-radius: 1rem;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #155724;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Header
    st.title("🎯 Intelligent Tableau Dashboard Converter")
    st.markdown("Convert Tableau workbooks to Streamlit apps with AI-powered formula extraction and data validation")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        output_framework = st.selectbox(
            "Output Framework",
            ["Streamlit (Current)", "React (Future)", "Tableau (Future)"],
            help="Currently testing Streamlit generation. React and Tableau coming soon!"
        )
        
        chart_library = st.selectbox(
            "Visualization Library",
            ["Plotly", "Altair", "Matplotlib"],
            help="Select chart library for visualizations"
        )
        
        validate_data = st.checkbox(
            "Validate with Snowflake",
            value=False,
            help="Optional: Compare calculations against source data"
        )
        
        st.divider()
        
        st.header("📊 About")
        st.info(
            "**Current Prototype (v1.0)**\n\n"
            "✅ **Streamlit Generation**: Extract formulas → Generate Streamlit apps\n"
            "✅ **Field Mapping**: User-guided field name mapping for Python compatibility\n"
            "✅ **Data Validation**: Optional comparison against Snowflake source data\n"
            "✅ **AI Translation**: Tableau formulas → Python/Pandas\n\n"
            "🚧 **Coming Soon**: React and Tableau output options"
        )
    
    # Main content
    if validate_data:
        tabs = st.tabs(["📁 Upload Files", "🔍 Analysis", "🔧 Field Mapping", "🚀 Generate", "✅ Validation"])
    else:
        tabs = st.tabs(["📁 Upload Files", "🔍 Analysis", "🔧 Field Mapping", "🚀 Generate"])
    
    # Tab 1: Upload Files
    with tabs[0]:
        st.header("Step 1: Upload Your Files")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📊 Tableau Workbook")
            twbx_file = st.file_uploader(
                "Upload .twbx file",
                type=['twbx', 'twb'],
                key="twbx_upload",
                help="Your Tableau packaged workbook"
            )
            
            if twbx_file:
                st.success(f"✓ Uploaded: {twbx_file.name}")
                file_size = len(twbx_file.getvalue()) / 1024 / 1024
                st.caption(f"Size: {file_size:.2f} MB")
        
        with col2:
            st.subheader("📂 Data Source (Optional)")
            data_file = st.file_uploader(
                "Upload data file",
                type=['csv', 'xlsx', 'json'],
                key="data_upload",
                help="Optional: Replace embedded data"
            )
            
            if data_file:
                st.success(f"✓ Uploaded: {data_file.name}")
        
        with col3:
            st.subheader("🖼️ Reference Image")
            reference_image = st.file_uploader(
                "Upload dashboard screenshot",
                type=['png', 'jpg', 'jpeg'],
                key="image_upload",
                help="For visual validation"
            )
            
            if reference_image:
                st.success(f"✓ Uploaded: {reference_image.name}")
                st.image(reference_image, width=200)
        
        # Process button
        if twbx_file:
            if st.button("🔍 Analyze Workbook", type="primary", use_container_width=True):
                process_workbook(twbx_file, data_file, reference_image, validate_data)
    
    # Tab 2: Analysis Results
    with tabs[1]:
        st.header("Step 2: Workbook Analysis")
        
        if 'workbook_structure' in st.session_state:
            display_analysis_results(st.session_state.workbook_structure)
        else:
            st.info("👆 Upload a Tableau workbook to begin analysis")
    
    # Tab 3: Field Mapping
    with tabs[2]:
        st.header("Step 3: Field Mapping")
        
        if 'workbook_structure' in st.session_state:
            display_field_mapping()
        else:
            st.info("👆 Upload and analyze a Tableau workbook to begin field mapping")
    
    # Tab 4: Generate Application
    with tabs[3]:
        st.header("Step 4: Generate Application")
        
        if not validate_data:
            st.info("💡 Validation is currently disabled. The app will be generated with all extracted calculations without verification.")
        
        if 'workbook_structure' in st.session_state:
            if output_framework == "Streamlit (Current)":
                if st.button("🚀 Generate Streamlit App", type="primary", use_container_width=True):
                    generate_application(
                        st.session_state.workbook_structure,
                        "Streamlit",
                        chart_library
                    )
            else:
                st.info(f"🚧 {output_framework} generation coming in future release!")
                st.write("**Current prototype focuses on:**")
                st.write("• Formula extraction and translation")
                st.write("• Data validation against Snowflake")
                st.write("• Streamlit app generation")
                
                if st.button("🚀 Generate Streamlit App (Demo)", type="secondary", use_container_width=True):
                    generate_application(
                        st.session_state.workbook_structure,
                        "Streamlit",
                        chart_library
                    )
        else:
            st.info("👆 Complete workbook analysis first")
            
        # Show generated app if available
        if 'generated_app' in st.session_state:
            st.subheader("📦 Generated Application")
            st.success("✅ Application generated successfully!")
            
            # Download button
            zip_data = st.session_state.generated_app
            st.download_button(
                label="📥 Download Complete Application Package",
                data=zip_data,
                file_name="streamlit_dashboard.zip",
                mime="application/zip"
            )
    
    # Tab 5: Validation Results (only if validation is enabled)
    if validate_data and len(tabs) > 4:
        with tabs[4]:
            st.header("Step 5: Data Validation")
            
            if 'validation_results' in st.session_state:
                display_validation_results(st.session_state.validation_results)
            else:
                st.info("👆 Validation will be performed after generating the application")


def process_workbook(twbx_file, data_file, reference_image, validate_data):
    """Process uploaded Tableau workbook"""
    try:
        with st.spinner("🔍 Parsing Tableau workbook..."):
            # Initialize parser
            parser = TWBXParser()
            
            # Save uploaded file temporarily
            temp_path = Path("temp") / twbx_file.name
            temp_path.parent.mkdir(exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(twbx_file.getvalue())
            
            # Parse workbook
            workbook_structure = parser.parse(str(temp_path))
            
            # Detect actual data sources (not just raw XML entries)
            detector = DataSourceDetector()
            detected_sources = detector.detect_data_sources(workbook_structure)
            
            # Store in session state
            st.session_state.workbook_structure = workbook_structure
            st.session_state.detected_data_sources = detected_sources
            
            # Initialize field mapper
            field_mapper = FieldMapper()
            field_mappings = field_mapper.extract_fields_from_workbook(workbook_structure)
            st.session_state.field_mapper = field_mapper
            st.session_state.field_mappings = field_mappings
            
            # Clean up
            temp_path.unlink()
        
        st.success("✅ Workbook parsed successfully!")
        
        # Extract and translate formulas
        with st.spinner("🧮 Extracting and translating formulas..."):
            translator = TableauFormulaTranslator()
            translated_formulas = {}
            
            for calc_name, calculation in workbook_structure.calculations.items():
                try:
                    translation = translator.translate(calculation.formula)
                    translated_formulas[calc_name] = translation
                    logger.info(f"Translated {calc_name}: {calculation.formula} -> {translation.pandas_expression}")
                except Exception as e:
                    logger.error(f"Failed to translate {calc_name}: {e}")
                    translated_formulas[calc_name] = None
            
            st.session_state.translated_formulas = translated_formulas
        
        # Validate against Snowflake if enabled
        if validate_data:
            validate_calculations(workbook_structure, translated_formulas)
        
        # Show summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Dashboards", len(workbook_structure.dashboards))
        with col2:
            st.metric("Worksheets", len(workbook_structure.worksheets))
        with col3:
            st.metric("Calculations", len(workbook_structure.calculations))
        with col4:
            # Use detected data sources count instead of raw datasources count
            detected_count = len(st.session_state.get('detected_data_sources', []))
            st.metric("Data Sources", detected_count)
        
    except Exception as e:
        st.error(f"❌ Error processing workbook: {str(e)}")
        st.code(traceback.format_exc())


def display_analysis_results(workbook: WorkbookStructure):
    """Display detailed analysis results"""
    
    # Calculations section
    st.subheader("📊 Extracted Calculations")
    
    if workbook.calculations:
        calc_df = []
        for name, calc in workbook.calculations.items():
            calc_df.append({
                'Name': name,
                'Formula': calc.formula,
                'Type': calc.calculation_type,
                'Data Type': calc.data_type,
                'Is LOD': '✓' if calc.is_lod else '',
                'Dependencies': ', '.join(calc.dependencies)
            })
        
        df = pd.DataFrame(calc_df)
        st.dataframe(df, use_container_width=True, height=300)
        
        # Show translated formulas if available
        if 'translated_formulas' in st.session_state:
            st.subheader("🔄 Formula Translations")
            
            for calc_name, translation in st.session_state.translated_formulas.items():
                if translation:
                    with st.expander(f"📐 {calc_name}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Original Tableau Formula:**")
                            st.code(workbook.calculations[calc_name].formula, language="sql")
                        
                        with col2:
                            st.markdown("**Translated Python/Pandas:**")
                            st.code(translation.pandas_expression, language="python")
                        
                        if translation.is_window_function:
                            st.info("ℹ️ This is a window function")
                        
                        if translation.requires_aggregation:
                            st.warning("⚠️ Requires aggregation")
    
    # Worksheets section
    st.subheader("📈 Worksheets")
    
    for ws_name, worksheet in workbook.worksheets.items():
        with st.expander(f"📊 {worksheet.title}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Calculations Used:**")
                for calc in worksheet.calculations:
                    st.write(f"• {calc.name}")
            
            with col2:
                st.markdown("**Visualizations:**")
                for mark in worksheet.marks:
                    st.write(f"• {mark.get('class', 'Unknown')} chart")
    
    # Data Sources section
    st.subheader("🗃️ Data Sources")
    
    if 'detected_data_sources' in st.session_state:
        detected_sources = st.session_state.detected_data_sources
        
        if detected_sources:
            for i, source in enumerate(detected_sources, 1):
                with st.expander(f"📊 {source.caption} ({'Primary' if source.is_primary else 'Secondary'})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Connection Details:**")
                        st.write(f"• **Type**: {source.connection_type}")
                        st.write(f"• **Name**: {source.name}")
                        if source.embedded_file:
                            st.write(f"• **File**: {source.embedded_file}")
                        
                        # Show connection details
                        for key, value in source.connection_details.items():
                            if value and key not in ['class']:
                                st.write(f"• **{key.title()}**: {value}")
                    
                    with col2:
                        st.markdown("**Usage:**")
                        st.write(f"• **Worksheets**: {len(source.worksheets_using)}")
                        st.write(f"• **Primary Source**: {'Yes' if source.is_primary else 'No'}")
                        
                        if source.worksheets_using:
                            st.markdown("**Used in:**")
                            for worksheet in source.worksheets_using[:5]:  # Show first 5
                                st.write(f"  - {worksheet}")
                            if len(source.worksheets_using) > 5:
                                st.write(f"  ... and {len(source.worksheets_using) - 5} more")
        else:
            st.info("No data sources detected in this workbook.")
    else:
        st.info("Data source detection not yet performed. Upload and analyze a workbook first.")

    # Dashboards section
    st.subheader("📱 Dashboards")
    
    for dash_name, dashboard in workbook.dashboards.items():
        with st.expander(f"🎯 {dashboard.title}"):
            st.write(f"Size: {dashboard.size['width']} x {dashboard.size['height']}")
            st.write(f"Worksheets: {', '.join(dashboard.worksheets)}")


def display_field_mapping():
    """Display field mapping interface"""
    st.markdown("**Configure how Tableau field names map to Python variables**")
    st.markdown("Fields with invalid Python names will break the generated code. Fix these before proceeding.")
    
    if 'field_mapper' not in st.session_state or 'field_mappings' not in st.session_state:
        st.error("Field mapping not initialized. Please re-analyze the workbook.")
        return
    
    field_mapper = st.session_state.field_mapper
    field_mappings = st.session_state.field_mappings
    
    # Get summary statistics
    stats = field_mapper.get_summary_stats()
    
    # Display summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Fields", stats['total_fields'])
    with col2:
        st.metric("Valid Mappings", stats['valid_mappings'])
    with col3:
        st.metric("Invalid Mappings", stats['invalid_mappings'])
    with col4:
        st.metric("Validation Rate", f"{stats['validation_rate']:.1f}%")
    
    # Show field type breakdown
    if stats['field_types']:
        st.subheader("📊 Field Types")
        type_cols = st.columns(len(stats['field_types']))
        for i, (field_type, count) in enumerate(stats['field_types'].items()):
            with type_cols[i]:
                st.metric(field_type.title(), count)
    
    # Filter options
    st.subheader("🔍 Filter Fields")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_type = st.selectbox(
            "Show Field Type",
            ["All"] + list(stats['field_types'].keys()),
            key="field_type_filter"
        )
    
    with col2:
        show_status = st.selectbox(
            "Show Status",
            ["All", "Valid Only", "Invalid Only"],
            key="field_status_filter"
        )
    
    with col3:
        search_term = st.text_input(
            "Search Fields",
            placeholder="Search by field name...",
            key="field_search"
        )
    
    # Filter mappings
    filtered_mappings = field_mappings
    
    if show_type != "All":
        filtered_mappings = [m for m in filtered_mappings if m.field_type == show_type]
    
    if show_status == "Valid Only":
        filtered_mappings = [m for m in filtered_mappings if m.is_valid]
    elif show_status == "Invalid Only":
        filtered_mappings = [m for m in filtered_mappings if not m.is_valid]
    
    if search_term:
        filtered_mappings = [m for m in filtered_mappings 
                           if search_term.lower() in m.tableau_field.lower() or 
                              search_term.lower() in m.display_name.lower()]
    
    # Display mappings table
    st.subheader("🔧 Field Mappings")
    
    if not filtered_mappings:
        st.info("No fields match the current filters.")
        return
    
    # Create editable table
    for i, mapping in enumerate(filtered_mappings):
        status_icon = "❌" if not mapping.is_valid else "✅"
        with st.expander(f"{status_icon} {mapping.display_name}", expanded=not mapping.is_valid):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Tableau Field:**")
                st.code(mapping.tableau_field, language="text")
                
                st.markdown("**Display Name:**")
                st.write(mapping.display_name)
                
                st.markdown("**Field Type:**")
                st.write(f"{mapping.field_type} ({mapping.data_type})")
                
                if not mapping.is_valid:
                    st.error(f"**Error:** {mapping.validation_error}")
            
            with col2:
                st.markdown("**Python Variable Name:**")
                new_python_name = st.text_input(
                    "Python Name",
                    value=mapping.python_name,
                    key=f"python_name_{i}",
                    help="Must be a valid Python identifier"
                )
                
                st.markdown("**Display Label:**")
                new_display_label = st.text_input(
                    "Display Label",
                    value=mapping.display_label,
                    key=f"display_label_{i}",
                    help="Human-readable label for the UI"
                )
                
                # Update button
                if st.button(f"Update Mapping", key=f"update_{i}"):
                    success = field_mapper.update_mapping(
                        mapping.tableau_field,
                        new_python_name,
                        new_display_label
                    )
                    
                    if success:
                        st.success("Mapping updated successfully!")
                        # Update session state
                        st.session_state.field_mappings = field_mapper.get_all_mappings()
                        st.rerun()
                    else:
                        current_mapping = field_mapper.get_mapping(mapping.tableau_field)
                        if current_mapping and not current_mapping.is_valid:
                            st.error(f"Update failed: {current_mapping.validation_error}")
                        else:
                            st.error("Update failed: Invalid Python name or name conflict")
    
    # Bulk operations
    st.subheader("📦 Bulk Operations")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Regenerate All Names"):
            # Regenerate all Python names
            for mapping in field_mapper.get_all_mappings():
                new_python_name = field_mapper._generate_python_name(mapping.tableau_field)
                field_mapper.update_mapping(mapping.tableau_field, new_python_name, mapping.display_label)
            
            st.session_state.field_mappings = field_mapper.get_all_mappings()
            st.success("All Python names regenerated!")
            st.rerun()
    
    with col2:
        # Export mappings
        if st.button("📥 Export Mappings"):
            mappings_json = field_mapper.export_mappings()
            st.download_button(
                label="Download Mappings JSON",
                data=mappings_json,
                file_name=f"field_mappings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        # Import mappings
        uploaded_mappings = st.file_uploader(
            "📤 Import Mappings",
            type=['json'],
            key="import_mappings"
        )
        
        if uploaded_mappings:
            try:
                mappings_data = uploaded_mappings.read().decode('utf-8')
                if field_mapper.import_mappings(mappings_data):
                    st.session_state.field_mappings = field_mapper.get_all_mappings()
                    st.success("Mappings imported successfully!")
                    st.rerun()
                else:
                    st.error("Failed to import mappings. Please check the file format.")
            except Exception as e:
                st.error(f"Error importing mappings: {e}")
    
    # Validation summary
    if stats['invalid_mappings'] > 0:
        st.warning(f"⚠️ {stats['invalid_mappings']} fields have invalid Python names. These must be fixed before generating the application.")
    else:
        st.success("✅ All field mappings are valid! You can proceed to generate the application.")


def validate_calculations(workbook: WorkbookStructure, translated_formulas: dict):
    """Validate calculations against Snowflake"""
    try:
        with st.spinner("🔍 Validating calculations against Snowflake..."):
            validator = SnowflakeValidator()
            
            # Validate predefined metrics
            results = validator.validate_tableau_metrics(SuperstoreMetrics.METRICS)
            
            st.session_state.validation_results = results
            
            # Show quick summary
            valid_count = sum(1 for r in results if r.is_valid)
            total_count = len(results)
            
            if valid_count == total_count:
                st.success(f"✅ All {total_count} metrics validated successfully!")
            else:
                st.warning(f"⚠️ {valid_count}/{total_count} metrics passed validation")
            
            validator.close()
            
    except Exception as e:
        st.error(f"❌ Validation error: {str(e)}")
        logger.error(f"Validation failed: {traceback.format_exc()}")


def display_validation_results(results: list):
    """Display detailed validation results"""
    
    st.subheader("📊 Metric Validation Results")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    valid_count = sum(1 for r in results if r.is_valid)
    total_count = len(results)
    
    with col1:
        st.metric("Total Metrics", total_count)
    with col2:
        st.metric("Passed", valid_count, delta=f"{valid_count/total_count*100:.1f}%")
    with col3:
        st.metric("Failed", total_count - valid_count)
    
    # Detailed results
    st.subheader("📋 Detailed Results")
    
    for result in results:
        if result.is_valid:
            with st.expander(f"✅ {result.metric_name}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Expected:** {result.expected_value}")
                with col2:
                    st.write(f"**Actual:** {result.actual_value}")
                
                if result.difference is not None:
                    st.write(f"**Difference:** {result.difference:.6f}")
        else:
            with st.expander(f"❌ {result.metric_name}", expanded=True):
                st.error(f"**Error:** {result.error_message}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Expected:** {result.expected_value}")
                with col2:
                    st.write(f"**Actual:** {result.actual_value}")


def generate_application(workbook: WorkbookStructure, framework: str, chart_library: str):
    """Generate the output application"""
    try:
        with st.spinner(f"🚀 Generating {framework} application..."):
            # Initialize the generator
            generator = StreamlitGenerator()
            
            # Get translated formulas from session state
            translated_formulas = st.session_state.get('translated_formulas', None)
            
            # Get field mappings from session state
            field_mapper = st.session_state.get('field_mapper', None)
            
            # Validate field mappings before generation
            if field_mapper:
                invalid_mappings = field_mapper.get_invalid_mappings()
                if invalid_mappings:
                    st.error(f"❌ Cannot generate application with {len(invalid_mappings)} invalid field mappings. Please fix them in the Field Mapping tab first.")
                    return
            
            # Generate the complete application
            generated_app = generator.generate_app(
                workbook_structure=workbook,
                chart_library=chart_library.lower(),
                theme="default",
                translated_formulas=translated_formulas,
                field_mapper=field_mapper
            )
            
            # Create deployment package
            zip_data = generator.create_deployment_package(generated_app)
            
            # Store in session state
            st.session_state.generated_app = zip_data
            
            st.success("✅ Application generated successfully!")
            
            # Show preview of main file
            st.subheader("📝 Generated Code Preview (app.py)")
            st.code(generated_app.main_file[:2000] + "\n...\n# [Truncated for preview]", language="python")
            
            # Show generated files
            st.subheader("📂 Generated Files")
            files_list = ["app.py"] + list(generated_app.supporting_files.keys()) + ["requirements.txt", "README.md"]
            st.write("The following files have been generated:")
            for file in files_list:
                st.write(f"- {file}")
            
    except Exception as e:
        st.error(f"❌ Generation error: {str(e)}")
        st.code(traceback.format_exc())


def generate_sample_streamlit_code(workbook: WorkbookStructure, chart_library: str) -> str:
    """Generate sample Streamlit code"""
    # This is a simplified version - full implementation would use templates
    code = f'''"""
Generated Streamlit Dashboard
Created from: {list(workbook.dashboards.values())[0].title if workbook.dashboards else "Tableau Workbook"}
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import streamlit as st
import pandas as pd
import {chart_library.lower()} as viz

# Page config
st.set_page_config(
    page_title="Generated Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load data (replace with your data source)
@st.cache_data
def load_data():
    # TODO: Connect to your data source
    return pd.DataFrame()

def main():
    st.title("📊 Generated Dashboard")
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Main content
'''

    # Add worksheets
    for ws_name, worksheet in workbook.worksheets.items():
        code += f'''
    # Worksheet: {worksheet.title}
    st.subheader("{worksheet.title}")
    
    # TODO: Implement visualization
    
'''
    
    code += '''
if __name__ == "__main__":
    main()
'''
    
    return code


if __name__ == "__main__":
    main()