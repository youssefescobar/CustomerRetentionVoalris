import streamlit as st
import pandas as pd
from datetime import datetime
import io

from styles import set_page, inject_css
from processing.customers import process_customer_data
from processing.companies import process_company_data
from ui.metrics import display_summary_metrics
from ui.visualizations import create_visualizations
from ui.customer_detail import display_individual_customer

def main():
    set_page()
    inject_css()
    # Enhanced Header with animation
    st.markdown("""
    <div class="main-header">
        <h1>🌟 Customer Analytics Dashboard 🌟</h1>
        <p>Transform your raw customer data into colorful, actionable insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Sidebar
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h2>📁 Data Upload Center</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.sidebar.file_uploader(
        "🚀 Upload your CSV file",
        type=['csv'],
        help="Upload a CSV file with customer quotation data"
    )
    
    # Sample data info with enhanced styling
    with st.sidebar.expander("📋 Required CSV Format", expanded=False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 1rem; border-radius: 8px;">
        <strong>Your CSV should contain:</strong><br>
        📅 <strong>Date:</strong> Quote date (DD/MM/YYYY)<br>
        🆔 <strong>ClientID:</strong> Unique client identifier<br>
        📄 <strong>Number:</strong> Quote number<br>
        ✅ <strong>Estimate status:</strong> Quote status<br>
        💰 <strong>Taxable amount:</strong> Quote value<br>
        🔄 <strong>converted to invoice:</strong> Converted amount<br>
        📝 <strong>Name:</strong> Project name<br>
        🛠️ Service columns: CME, Design, Med Com, etc.
        </div>
        """, unsafe_allow_html=True)
    
    if uploaded_file is not None:
        try:
            # Load the data
            with st.spinner("🔄 Loading and processing data..."):
                df_raw = pd.read_csv(uploaded_file)
                
            st.markdown(f"""
            <div class="success-highlight">
                ✅ File uploaded successfully! Found {len(df_raw)} records
            </div>
            """, unsafe_allow_html=True)
            
            # Show raw data preview
            with st.expander("👀 Preview Raw Data"):
                st.dataframe(df_raw.head(10), width='stretch')
                st.write(f"**Shape:** {df_raw.shape[0]} rows × {df_raw.shape[1]} columns")
            
            # Process the data
            with st.spinner("🎨 Processing customer analytics..."):
                processed_data, error = process_customer_data(df_raw)
            
            if error:
                st.markdown(f"""
                <div class="warning-highlight">
                    ❌ Error processing data: {error}
                </div>
                """, unsafe_allow_html=True)
                return
            
            if processed_data is None:
                st.markdown("""
                <div class="warning-highlight">
                    ❌ Failed to process data. Please check your CSV format.
                </div>
                """, unsafe_allow_html=True)
                return
            
            st.markdown(f"""
            <div class="success-highlight">
                🎉 Data processed successfully! Generated analytics for {len(processed_data)} customers
            </div>
            """, unsafe_allow_html=True)
            
            # Show processed data preview
            with st.expander("👀 Preview Processed Data"):
                st.dataframe(processed_data.head(10), width='stretch')
                st.write(f"**Shape:** {processed_data.shape[0]} rows × {processed_data.shape[1]} columns")
            
            # Quick Search Options (placed BEFORE KPIs)
            st.header("🔎 Find a Customer")
            st.markdown("""
            <div class="stats-container">
                <p>Choose how you'd like to look up a customer: by company or directly by client name.</p>
            </div>
            """, unsafe_allow_html=True)

            # Prepare lightweight company data for quick search
            with st.spinner("⚙️ Preparing quick search options..."):
                top_company_data = process_company_data(df_raw)

            search_mode = st.radio(
                "Lookup mode:",
                options=["Search by Company", "Search by Client"],
                horizontal=True,
            )

            selected_customer_quick = None
            if search_mode == "Search by Client":
                # Always show all clients (as requested), but don't select by default
                candidates = sorted(processed_data['ClientID'].dropna().unique().tolist())
                select_options = ["-- Select Customer --"] + candidates
                sel_val = st.selectbox("Select customer:", options=select_options, index=0, key="quick_client_select")
                selected_customer_quick = None if sel_val == "-- Select Customer --" else sel_val

            else:  # Search by Company: Country -> Company -> Customer
                if top_company_data is not None and not top_company_data.empty:
                    available_countries = sorted(top_company_data['Country'].dropna().unique().tolist())
                    sel_country = st.selectbox(
                        "Choose a Country:", options=["-- Select Country --"] + available_countries, key="quick_country_select"
                    )
                    if sel_country and sel_country != "-- Select Country --":
                        sub_country = top_company_data[top_company_data['Country'] == sel_country]
                        available_companies = sorted(sub_country['Company'].dropna().unique().tolist())
                        sel_company = st.selectbox(
                            "Choose a Company:", options=["-- Select Company --"] + available_companies, key="quick_company_select"
                        )
                        if sel_company and sel_company != "-- Select Company --":
                            # Get the row for this country+company
                            row = sub_country[sub_country['Company'] == sel_company]
                            all_clients = []
                            for lst in row['ClientIDs'].values:
                                all_clients.extend(lst)
                            all_clients = sorted(set(all_clients))
                            if all_clients:
                                company_select_options = ["-- Select Customer --"] + all_clients
                                sel_cust = st.selectbox(
                                    "Choose a Customer:", options=company_select_options, index=0, key="quick_company_client_select"
                                )
                                selected_customer_quick = None if sel_cust == "-- Select Customer --" else sel_cust
                            else:
                                st.warning("No customers found for the selected company.")
                else:
                    st.warning("Company data is not available for quick search.")

            # If a customer is selected via quick lookup, show their analytics immediately
            if selected_customer_quick:
                st.markdown("---")
                st.subheader(f"📊 Quick View: {selected_customer_quick}")
                if selected_customer_quick in processed_data['ClientID'].values:
                    cust_row = processed_data[processed_data['ClientID'] == selected_customer_quick].iloc[0]
                    display_individual_customer(cust_row, selected_customer_quick, df_raw)
                else:
                    st.warning("Selected customer not found in processed data.")
            
            # Exports available within Find a Customer
            st.markdown("---")
            st.markdown("### 📥 Export Your Analytics")
            
            export_col1, export_col2 = st.columns(2)
            with export_col1:
                # Download all analytics
                full_csv_buffer_fc = io.StringIO()
                processed_data.to_csv(full_csv_buffer_fc, index=False)
                full_csv_data_fc = full_csv_buffer_fc.getvalue()
                st.download_button(
                    label="📋 Download All Analytics (CSV)",
                    data=full_csv_data_fc,
                    file_name=f"complete_customer_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_all_from_find"
                )
            with export_col2:
                # Download selected customer's analytics when available
                if selected_customer_quick:
                    single_row = processed_data[processed_data['ClientID'] == selected_customer_quick]
                    single_csv_buffer = io.StringIO()
                    single_row.to_csv(single_csv_buffer, index=False)
                    single_csv_data = single_csv_buffer.getvalue()
                    st.download_button(
                        label=f"👤 Download {selected_customer_quick} (CSV)",
                        data=single_csv_data,
                        file_name=f"{selected_customer_quick}_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_single_from_find"
                    )
                else:
                    st.info("Select a customer above to enable single-customer export.")
            
            # Display summary metrics
            st.header("📈 Key Performance Indicators")
            display_summary_metrics(processed_data)
            
            # Display visualizations
            st.header("📊 Interactive Visual Analytics")
            create_visualizations(processed_data)
            
            # Interactive data exploration (moved into an expander to declutter main flow)
            with st.expander("🔍 Advanced Customer Data Explorer", expanded=False):
                # Enhanced Filters with colorful styling
                st.markdown("""
                <div class=\"stats-container\">
                    <h3>🎛️ Filter Controls</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    segment_filter = st.multiselect(
                        "🎯 Filter by Customer Segment",
                        options=processed_data['Customer_Segment'].unique(),
                        default=processed_data['Customer_Segment'].unique()
                    )
                
                with col2:
                    min_clv = st.number_input(
                        "💰 Minimum CLV",
                        min_value=0,
                        value=0,
                        step=1000
                    )
                
                with col3:
                    min_win_rate = st.slider(
                        "📈 Minimum Win Rate (%)",
                        min_value=0,
                        max_value=100,
                        value=0
                    )
                
                with col4:
                    min_retention = st.slider(
                        "🔄 Minimum Retention Rate",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.0,
                        step=0.1,
                        format="%.1f"
                    )
                
                # Apply filters
                filtered_data = processed_data[
                    (processed_data['Customer_Segment'].isin(segment_filter)) &
                    (processed_data['CLV'] >= min_clv) &
                    (processed_data['Win_Rate_%'] >= min_win_rate) &
                    (processed_data['Retention_Rate'] >= min_retention)
                ]
                
                # Enhanced filter results display
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class=\"success-highlight\">
                        📊 Showing {len(filtered_data)} customers
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class=\"stats-container\">
                        📉 Filtered from {len(processed_data)} total customers
                    </div>
                    """, unsafe_allow_html=True)
                
                # Customer search with enhanced styling
                st.markdown("""
                <div class=\"stats-container\">\n                    <h4>🔍 Customer Search</h4>\n                </div>
                """, unsafe_allow_html=True)
                
                search_term = st.text_input(
                    "Customer Search", 
                    placeholder="Enter customer name or ID to search...",
                    label_visibility="collapsed"
                )
                if search_term:
                    filtered_data = filtered_data[
                        filtered_data['ClientID'].str.contains(search_term, case=False, na=False)
                    ]
                    st.markdown(f"""
                    <div class=\"success-highlight\">
                        🎯 Search results: {len(filtered_data)} customers found
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display filtered data with enhanced controls
                if len(filtered_data) > 0:
                    # Sort options with colorful styling
                    st.markdown("""
                    <div class=\"stats-container\">\n                        <h4>📊 Data Display Controls</h4>\n                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        sort_by = st.selectbox(
                            "🔤 Sort by:",
                            options=['CLV', 'Win_Rate_%', 'Retention_Rate', 'Churn_Rate', 'Total_Quotations', 'Years_Active', 'Projects_Per_Year'],
                            index=0
                        )
                    
                    with col2:
                        sort_order = st.radio("📈 Sort order:", ['Descending', 'Ascending'])
                        ascending = sort_order == 'Ascending'
                    
                    # Sort and display with color-coded segments
                    display_data = filtered_data.sort_values(by=sort_by, ascending=ascending)
                    
                    # Color-code the dataframe based on customer segments
                    def highlight_segments(val, column_name):
                        if column_name == 'Customer_Segment':
                            if val == 'High':
                                return 'background-color: #4facfe; color: white; font-weight: bold'
                            elif val == 'Medium':
                                return 'background-color: #43e97b; color: white; font-weight: bold'
                            else:
                                return 'background-color: #fa709a; color: white; font-weight: bold'
                        elif column_name == 'Retention_Rate':
                            if val >= 0.7:
                                return 'background-color: #00ff88; color: white; font-weight: bold'
                            elif val >= 0.4:
                                return 'background-color: #ffaa00; color: white; font-weight: bold'
                            else:
                                return 'background-color: #ff4757; color: white; font-weight: bold'
                        elif column_name == 'CLV' and val >= 75000:
                            return 'background-color: #667eea; color: white; font-weight: bold'
                        elif column_name == 'Win_Rate_%' and val >= 70:
                            return 'background-color: #764ba2; color: white; font-weight: bold'
                        return ''
                    
                    # Apply styling to dataframe
                    styled_df = display_data.style.map(
                        lambda x: highlight_segments(x, 'Customer_Segment'), 
                        subset=['Customer_Segment']
                    ).map(
                        lambda x: highlight_segments(x, 'Retention_Rate'), 
                        subset=['Retention_Rate']
                    ).map(
                        lambda x: highlight_segments(x, 'CLV'), 
                        subset=['CLV']
                    ).map(
                        lambda x: highlight_segments(x, 'Win_Rate_%'), 
                        subset=['Win_Rate_%']
                    ).format({
                        'CLV': 'E£{:,.2f}',
                        'Total_Project_Value': 'E£{:,.2f}',
                        'Revenue_by_Service': 'E£{:,.2f}',
                        'Win_Rate_%': '{:.1f}%','Loss_Rate_%': '{:.1f}%',
                        'Retention_Rate': '{:.2f}',
                        'Churn_Rate': '{:.2f}',
                        'Years_Active': '{:.1f}',
                        'Projects_Per_Year': '{:.1f}'
                    })
                    
                    st.dataframe(
                        styled_df,
                        width='stretch',
                        height=400
                    )
                    
                    # Download processed data with enhanced buttons
                    st.header("📥 Export Your Analytics")
                    
                    csv_buffer = io.StringIO()
                    display_data.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        <div class=\"stats-container\">\n                            <h4>📊 Filtered Data Export</h4>\n                        </div>
                        """, unsafe_allow_html=True)
                        st.download_button(
                            label="📊 Download Filtered Data (CSV)",
                            data=csv_data,
                            file_name=f"customer_analytics_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        st.markdown("""
                        <div class=\"stats-container\">\n                            <h4>📋 Complete Analytics Export</h4>\n                        </div>
                        """, unsafe_allow_html=True)
                        # Download full processed data
                        full_csv_buffer = io.StringIO()
                        processed_data.to_csv(full_csv_buffer, index=False)
                        full_csv_data = full_csv_buffer.getvalue()
                        
                        st.download_button(
                            label="📋 Download All Analytics (CSV)",
                            data=full_csv_data,
                            file_name=f"complete_customer_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.markdown("""
                    <div class=\"warning-highlight\">\n                        ⚠️ No customers match the current filters. Try adjusting your criteria.\n                    </div>
                    """, unsafe_allow_html=True)
                
        except Exception as e:
            st.markdown(f"""
            <div class="warning-highlight">
                ❌ Error loading file: {str(e)}
            </div>
            """, unsafe_allow_html=True)
            st.write("Please ensure your CSV file is properly formatted and try again.")
    
    else:
        # Enhanced instructions when no file is uploaded
        st.markdown("""
        <div class="stats-container">
            <h2>🚀 Welcome to Your Analytics Journey!</h2>
            <p>👆 Please upload a CSV file to get started with your colorful customer analytics!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show sample data format with colorful styling
        st.header("📋 Sample Data Format")
        st.markdown("""
        <div class="stats-container">
            <h4>Here's what your CSV should look like:</h4>
        </div>
        """, unsafe_allow_html=True)
        
        sample_data = {
            'Date': ['9/1/2022', '1/2/2022', '11/4/2022'],
            'Number': ['KSA.Abb.QU.1002.1', 'KSA.Abb.QU.1002.2', 'KSA.Abb.QU.1058.1'],
            'Estimate status': ['Rejected', 'Rejected', 'Closed'],
            'Taxable amount': [103547.5, 40303.5, 161598.53],
            'ClientID': ['Ibrahim Elnahal Abbive', 'Ibrahim Elnahal Abbive', 'Ibrahim Elnahal Abbive'],
            'converted to invoice (AMOUNT)': [0, 0, 161598.53],
            'Name': ['Project A', 'Project B', 'Project C'],
            'CME': [0, 0, 1000],
            'Design': [0, 500, 0]
        }
        sample_df = pd.DataFrame(sample_data)
        
        # Style the sample dataframe (use set_table_styles to avoid typing issues)
        styled_sample = sample_df.style.set_table_styles([
            {'selector': 'td', 'props': [('background-color', '#f8f9fa'), ('border-color', '#667eea'), ('color', '#333')]},
            {'selector': 'th', 'props': [('background-color', '#f8f9fa'), ('color', '#333')]}
        ])

        st.dataframe(styled_sample, width='stretch')
        
        # Feature highlights
        st.markdown("""
        <div class="stats-container">
            <h3>🌟 What You'll Get:</h3>
            <ul style="font-size: 16px; line-height: 2;">
                <li>🎯 <strong>Customer Segmentation</strong> - High, Medium, Low value customers</li>
                <li>📈 <strong>Win Rate Analysis</strong> - Success rates with colorful highlights</li>
                <li>🔄 <strong>Retention & Churn Rates</strong> - Customer loyalty metrics</li>
                <li>💰 <strong>Customer Lifetime Value</strong> - Revenue impact analysis</li>
                <li>📊 <strong>Interactive Visualizations</strong> - Beautiful charts and graphs</li>
                <li>🔍 <strong>Advanced Filtering</strong> - Find exactly what you need</li>
                <li>👤 <strong>Individual Customer Deep Dive</strong> - Detailed customer profiles</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()