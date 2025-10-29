import pandas as pd
import numpy as np


def process_customer_data(df: pd.DataFrame):
    """
    Process raw customer data to generate analytics.
    Returns (processed_df, error_message_or_None).
    """
    try:
        data = df.copy()
        data.columns = data.columns.str.strip()

        service_columns = ['CME', 'Design', 'Med Com', 'Multichannel', 'Onsite Support',
                           'Other Services', 'Video', 'Webinars', 'Websites']
        numeric_columns = service_columns + ['Taxable amount', 'converted to invoice (AMOUNT)']
        existing_numeric_cols = [col for col in numeric_columns if col in data.columns]
        data[existing_numeric_cols] = data[existing_numeric_cols].apply(pd.to_numeric, errors='coerce')

        try:
            data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y')
        except Exception:
            data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

        if 'Number' in data.columns:
            data['Project_Number'] = data['Number'].astype(str).str.split('.').str[3]

            def extract_version(number_str):
                try:
                    parts = str(number_str).split('.')
                    if len(parts) >= 5:
                        version_str = parts[4]
                        try:
                            return float(version_str)
                        except Exception:
                            import re
                            numeric = re.findall(r'\d+', version_str)
                            if numeric:
                                return float(numeric[0]) + 0.1
                            return 1.0
                    return 1.0
                except Exception:
                    return 1.0

            data['Version_Number'] = data['Number'].apply(extract_version)
            data['Quote_ID'] = data['Number'].astype(str).str.rsplit('.', n=1).str[0]
        else:
            data['Project_Number'] = range(len(data))
            data['Quote_ID'] = range(len(data))
            data['Version_Number'] = 1.0

        data_latest = data.sort_values('Version_Number').groupby(['ClientID', 'Quote_ID']).tail(1).copy()

        def get_project_status(group):
            if (group['Estimate status'] == 'Closed').any():
                return 'Closed'
            return 'Rejected'

        if 'Estimate status' in data.columns:
            project_status = data.groupby(['ClientID', 'Quote_ID']).apply(get_project_status).reset_index(name='Final_Project_Status')
            data_latest = data_latest.merge(project_status[['ClientID', 'Quote_ID', 'Final_Project_Status']], on=['ClientID', 'Quote_ID'], how='left')
            data_latest['Project_Status_For_Counting'] = data_latest['Final_Project_Status']
        else:
            data_latest['Project_Status_For_Counting'] = 'Unknown'

        agg_dict = {
            'Date': ['min', 'max'],
            'Quote_ID': 'nunique',
            'Project_Status_For_Counting': [
                ('Closed', lambda x: (x == 'Closed').sum()),
                ('Rejected', lambda x: (x == 'Rejected').sum()),
            ],
            'Taxable amount': 'sum' if 'Taxable amount' in data_latest.columns else (lambda x: 0),
            'converted to invoice (AMOUNT)': 'sum' if 'converted to invoice (AMOUNT)' in data_latest.columns else (lambda x: 0),
            'Name': 'nunique' if 'Name' in data_latest.columns else (lambda x: 1),
            'Project_Number': 'nunique',
        }

        for col in service_columns:
            if col in data_latest.columns:
                agg_dict[col] = 'sum'

        client_data = data_latest.groupby('ClientID').agg(agg_dict).reset_index()

        client_data.columns = ['_'.join(str(c) for c in col).strip() if isinstance(col, tuple) and col[1] else (col[0] if isinstance(col, tuple) else col) for col in client_data.columns.values]

        client_data['First_Quote_Date'] = client_data['Date_min']
        client_data['Last_Quote_Date'] = client_data['Date_max']
        client_data['Years_Active'] = (client_data['Last_Quote_Date'] - client_data['First_Quote_Date']).dt.days / 365
        client_data['Years_Active'] = client_data['Years_Active'].replace(0, 0.003)

        today = pd.Timestamp.now()
        client_data['Idle_Time_Days'] = (today - client_data['Last_Quote_Date']).dt.days
        client_data['Idle_Time_Years'] = client_data['Idle_Time_Days'] / 365

        try:
            avg_days = data_latest.groupby('ClientID')['Date'].apply(lambda x: x.sort_values().diff().mean().days if len(x) > 1 else 0).reset_index(name='Average_Days_Between_Quotes')
            client_data = client_data.merge(avg_days, on='ClientID', how='left')
        except Exception:
            client_data['Average_Days_Between_Quotes'] = 30

        def calculate_projects_per_year(row):
            years = row['Years_Active']
            projects = row.get('Project_Number_nunique', 1)
            return projects if years < 1 else projects / years

        client_data['Projects_Per_Year'] = client_data.apply(calculate_projects_per_year, axis=1)

        client_data['Project_Diversity'] = client_data.get('Name_nunique', 1)
        client_data['Total_Project_Value'] = client_data.get('Taxable amount_sum', 0).fillna(0)
        client_data['CLV'] = client_data.get('converted to invoice (AMOUNT)_sum', 0).fillna(0)
        client_data['Total_Quotations'] = client_data.get('Quote_ID_nunique', 1)

        if 'Project_Status_For_Counting_Closed' in client_data.columns:
            client_data['Converted_Quotations'] = client_data['Project_Status_For_Counting_Closed']
        else:
            client_data['Converted_Quotations'] = 0
        if 'Project_Status_For_Counting_Rejected' in client_data.columns:
            client_data['Lost_Quotations'] = client_data['Project_Status_For_Counting_Rejected']
        else:
            client_data['Lost_Quotations'] = 0

        client_data['Win_Rate_%'] = (client_data['Converted_Quotations'] / client_data['Total_Quotations']) * 100
        client_data['Loss_Rate_%'] = (client_data['Lost_Quotations'] / client_data['Total_Quotations']) * 100

        existing_service_cols = [col for col in service_columns if col in data_latest.columns]
        if existing_service_cols:
            service_totals = data_latest.groupby('ClientID')[existing_service_cols].sum().fillna(0)
            client_data['Top_Service_by_Volume'] = service_totals.apply(lambda row: row.idxmax() if row.max() > 0 else 'No Service', axis=1).values
            client_data['Top_Service_by_Value'] = service_totals.apply(lambda row: row.idxmax() if row.max() > 0 else 'No Service', axis=1).values
            client_data['Revenue_by_Service'] = service_totals.sum(axis=1).values

            svc_rev_sum = service_totals.sum(axis=1).replace({0: np.nan})
            service_revenue_pct = service_totals.div(svc_rev_sum, axis=0).fillna(0)
            service_revenue_pct_dict = service_revenue_pct.apply(lambda row: {col: float(row[col]) for col in existing_service_cols if row[col] > 0}, axis=1).to_dict()
            client_data['Service_Revenue_Breakdown'] = client_data['ClientID'].map(service_revenue_pct_dict).fillna({})

            avg_service_rev = service_totals.div(client_data.set_index('ClientID')['Total_Quotations'].replace(0, np.nan), axis=0).fillna(0)
            avg_service_rev_dict = avg_service_rev.apply(lambda row: {col: float(row[col]) for col in existing_service_cols if row[col] > 0}, axis=1).to_dict()
            client_data['Service_Avg_Revenue_Per_Project'] = client_data['ClientID'].map(avg_service_rev_dict).fillna({})

            service_total_rev_dict = service_totals.apply(lambda row: {col: float(row[col]) for col in existing_service_cols if row[col] != 0}, axis=1).to_dict()
            client_data['Service_Total_Revenue'] = client_data['ClientID'].map(service_total_rev_dict).fillna({})

            proj_diversity_pct_dict = {}
            try:
                proj_service_presence = data.groupby(['ClientID', 'Quote_ID'])[existing_service_cols].sum().gt(0).astype(int)
                proj_service_counts = proj_service_presence.groupby('ClientID').sum()
                total_projects_series = client_data.set_index('ClientID')['Total_Quotations'].replace(0, np.nan)
                proj_diversity_pct = proj_service_counts.div(total_projects_series, axis=0).fillna(0)
                proj_diversity_pct_dict = proj_diversity_pct.apply(lambda row: {col: float(row[col]) for col in existing_service_cols if row[col] > 0}, axis=1).to_dict()
                client_data['Project_Diversity_Breakdown'] = client_data['ClientID'].map(proj_diversity_pct_dict).fillna({})
            except Exception:
                client_data['Project_Diversity_Breakdown'] = client_data['ClientID'].apply(lambda x: {})

            for svc in existing_service_cols:
                client_data[f'Total_{svc}'] = client_data['ClientID'].map(lambda cid: service_total_rev_dict.get(cid, {}).get(svc, 0.0))
                client_data[f'AvgPerProject_{svc}'] = client_data['ClientID'].map(lambda cid: avg_service_rev_dict.get(cid, {}).get(svc, 0.0))
                client_data[f'ProjectDiversity_{svc}'] = client_data['ClientID'].map(lambda cid: proj_diversity_pct_dict.get(cid, {}).get(svc, 0.0))
        else:
            client_data['Top_Service_by_Volume'] = 'No Service'
            client_data['Top_Service_by_Value'] = 'No Service'
            client_data['Revenue_by_Service'] = 0
            client_data['Service_Revenue_Breakdown'] = client_data['ClientID'].apply(lambda x: {})
            client_data['Project_Diversity_Breakdown'] = client_data['ClientID'].apply(lambda x: {})
            for svc in service_columns:
                client_data[f'Total_{svc}'] = 0.0
                client_data[f'AvgPerProject_{svc}'] = 0.0
                client_data[f'ProjectDiversity_{svc}'] = 0.0

        def calculate_retention_rate(row):
            years_active = row['Years_Active']
            avg_days = row.get('Average_Days_Between_Quotes', 0)
            total_quotes = row['Total_Quotations']
            converted = row['Converted_Quotations']
            if total_quotes <= 1:
                return 1.0 if converted > 0 else 0.0
            conversion_factor = converted / total_quotes if total_quotes > 0 else 0
            if avg_days > 0:
                engagement_factor = max(0, min(1, (365 - avg_days) / 365))
            else:
                engagement_factor = 0.5
            activity_factor = min(1.0, years_active / 5.0)
            retention = (conversion_factor * 0.5) + (engagement_factor * 0.2) + (activity_factor * 0.3)
            return max(0, min(1, retention))

        client_data['Retention_Rate'] = client_data.apply(calculate_retention_rate, axis=1)
        client_data['Churn_Rate'] = 1 - client_data['Retention_Rate']

        client_data['Quote_to_Project_Ratio'] = np.where(
            client_data['Projects_Per_Year'] > 0,
            client_data['Total_Quotations'] / client_data['Projects_Per_Year'],
            client_data['Total_Quotations']
        )

        all_quotes_per_client = data.groupby('ClientID')['Number'].count().to_dict()
        client_data['Total_Offers_Sent'] = client_data['ClientID'].map(all_quotes_per_client).fillna(0)
        client_data['OCDS'] = np.where(
            client_data['Converted_Quotations'] > 0,
            client_data['Total_Offers_Sent'] / client_data['Converted_Quotations'],
            client_data['Total_Offers_Sent']
        )
        client_data['Avg_Offers_per_Project'] = np.where(
            client_data['Total_Quotations'] > 0,
            client_data['Total_Offers_Sent'] / client_data['Total_Quotations'],
            0
        )

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

        final_columns = [
            'ClientID', 'First_Quote_Date', 'Last_Quote_Date', 'Average_Days_Between_Quotes',
            'Years_Active', 'Projects_Per_Year', 'Project_Diversity', 'Total_Project_Value',
            'CLV', 'Total_Quotations', 'Converted_Quotations', 'Lost_Quotations',
            'Win_Rate_%', 'Loss_Rate_%', 'Top_Service_by_Volume', 'Top_Service_by_Value',
            'Revenue_by_Service', 'Retention_Rate', 'Churn_Rate',
            'Quote_to_Project_Ratio', 'Customer_Segment', 'Idle_Time_Days', 'Idle_Time_Years',
            'Total_Offers_Sent', 'OCDS', 'Avg_Offers_per_Project',
            'Service_Revenue_Breakdown', 'Project_Diversity_Breakdown', 'Service_Total_Revenue', 'Service_Avg_Revenue_Per_Project'
        ]
        existing_final_columns = [col for col in final_columns if col in client_data.columns]
        client_data_clean = client_data[existing_final_columns].copy()
        return client_data_clean, None
    except Exception as e:
        return None, str(e)


