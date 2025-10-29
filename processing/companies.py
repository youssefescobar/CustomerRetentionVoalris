import pandas as pd
import streamlit as st


def process_company_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process company-level data to generate company analytics."""
    try:
        data = df.copy()
        data.columns = data.columns.str.strip()

        if 'Location' in data.columns:
            data['Country'] = data['Location'].astype(str).str.strip()
            valid_countries = ['UAE', 'KSA', 'Gulf', 'Kuwait', 'Egypt', 'Oman', 'Lebanon', 'Levant', 'Out Side UAE', 'Jordan']
            data['Country'] = data['Country'].apply(lambda x: x if x in valid_countries else 'Others')
        else:
            data['Country'] = 'Unknown'

        if 'Company' not in data.columns:
            data['Company'] = 'Unknown'
        if 'Client' not in data.columns:
            data['Client'] = 'Unknown'
        if 'ClientID' not in data.columns:
            data['ClientID'] = 'Unknown'

        numeric_columns = ['Taxable amount', 'converted to invoice (AMOUNT)']
        existing_numeric_cols = [col for col in numeric_columns if col in data.columns]
        data[existing_numeric_cols] = data[existing_numeric_cols].apply(pd.to_numeric, errors='coerce')

        company_data = data.groupby(['Company', 'Country']).agg({
            'Client': lambda x: sorted(x.dropna().unique().tolist()),
            'ClientID': lambda x: sorted(x.dropna().unique().tolist()),
            'Number': 'count',
            'Estimate status': lambda x: (x == 'Closed').sum(),
            'Taxable amount': 'sum',
            'converted to invoice (AMOUNT)': 'sum'
        }).reset_index()

        company_data.columns = ['Company', 'Country', 'Representatives', 'ClientIDs',
                                'Total_Quotes', 'Closed_Quotes', 'Total_Value',
                                'Total_Revenue']

        company_data['Total_Clients'] = company_data['ClientIDs'].apply(len)
        company_data['Win_Rate_%'] = (company_data['Closed_Quotes'] / company_data['Total_Quotes'] * 100).fillna(0)
        company_data = company_data.sort_values('Total_Revenue', ascending=False)
        return company_data
    except Exception as e:
        st.error(f"Error processing company data: {str(e)}")
        return pd.DataFrame()


