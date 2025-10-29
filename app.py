import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Set page config
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with vibrant colors
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px 0 rgba(31, 38, 135, 0.2);
        transform: translateY(0px);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px 0 rgba(31, 38, 135, 0.3);
    }
    
    .high-value {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        color: white !important;
        font-weight: bold;
        padding: 0.5rem;
        border-radius: 8px;
        text-align: center;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    .medium-value {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        color: white !important;
        font-weight: bold;
        padding: 0.5rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .low-value {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%) !important;
        color: white !important;
        font-weight: bold;
        padding: 0.5rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .retention-high {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        padding: 0.8rem;
        border-radius: 10px;
        border-left: 5px solid #00ff88;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);
    }
    
    .retention-medium {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%) !important;
        color: #333 !important;
        padding: 0.8rem;
        border-radius: 10px;
        border-left: 5px solid #ffaa00;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(255, 170, 0, 0.3);
    }
    
    .retention-low {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%) !important;
        color: #333 !important;
        padding: 0.8rem;
        border-radius: 10px;
        border-left: 5px solid #ff4757;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
    }
    
    .customer-highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px 0 rgba(102, 126, 234, 0.37);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .stats-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.2) 100%);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
        margin: 1rem 0;
    }
    
    @keyframes glow {
        from { box-shadow: 0 0 5px #4facfe, 0 0 10px #4facfe, 0 0 15px #4facfe; }
        to { box-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe, 0 0 30px #00f2fe; }
    }
    
    .stDataFrame {
        border: 2px solid transparent;
        border-radius: 12px;
        background: linear-gradient(white, white) padding-box, linear-gradient(135deg, #667eea, #764ba2) border-box;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .success-highlight {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .warning-highlight {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_segment_color_class(segment):
    """Return CSS class based on customer segment"""
    if segment == 'High':
        return 'high-value'
    elif segment == 'Medium':
        return 'medium-value'
    else:
        return 'low-value'

def get_retention_color_class(retention_rate):
    """Return CSS class based on retention rate"""
    if retention_rate >= 0.7:
        return 'retention-high'
    elif retention_rate >= 0.4:
        return 'retention-medium'
    else:
        return 'retention-low'

def process_company_data(df):
    """
    Process company-level data to generate company analytics
    """
    try:
        # Create a copy to avoid modifying original data
        data = df.copy()
        
        # Strip whitespace from column names
        data.columns = data.columns.str.strip()
        
        # Use Location column for country
        if 'Location' in data.columns:
            # Clean and standardize location data
            data['Country'] = data['Location'].astype(str).str.strip()
            
            # Map valid countries
            valid_countries = ['UAE', 'KSA', 'Gulf', 'Kuwait', 'Egypt', 'Oman', 'Lebanon', 'Levant', 'Out Side UAE', 'Jordan']
            
            # If location is not in valid list, mark as "Others"
            data['Country'] = data['Country'].apply(lambda x: x if x in valid_countries else 'Others')
        else:
            data['Country'] = 'Unknown'
        
        # Ensure Company and Client columns exist
        if 'Company' not in data.columns:
            data['Company'] = 'Unknown'
        if 'Client' not in data.columns:
            data['Client'] = 'Unknown'
        if 'ClientID' not in data.columns:
            data['ClientID'] = 'Unknown'
            
        # Convert numeric columns
        numeric_columns = ['Taxable amount', 'converted to invoice (AMOUNT)']
        existing_numeric_cols = [col for col in numeric_columns if col in data.columns]
        data[existing_numeric_cols] = data[existing_numeric_cols].apply(pd.to_numeric, errors='coerce')
        
        # Group by Company and Country
        company_data = data.groupby(['Company', 'Country']).agg({
            'Client': lambda x: sorted(x.dropna().unique().tolist()),
            'ClientID': lambda x: sorted(x.dropna().unique().tolist()),
            'Number': 'count',
            'Estimate status': lambda x: (x == 'Closed').sum(),
            'Taxable amount': 'sum',
            'converted to invoice (AMOUNT)': 'sum'
        }).reset_index()
        
        # Rename columns
        company_data.columns = ['Company', 'Country', 'Representatives', 'ClientIDs',
                                'Total_Quotes', 'Closed_Quotes', 'Total_Value', 
                                'Total_Revenue']
        
        # Calculate metrics
        company_data['Total_Clients'] = company_data['ClientIDs'].apply(len)
        company_data['Win_Rate_%'] = (company_data['Closed_Quotes'] / company_data['Total_Quotes'] * 100).fillna(0)
        
        # Sort by revenue
        company_data = company_data.sort_values('Total_Revenue', ascending=False)
        
        return company_data
        
    except Exception as e:
        st.error(f"Error processing company data: {str(e)}")
        return pd.DataFrame()

def process_customer_data(df):
    """
    Process raw customer data to generate analytics similar to the provided code
    """
    try:
        # Create a copy to avoid modifying original data
        data = df.copy()
        
        # Strip whitespace from column names
        data.columns = data.columns.str.strip()
        
        # Convert service columns to numeric
        service_columns = ['CME', 'Design', 'Med Com', 'Multichannel', 'Onsite Support', 
                          'Other Services', 'Video', 'Webinars', 'Websites']
        numeric_columns = service_columns + ['Taxable amount', 'converted to invoice (AMOUNT)']
        
        # Handle columns that might not exist
        existing_numeric_cols = [col for col in numeric_columns if col in data.columns]
        data[existing_numeric_cols] = data[existing_numeric_cols].apply(pd.to_numeric, errors='coerce')
        
        # Convert Date column to datetime
        try:
            data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y')
        except:
            try:
                # Let pandas infer the format automatically
                data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
            except:
                data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        
        # Extract project number for diversity calculation
        if 'Number' in data.columns:
            # Extract project number (e.g., from KSA.Abb.QU.1002.1 -> 1002)
            data['Project_Number'] = data['Number'].astype(str).str.split('.').str[3]
            
            # For counting quotes: Use only the LATEST version of each project per client
            # Extract version number, handling different formats (1, 2, 2-A, etc.)
            def extract_version(number_str):
                try:
                    parts = str(number_str).split('.')
                    if len(parts) >= 5:
                        version_str = parts[4]
                        # Try to convert to float, if it fails (like '2-A'), use string sorting
                        try:
                            return float(version_str)
                        except:
                            # For non-numeric versions, create a sortable value
                            # Extract numeric part if exists
                            import re
                            numeric = re.findall(r'\d+', version_str)
                            if numeric:
                                return float(numeric[0]) + 0.1  # Add 0.1 for letter versions
                            return 1.0
                    return 1.0
                except:
                    return 1.0
            
            data['Version_Number'] = data['Number'].apply(extract_version)
            
            # Create a unique identifier for each quote (project)
            data['Quote_ID'] = data['Number'].astype(str).str.rsplit('.', n=1).str[0]
        else:
            data['Project_Number'] = range(len(data))
            data['Quote_ID'] = range(len(data))
            data['Version_Number'] = 1.0
        
        # Get only the latest version of each quote per client
        # Sort by version number and keep last (highest version)
        data_latest = data.sort_values('Version_Number').groupby(['ClientID', 'Quote_ID']).tail(1).copy()
        
        # CRITICAL: Determine project status - if ANY version was Closed, project is Closed
        # Group by ClientID and Quote_ID to check if any version was closed
        def get_project_status(group):
            # If any version is Closed, the project is Closed
            if (group['Estimate status'] == 'Closed').any():
                return 'Closed'
            # Otherwise, it's Rejected
            return 'Rejected'
        
        if 'Estimate status' in data.columns:
            project_status = data.groupby(['ClientID', 'Quote_ID']).apply(
                get_project_status
            ).reset_index(name='Final_Project_Status')
            
            # Merge the final status back to data_latest
            data_latest = data_latest.merge(
                project_status[['ClientID', 'Quote_ID', 'Final_Project_Status']], 
                on=['ClientID', 'Quote_ID'], 
                how='left'
            )
            # Use Final_Project_Status for counting
            data_latest['Project_Status_For_Counting'] = data_latest['Final_Project_Status']
        else:
            data_latest['Project_Status_For_Counting'] = 'Unknown'
        
        # Create base aggregation - using LATEST VERSION data only
        # IMPORTANT: We count UNIQUE quote/project numbers (not versions)
        agg_dict = {
            'Date': ['min', 'max'],
            'Quote_ID': 'nunique',  # Count unique quotes (projects), not versions
            'Project_Status_For_Counting': [
                ('Closed', lambda x: (x == 'Closed').sum()),  # Count projects where ANY version was Closed
                ('Rejected', lambda x: (x == 'Rejected').sum())  # Count projects where ALL versions were Rejected
            ],
            'Taxable amount': 'sum' if 'Taxable amount' in data_latest.columns else lambda x: 0,
            'converted to invoice (AMOUNT)': 'sum' if 'converted to invoice (AMOUNT)' in data_latest.columns else lambda x: 0,
            'Name': 'nunique' if 'Name' in data_latest.columns else lambda x: 1,
            'Project_Number': 'nunique'
        }
        
        # Add service columns to aggregation if they exist
        for col in service_columns:
            if col in data_latest.columns:
                agg_dict[col] = 'sum'
        
        # Aggregate using LATEST VERSION data only
        client_data = data_latest.groupby('ClientID').agg(agg_dict).reset_index()
        
        # Flatten column names
        client_data.columns = ['_'.join(str(c) for c in col).strip() if isinstance(col, tuple) and col[1] else (col[0] if isinstance(col, tuple) else col) for col in client_data.columns.values]
        
        # Calculate derived metrics
        client_data['First_Quote_Date'] = client_data['Date_min']
        client_data['Last_Quote_Date'] = client_data['Date_max']
        
        # Calculate years active (actual time between first and last project)
        client_data['Years_Active'] = (client_data['Last_Quote_Date'] - client_data['First_Quote_Date']).dt.days / 365
        client_data['Years_Active'] = client_data['Years_Active'].replace(0, 0.003)  # If same day, set to ~1 day
        
        # Calculate idle time (time since last project until today)
        today = pd.Timestamp.now()
        client_data['Idle_Time_Days'] = (today - client_data['Last_Quote_Date']).dt.days
        client_data['Idle_Time_Years'] = client_data['Idle_Time_Days'] / 365
        
        # Calculate average days between quotes
        try:
            # Use latest version data only for date calculations
            avg_days = data_latest.groupby('ClientID')['Date'].apply(
                lambda x: x.sort_values().diff().mean().days if len(x) > 1 else 0
            ).reset_index(name='Average_Days_Between_Quotes')
            client_data = client_data.merge(avg_days, on='ClientID', how='left')
        except:
            client_data['Average_Days_Between_Quotes'] = 30
        
        # Calculate projects per year
        def calculate_projects_per_year(row):
            years = row['Years_Active']
            projects = row.get('Project_Number_nunique', 1)
            return projects if years < 1 else projects / years
        
        client_data['Projects_Per_Year'] = client_data.apply(calculate_projects_per_year, axis=1)
        
        # Final features
        client_data['Project_Diversity'] = client_data.get('Name_nunique', 1)
        client_data['Total_Project_Value'] = client_data.get('Taxable amount_sum', 0).fillna(0)
        client_data['CLV'] = client_data.get('converted to invoice (AMOUNT)_sum', 0).fillna(0)
        
        # CRITICAL FIX: Count UNIQUE quotes (projects), not versions
        # Use Quote_ID count which represents unique projects
        client_data['Total_Quotations'] = client_data.get('Quote_ID_nunique', 1)
        
        # Get converted and lost counts based on FINAL project status
        if 'Project_Status_For_Counting_Closed' in client_data.columns:
            client_data['Converted_Quotations'] = client_data['Project_Status_For_Counting_Closed']
        else:
            client_data['Converted_Quotations'] = 0
            
        if 'Project_Status_For_Counting_Rejected' in client_data.columns:
            client_data['Lost_Quotations'] = client_data['Project_Status_For_Counting_Rejected']
        else:
            client_data['Lost_Quotations'] = 0
        
        # Calculate rates
        client_data['Win_Rate_%'] = (client_data['Converted_Quotations'] / client_data['Total_Quotations']) * 100
        client_data['Loss_Rate_%'] = (client_data['Lost_Quotations'] / client_data['Total_Quotations']) * 100
        
        # Calculate service totals for each client
        existing_service_cols = [col for col in service_columns if col in data_latest.columns]
        if existing_service_cols:
            # Use latest version data for service analysis
            service_totals = data_latest.groupby('ClientID')[existing_service_cols].sum().fillna(0)
            
            # Find top service by volume and value
            client_data['Top_Service_by_Volume'] = service_totals.apply(
                lambda row: row.idxmax() if row.max() > 0 else 'No Service', axis=1
            ).values
            client_data['Top_Service_by_Value'] = service_totals.apply(
                lambda row: row.idxmax() if row.max() > 0 else 'No Service', axis=1
            ).values
            
            # Calculate revenue by service
            client_data['Revenue_by_Service'] = service_totals.sum(axis=1).values

            # --- New: Per-client service revenue breakdown (percentages) ---
            # Compute per-service percentage of service revenue for each client
            # If a client has zero service revenue, percentages will be empty {}
            svc_rev_sum = service_totals.sum(axis=1).replace({0: np.nan})
            service_revenue_pct = service_totals.div(svc_rev_sum, axis=0).fillna(0)

            # Convert to dict mapping ClientID -> {service: pct, ...}
            service_revenue_pct_dict = service_revenue_pct.apply(
                lambda row: {col: float(row[col]) for col in existing_service_cols if row[col] > 0},
                axis=1
            ).to_dict()

            # Map dicts into client_data
            client_data['Service_Revenue_Breakdown'] = client_data['ClientID'].map(service_revenue_pct_dict).fillna({})

            # --- New: Average service revenue per project (absolute E£) ---
            # Divide total service revenue by total unique projects per client
            avg_service_rev = service_totals.div(client_data.set_index('ClientID')['Total_Quotations'].replace(0, np.nan), axis=0).fillna(0)
            avg_service_rev_dict = avg_service_rev.apply(lambda row: {col: float(row[col]) for col in existing_service_cols if row[col] > 0}, axis=1).to_dict()
            client_data['Service_Avg_Revenue_Per_Project'] = client_data['ClientID'].map(avg_service_rev_dict).fillna({})
            
            # --- New: Total service revenue per client (absolute E£) ---
            service_total_rev_dict = service_totals.apply(lambda row: {col: float(row[col]) for col in existing_service_cols if row[col] != 0}, axis=1).to_dict()
            client_data['Service_Total_Revenue'] = client_data['ClientID'].map(service_total_rev_dict).fillna({})

            # --- New: Project diversity by service (percentage of projects that include each service) ---
            # For project-level presence, consider any version that had the service -> group original data by Quote_ID
            proj_diversity_pct_dict = {}
            try:
                proj_service_presence = data.groupby(['ClientID', 'Quote_ID'])[existing_service_cols].sum().gt(0).astype(int)
                proj_service_counts = proj_service_presence.groupby('ClientID').sum()

                # Align with client totals (Total_Quotations is unique projects per client)
                # Avoid division by zero
                total_projects_series = client_data.set_index('ClientID')['Total_Quotations'].replace(0, np.nan)
                proj_diversity_pct = proj_service_counts.div(total_projects_series, axis=0).fillna(0)

                proj_diversity_pct_dict = proj_diversity_pct.apply(
                    lambda row: {col: float(row[col]) for col in existing_service_cols if row[col] > 0},
                    axis=1
                ).to_dict()

                client_data['Project_Diversity_Breakdown'] = client_data['ClientID'].map(proj_diversity_pct_dict).fillna({})
            except Exception:
                # If something goes wrong, add empty breakdowns
                client_data['Project_Diversity_Breakdown'] = client_data['ClientID'].apply(lambda x: {})
            
            # --- New: Expand per-service dicts to explicit numeric columns for CSV/export ---
            # Ensure proj_diversity_pct_dict exists (empty if exception)
            for svc in existing_service_cols:
                # Total spent per service
                client_data[f'Total_{svc}'] = client_data['ClientID'].map(lambda cid: service_total_rev_dict.get(cid, {}).get(svc, 0.0))
                # Avg revenue per project per service
                client_data[f'AvgPerProject_{svc}'] = client_data['ClientID'].map(lambda cid: avg_service_rev_dict.get(cid, {}).get(svc, 0.0))
                # Project diversity percentage (0-1)
                client_data[f'ProjectDiversity_{svc}'] = client_data['ClientID'].map(lambda cid: proj_diversity_pct_dict.get(cid, {}).get(svc, 0.0))
        else:
            client_data['Top_Service_by_Volume'] = 'No Service'
            client_data['Top_Service_by_Value'] = 'No Service'
            client_data['Revenue_by_Service'] = 0
            client_data['Service_Revenue_Breakdown'] = client_data['ClientID'].apply(lambda x: {})
            client_data['Project_Diversity_Breakdown'] = client_data['ClientID'].apply(lambda x: {})
            # create explicit zero columns for expected service columns (so CSV exports keep consistent columns)
            for svc in service_columns:
                client_data[f'Total_{svc}'] = 0.0
                client_data[f'AvgPerProject_{svc}'] = 0.0
                client_data[f'ProjectDiversity_{svc}'] = 0.0
        
        # Calculate retention and churn rates
        # Retention Rate: Measure of customer stickiness - ratio of repeat business
        # We calculate this as: customers with multiple quotes who keep coming back
        # For simplicity: (Years Active / Average Days Between Quotes) normalized
        # Better approach: Use successful quotes over time as indicator of retention
        
        # Calculate retention based on consistent engagement over time
        def calculate_retention_rate(row):
            years_active = row['Years_Active']
            avg_days = row.get('Average_Days_Between_Quotes', 0)
            total_quotes = row['Total_Quotations']
            converted = row['Converted_Quotations']
            
            # If only one quote, retention is based solely on conversion
            if total_quotes <= 1:
                return 1.0 if converted > 0 else 0.0
            
            # For multiple quotes: combination of conversion rate and engagement frequency
            # Retention increases with: more converted quotes, consistent engagement (lower avg days)
            conversion_factor = converted / total_quotes if total_quotes > 0 else 0
            
            # Engagement factor: customers who quote more frequently are more "retained"
            # Normalize average days (30 days = high engagement, 365+ = low)
            if avg_days > 0:
                engagement_factor = max(0, min(1, (365 - avg_days) / 365))
            else:
                engagement_factor = 0.5
            
            # Activity factor: customers active for more years show retention
            activity_factor = min(1.0, years_active / 5.0)  # Cap at 5 years
            
            # Weighted retention score
            # Conversion factor (50% weight): How many quotes convert to projects
            # Engagement factor (20% weight): How frequently the customer requests quotes
            # Activity factor (30% weight): How long the customer has been active
            retention = (conversion_factor * 0.5) + (engagement_factor * 0.2) + (activity_factor * 0.3)
            
            return max(0, min(1, retention))  # Ensure between 0 and 1
        
        client_data['Retention_Rate'] = client_data.apply(calculate_retention_rate, axis=1)
        client_data['Churn_Rate'] = 1 - client_data['Retention_Rate']
        
        # Calculate quote-to-project ratio
        client_data['Quote_to_Project_Ratio'] = np.where(
            client_data['Projects_Per_Year'] > 0,
            client_data['Total_Quotations'] / client_data['Projects_Per_Year'],
            client_data['Total_Quotations']
        )
        
        # Calculate OCDS (Offer Convincing Difficulty (OCDS) Score)
        # Total offers sent (all versions) / Accepted offers
        # We need to count ALL quote versions from original data
        all_quotes_per_client = data.groupby('ClientID')['Number'].count().to_dict()
        client_data['Total_Offers_Sent'] = client_data['ClientID'].map(all_quotes_per_client).fillna(0)
        
        # OCDS = Total offers sent / Converted quotations (avoid division by zero)
        client_data['OCDS'] = np.where(
            client_data['Converted_Quotations'] > 0,
            client_data['Total_Offers_Sent'] / client_data['Converted_Quotations'],
            client_data['Total_Offers_Sent']  # If no conversions, OCDS equals total offers
        )

        # --- New: Average number of offers per project ---
        client_data['Avg_Offers_per_Project'] = np.where(
            client_data['Total_Quotations'] > 0,
            client_data['Total_Offers_Sent'] / client_data['Total_Quotations'],
            0
        )
        
        # Customer segmentation
        def segment_customer(row):
            clv = row['CLV'] if not pd.isna(row['CLV']) else 0
            win_rate = row['Win_Rate_%'] if not pd.isna(row['Win_Rate_%']) else 0
            converted_deals = row['Converted_Quotations'] if not pd.isna(row['Converted_Quotations']) else 0
            
            if clv >= 75000 and win_rate >= 40:
                return 'High'
            elif clv >= 30000 or (win_rate >= 60 and converted_deals >= 3):
                return 'Medium'
            else:
                return 'Low'
        
        client_data['Customer_Segment'] = client_data.apply(segment_customer, axis=1)
        
        # Select final columns
        final_columns = [
            'ClientID', 'First_Quote_Date', 'Last_Quote_Date', 'Average_Days_Between_Quotes',
            'Years_Active', 'Projects_Per_Year', 'Project_Diversity', 'Total_Project_Value',
            'CLV', 'Total_Quotations', 'Converted_Quotations', 'Lost_Quotations',
            'Win_Rate_%', 'Loss_Rate_%', 'Top_Service_by_Volume', 'Top_Service_by_Value',
            'Revenue_by_Service', 'Retention_Rate', 'Churn_Rate',
            'Quote_to_Project_Ratio', 'Customer_Segment', 'Idle_Time_Days', 'Idle_Time_Years',
            'Total_Offers_Sent', 'OCDS', 'Avg_Offers_per_Project',
            # New breakdowns
            'Service_Revenue_Breakdown', 'Project_Diversity_Breakdown', 'Service_Total_Revenue', 'Service_Avg_Revenue_Per_Project'
        ]
        
        existing_final_columns = [col for col in final_columns if col in client_data.columns]
        client_data_clean = client_data[existing_final_columns].copy()
        
        return client_data_clean, None
        
    except Exception as e:
        return None, str(e)

def create_visualizations(df):
    """Create interactive visualizations for the dashboard"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer Segment Distribution with enhanced colors
        segment_counts = df['Customer_Segment'].value_counts()
        colors = ['#4facfe', '#43e97b', '#fa709a']  # Bright gradient colors
        fig_pie = px.pie(
            values=segment_counts.values, 
            names=segment_counts.index,
            title="🎯 Customer Segment Distribution",
            color_discrete_sequence=colors
        )
        fig_pie.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont_size=16,
            marker=dict(line=dict(color='#FFFFFF', width=3))
        )
        fig_pie.update_layout(
            title_font_size=18,
            font=dict(size=14),
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Win Rate Distribution with vibrant colors
        fig_hist = px.histogram(
            df, 
            x='Win_Rate_%',
            nbins=20,
            title="📈 Win Rate Distribution",
            color='Customer_Segment',
            color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a']
        )
        fig_hist.update_layout(
            xaxis_title="Win Rate (%)", 
            yaxis_title="Number of Customers",
            title_font_size=18,
            font=dict(size=14),
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='lightgray'),
            yaxis=dict(gridcolor='lightgray')
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # CLV vs Win Rate Scatter Plot with enhanced styling
    fig_scatter = px.scatter(
        df,
        x='Win_Rate_%',
        y='CLV',
        size='Total_Quotations',
        color='Customer_Segment',
        hover_data=['ClientID', 'Projects_Per_Year', 'Retention_Rate', 'Churn_Rate'],
        title="💰 Customer Lifetime Value vs Win Rate",
        color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a']
    )
    fig_scatter.update_layout(
        xaxis_title="Win Rate (%)",
        yaxis_title="Customer Lifetime Value (E£)",
        height=500,
        title_font_size=20,
        font=dict(size=14),
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='lightgray'),
        yaxis=dict(gridcolor='lightgray')
    )
    fig_scatter.update_traces(
        marker=dict(
            line=dict(width=2, color='white'),
            opacity=0.8
        )
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Enhanced retention and churn analysis
    col3, col4 = st.columns(2)
    
    with col3:
        # Retention Rate Distribution
        fig_retention = px.histogram(
            df,
            x='Retention_Rate',
            nbins=15,
            title="🎯 Customer Retention Rate Distribution",
            color='Customer_Segment',
            color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a']
        )
        fig_retention.update_layout(
            xaxis_title="Retention Rate",
            yaxis_title="Number of Customers",
            title_font_size=18,
            font=dict(size=14),
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='lightgray'),
            yaxis=dict(gridcolor='lightgray')
        )
        st.plotly_chart(fig_retention, use_container_width=True)
    
    with col4:
        # Top Services Analysis with rainbow colors
        top_services = df['Top_Service_by_Volume'].value_counts().head(10)
        rainbow_colors = ['#ff006e', '#8338ec', '#3a86ff', '#06ffa5', '#ffbe0b', 
                         '#fb5607', '#ff006e', '#8338ec', '#3a86ff', '#06ffa5']
        fig_bar = px.bar(
            x=top_services.index,
            y=top_services.values,
            title="🌟 Most Popular Services",
            color=top_services.values,
            color_continuous_scale='Viridis'
        )
        fig_bar.update_layout(
            xaxis_title="Service", 
            yaxis_title="Number of Customers",
            title_font_size=18,
            font=dict(size=14),
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='lightgray'),
            yaxis=dict(gridcolor='lightgray')
        )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Add Project Analysis Section
    st.subheader("📊 Project Analysis")
    col5, col6 = st.columns(2)
    
    with col5:
        # Projects per Customer Distribution
        # Use Total_Quotations directly as it represents projects per customer
        fig_projects = px.histogram(
            df,
            x='Total_Quotations',
            nbins=20,
            title="📁 Projects per Customer Distribution",
            color='Customer_Segment',
            color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a']
        )
        fig_projects.update_layout(
            xaxis_title="Number of Projects",
            yaxis_title="Number of Customers",
            title_font_size=18,
            font=dict(size=14),
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='lightgray'),
            yaxis=dict(gridcolor='lightgray')
        )
        st.plotly_chart(fig_projects, use_container_width=True)
    
    with col6:
        # Project Conversion Analysis
        fig_conversion = px.scatter(
            df,
            x='Total_Quotations',
            y='Converted_Quotations',
            color='Customer_Segment',
            size='CLV',
            title="🎯 Project Conversion Analysis",
            color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a'],
            hover_data=['ClientID', 'Win_Rate_%']
        )
        fig_conversion.update_layout(
            xaxis_title="Total Quotations",
            yaxis_title="Converted Projects",
            title_font_size=18,
            font=dict(size=14),
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='lightgray'),
            yaxis=dict(gridcolor='lightgray')
        )
        fig_conversion.add_trace(
            go.Scatter(
                x=[0, df['Total_Quotations'].max()],
                y=[0, df['Total_Quotations'].max()],
                mode='lines',
                line=dict(dash='dash', color='gray'),
                name='100% Conversion',
                showlegend=True
            )
        )
        st.plotly_chart(fig_conversion, use_container_width=True)

def display_summary_metrics(df):
    """Display key summary metrics with colorful styling"""
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    
    # First row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = len(df)
        st.markdown(f"""
        <div class="metric-card">
            <h3>👥 Total Customers</h3>
            <h2>{total_customers:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Sum up the unique projects per customer
        total_projects = df['Total_Quotations'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>📁 Total Projects</h3>
            <h2>{total_projects:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_projects_per_customer = df['Total_Quotations'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Avg Projects/Customer</h3>
            <h2>{avg_projects_per_customer:.1f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_converted_projects = df['Converted_Quotations'].sum()
        project_conversion_rate = (total_converted_projects / total_projects * 100) if total_projects > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>✅ Project Conversion Rate</h3>
            <h2>{project_conversion_rate:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row of metrics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        avg_clv = df['CLV'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Average CLV</h3>
            <h2>E£{avg_clv:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        avg_win_rate = df['Win_Rate_%'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯 Average Win Rate</h3>
            <h2>{avg_win_rate:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col7:
        avg_retention = df['Retention_Rate'].mean() * 100
        st.markdown(f"""
        <div class="metric-card">
            <h3>🔄 Average Retention</h3>
            <h2>{avg_retention:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col8:
        high_value_customers = len(df[df['Customer_Segment'] == 'High'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>⭐ High-Value Customers</h3>
            <h2>{high_value_customers:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_individual_customer(customer_data, selected_customer, df_raw=None):
    """Display individual customer analysis with enhanced highlighting"""
    
    segment_class = get_segment_color_class(customer_data['Customer_Segment'])
    retention_class = get_retention_color_class(customer_data['Retention_Rate'])
    
    st.markdown(f"""
    <div class="customer-highlight">
        <h2>👤 {selected_customer} Analytics</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Main metrics in colorful cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="{segment_class}">
            <h3>🎯 Customer Segment</h3>
            <h2>{customer_data['Customer_Segment']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stats-container">
            <h4>💰 CLV: <span style="color: #4facfe; font-weight: bold;">E£{customer_data['CLV']:,.2f}</span></h4>
            <h4>📊 Win Rate: <span style="color: #43e97b; font-weight: bold;">{customer_data['Win_Rate_%']:.1f}%</span></h4>
            <h4>📅 Years Active: <span style="color: #fa709a; font-weight: bold;">{customer_data['Years_Active']:.1f}</span></h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Calculate time span between first and last project
        time_span = (customer_data['Last_Quote_Date'] - customer_data['First_Quote_Date']).days / 30  # Convert to months
        total_projects = customer_data['Total_Quotations']
        
        # Check if customer has limited data
        has_limited_data = (total_projects <= 2 and time_span <= 6)
        
        if has_limited_data:
            st.markdown(f"""
            <div class="warning-highlight" style="margin-bottom: 1rem;">
                ⚠️ <strong>Limited Data:</strong> This customer has only {total_projects} project(s) over {time_span:.1f} month(s). Some metrics may be less reliable.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="{retention_class}">
            <h3>🔄 Retention Analysis</h3>
            <h4>Retention Rate: {customer_data['Retention_Rate']*100:.1f}%</h4>
            <h4>Churn Rate: {customer_data['Churn_Rate']*100:.1f}%</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Format idle time for display
        idle_years = customer_data['Idle_Time_Years']
        idle_days = customer_data['Idle_Time_Days']
        
        if idle_days < 30:
            idle_text = f"{idle_days:.0f} days"
        else:
            idle_text = f"{idle_years:.1f} years"
            
        # Determine idle time color based on duration
        if idle_days < 180:  # Less than 6 months
            idle_color = "#43e97b"  # Green
        elif idle_days < 365:  # Less than 1 year
            idle_color = "#ffbe0b"  # Yellow
        else:
            idle_color = "#fa709a"  # Red
            
        st.markdown(f"""
        <div class="stats-container">
            <h4>� Active Period: <span style="color: #667eea; font-weight: bold;">{customer_data['Years_Active']:.1f} years</span></h4>
            <h4>⏳ Idle Time: <span style="color: {idle_color}; font-weight: bold;">{idle_text}</span></h4>
            <h4>🎲 Project Diversity: <span style="color: #764ba2; font-weight: bold;">{customer_data['Project_Diversity']}</span></h4>
            <h4>🏆 Top Service: <span style="color: #f093fb; font-weight: bold;">{customer_data['Top_Service_by_Volume']}</span></h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Quote analysis
        conversion_rate = (customer_data['Converted_Quotations'] / customer_data['Total_Quotations']) * 100 if customer_data['Total_Quotations'] > 0 else 0
        
        st.markdown(f"""
        <div class="stats-container">
            <h3>📋 Project Analysis</h3>
            <h4>Total Projects: <span style="color: #4facfe; font-weight: bold;">{customer_data['Total_Quotations']}</span></h4>
            <h4>✅ Completed: <span style="color: #43e97b; font-weight: bold;">{customer_data['Converted_Quotations']}</span></h4>
            <h4>❌ Cancelled: <span style="color: #fa709a; font-weight: bold;">{customer_data['Lost_Quotations']}</span></h4>
            <h4>🎯 Success Rate: <span style="color: #667eea; font-weight: bold;">{conversion_rate:.1f}%</span></h4>
            <h4>📩 Avg Offers/Project: <span style="color: #8338ec; font-weight: bold;">{customer_data.get('Avg_Offers_per_Project', 0):.2f}</span></h4>
        </div>
        """, unsafe_allow_html=True)
        
        # OCDS (Offer Convincing Difficulty Score)
        ocds_value = customer_data.get('OCDS', 0)
        total_offers = customer_data.get('Total_Offers_Sent', 0)
        
        # Determine OCDS color based on difficulty (lower is better)
        if ocds_value <= 1.5:
            ocds_color = '#43e97b'  # Green - Easy to convince
            ocds_label = 'Easy'
        elif ocds_value <= 3:
            ocds_color = '#ffbe0b'  # Yellow - Moderate
            ocds_label = 'Moderate'
        else:
            ocds_color = '#fa709a'  # Red - Difficult
            ocds_label = 'Difficult'
        
        st.markdown(f"""
        <div class="stats-container">
            <h3>🎲 Offer Convincing Difficulty</h3>
            <h4>Total Offers Sent: <span style="color: #8338ec; font-weight: bold;">{total_offers}</span></h4>
            <h4>OCDS Score: <span style="color: {ocds_color}; font-weight: bold;">{ocds_value:.2f}</span> <small>({ocds_label})</small></h4>
            <p style="font-size: 12px; color: #888;">Lower score = easier to convince</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stats-container">
            <h4>💼 Service Revenue: <span style="color: #f093fb; font-weight: bold;">E£{customer_data['Revenue_by_Service']:,.2f}</span></h4>
            <h4>📈 Project Value: <span style="color: #764ba2; font-weight: bold;">E£{customer_data['Total_Project_Value']:,.2f}</span></h4>
        </div>
        """, unsafe_allow_html=True)

        # --- New charts: Revenue breakdown by service (pie), avg revenue, and service frequency ---
        try:
            svc_break = customer_data.get('Service_Revenue_Breakdown', {})
            proj_div = customer_data.get('Project_Diversity_Breakdown', {})

            # Revenue breakdown pie (absolute totals per service)
            svc_tot = customer_data.get('Service_Total_Revenue', {})
            if isinstance(svc_tot, dict) and len(svc_tot) > 0:
                labels = list(svc_tot.keys())
                values = [v for v in svc_tot.values()]
                fig_rev = px.pie(
                    names=labels,
                    values=values,
                    title="💸 Total Spent by Service (E£)",
                    color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a', '#ffbe0b', '#8338ec', '#3a86ff']
                )
                fig_rev.update_traces(textinfo='label+value', textfont_size=14)
                fig_rev.update_layout(title_font_size=18, font=dict(size=14))
                st.plotly_chart(fig_rev, use_container_width=True)

            # Average revenue per project by service (absolute E£) as a pie chart
            avg_rev = customer_data.get('Service_Avg_Revenue_Per_Project', {})
            if isinstance(avg_rev, dict) and len(avg_rev) > 0:
                labels = list(avg_rev.keys())
                values = [v for v in avg_rev.values()]
                fig_avg_rev = px.pie(
                    names=labels,
                    values=values,
                    title="💵 Avg Revenue per Project by Service (E£)",
                    color_discrete_sequence=['#667eea', '#43e97b', '#fa709a', '#ffbe0b', '#8338ec', '#3a86ff']
                )
                fig_avg_rev.update_traces(textinfo='label+value', textfont_size=14)
                fig_avg_rev.update_layout(title_font_size=18, font=dict(size=14))
                st.plotly_chart(fig_avg_rev, use_container_width=True)
            # Service frequency per user by service (pie based on project inclusion)
            if isinstance(proj_div, dict) and len(proj_div) > 0:
                labels = list(proj_div.keys())
                values = [v for v in proj_div.values()]  # use raw fractions; pie shows %
                fig_freq = px.pie(
                    names=labels,
                    values=values,
                    title="📊 Service Frequency per User (%)",
                    color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a', '#ffbe0b', '#8338ec', '#3a86ff']
                )
                fig_freq.update_traces(textinfo='label+percent', textfont_size=14)
                fig_freq.update_layout(title_font_size=18, font=dict(size=14))
                st.plotly_chart(fig_freq, use_container_width=True)

            # Show a small table combining Total, Avg, and Frequency per service
            try:
                totals = customer_data.get('Service_Total_Revenue', {})
                avgs = customer_data.get('Service_Avg_Revenue_Per_Project', {})
                freqs = customer_data.get('Project_Diversity_Breakdown', {})
                # build rows for all services present in either dict
                all_services = sorted(set(list(totals.keys()) + list(avgs.keys()) + list(freqs.keys())))
                if all_services:
                    table_rows = []
                    for s in all_services:
                        table_rows.append({
                            'Service': s,
                            'Total_E£': totals.get(s, 0.0),
                            'Avg_E£_per_Project': avgs.get(s, 0.0),
                            'Frequency_%': freqs.get(s, 0.0) * 100
                        })
                    import pandas as _pd
                    svc_table = _pd.DataFrame(table_rows)
                    svc_table = svc_table.sort_values('Total_E£', ascending=False)
                    svc_table['Total_E£'] = svc_table['Total_E£'].map(lambda x: f"E£{x:,.2f}")
                    svc_table['Avg_E£_per_Project'] = svc_table['Avg_E£_per_Project'].map(lambda x: f"E£{x:,.2f}")
                    svc_table['Frequency_%'] = svc_table['Frequency_%'].map(lambda x: f"{x:.1f}%")
                    st.markdown("**🔎 Service Spend Summary**")
                    st.table(svc_table)
            except Exception as e:
                st.write(f"Error building service totals table: {e}")
        except Exception as e:
            st.write(f"Error creating service/project charts: {e}")
    
    # Project Explorer Section
    if df_raw is not None:
        st.markdown("---")
        st.markdown("""
        <div class="stats-container">
            <h3>📋 Project Explorer</h3>
            <p>Select a project to view its services and quotation details</p>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            # Filter raw data for this customer
            customer_projects = df_raw[df_raw['ClientID'] == selected_customer].copy()
            
            if len(customer_projects) > 0:
                # Extract Quote_ID if available
                if 'Number' in customer_projects.columns:
                    customer_projects['Quote_ID'] = customer_projects['Number'].astype(str).str.rsplit('.', n=1).str[0]
                    customer_projects['Version_Number'] = customer_projects['Number'].astype(str).str.rsplit('.', n=1).str[1]
                else:
                    customer_projects['Quote_ID'] = customer_projects.index.astype(str)
                    customer_projects['Version_Number'] = '1'
                
                # Get unique project names
                if 'Name' in customer_projects.columns:
                    # Create a mapping of project names to their Quote_IDs
                    project_mapping = customer_projects.groupby('Name')['Quote_ID'].first().to_dict()
                    unique_project_names = sorted(project_mapping.keys())
                    
                    # Project selector by name
                    project_options = ["-- Select Project --"] + unique_project_names
                    selected_project_name = st.selectbox(
                        "Choose a project:",
                        options=project_options,
                        key=f"project_selector_{selected_customer}"
                    )
                    
                    if selected_project_name and selected_project_name != "-- Select Project --":
                        # Get all data for this project name (could be multiple Quote_IDs with same name)
                        project_data = customer_projects[customer_projects['Name'] == selected_project_name].copy()
                        
                        # Count quotations (versions)
                        num_quotations = len(project_data)
                        
                        # Get project ID
                        project_id = project_data['Quote_ID'].iloc[0] if 'Quote_ID' in project_data.columns else "N/A"
                        
                        # Get status
                        statuses = project_data['Estimate status'].unique() if 'Estimate status' in project_data.columns else ['Unknown']
                        final_status = 'Closed' if 'Closed' in statuses else statuses[0] if len(statuses) > 0 else 'Unknown'
                        
                        # Display project header
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"""
                            <div class="stats-container">
                                <h4>📝 Project Name</h4>
                                <h3 style="color: #4facfe;">{selected_project_name}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="stats-container">
                                <h4>📊 Quotations Sent</h4>
                                <h3 style="color: #43e97b;">{num_quotations}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            status_color = '#43e97b' if final_status == 'Closed' else '#fa709a'
                            st.markdown(f"""
                            <div class="stats-container">
                                <h4>✅ Status</h4>
                                <h3 style="color: {status_color};">{final_status}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Project ID
                        st.markdown(f"""
                        <div class="stats-container">
                            <h4>📁 Project ID</h4>
                            <p style="font-size: 16px; color: #667eea; font-weight: bold;">{project_id}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Identify service columns (assuming they're the ones with numeric values, excluding standard columns)
                        exclude_cols = ['Date', 'Number', 'Estimate status', 'Taxable amount', 'ClientID', 
                                       'converted to invoice (AMOUNT)', 'Name', 'Quote_ID', 'Version_Number']
                        
                        service_cols = [col for col in project_data.columns 
                                       if col not in exclude_cols and pd.api.types.is_numeric_dtype(project_data[col])]
                        
                        if service_cols:
                            st.markdown("""
                            <div class="stats-container">
                                <h4>🛠️ Services in this Project</h4>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Aggregate services across all versions to see which services were included
                        service_summary = []
                        for svc in service_cols:
                            total_value = project_data[svc].sum()
                            if total_value > 0:  # Only show services that were actually used
                                service_summary.append({
                                    'Service': svc,
                                    'Total_Value': total_value
                                })
                        
                        if service_summary:
                            service_df = pd.DataFrame(service_summary)
                            service_df = service_df.sort_values('Total_Value', ascending=False)
                            
                            # Display as cards
                            cols = st.columns(min(3, len(service_summary)))
                            for i, (idx, row) in enumerate(service_df.iterrows()):
                                with cols[i % 3]:
                                    st.markdown(f"""
                                    <div class="stats-container" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                                        <h4>{row['Service']}</h4>
                                        <p><strong>Total:</strong> E£{row['Total_Value']:,.2f}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Show detailed version history
                            st.markdown("---")
                            st.markdown("**📜 Quotation Version History**")
                            
                            # Prepare version data
                            version_display = project_data[['Version_Number', 'Date', 'Estimate status', 'Taxable amount'] + service_cols].copy()
                            if 'Date' in version_display.columns:
                                version_display['Date'] = pd.to_datetime(version_display['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
                            
                            # Format currency columns
                            for col in ['Taxable amount'] + service_cols:
                                if col in version_display.columns:
                                    version_display[col] = version_display[col].apply(lambda x: f"E£{x:,.2f}" if pd.notna(x) and x > 0 else "-")
                            
                            st.dataframe(version_display, use_container_width=True)
                        else:
                            st.info("No services found with values > 0 for this project.")
                else:
                    st.info("No 'Name' column found in data. Cannot search by project name.")
            else:
                st.warning("No project data found for this customer.")
        except Exception as e:
            st.error(f"Error loading project data: {e}")

def main():
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
                st.dataframe(df_raw.head(10), use_container_width=True)
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
                st.dataframe(processed_data.head(10), use_container_width=True)
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
                        use_container_width=True,
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

        st.dataframe(styled_sample, use_container_width=True)
        
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