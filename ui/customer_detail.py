import pandas as pd
import streamlit as st
import plotly.express as px
from ui.helpers import get_segment_color_class, get_retention_color_class


def display_individual_customer(customer_data: pd.Series, selected_customer: str, df_raw: pd.DataFrame | None = None):
    segment_class = get_segment_color_class(customer_data['Customer_Segment'])
    retention_class = get_retention_color_class(customer_data['Retention_Rate'])

    st.markdown(f"""
    <div class="customer-highlight">
        <h2>👤 {selected_customer} Analytics</h2>
    </div>
    """, unsafe_allow_html=True)

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
        time_span = (customer_data['Last_Quote_Date'] - customer_data['First_Quote_Date']).days / 30
        total_projects = customer_data['Total_Quotations']
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

        idle_years = customer_data['Idle_Time_Years']
        idle_days = customer_data['Idle_Time_Days']
        if idle_days < 30:
            idle_text = f"{idle_days:.0f} days"
        else:
            idle_text = f"{idle_years:.1f} years"
        if idle_days < 180:
            idle_color = "#43e97b"
        elif idle_days < 365:
            idle_color = "#ffbe0b"
        else:
            idle_color = "#fa709a"

        st.markdown(f"""
        <div class="stats-container">
            <h4>� Active Period: <span style="color: #667eea; font-weight: bold;">{customer_data['Years_Active']:.1f} years</span></h4>
            <h4>⏳ Idle Time: <span style="color: {idle_color}; font-weight: bold;">{idle_text}</span></h4>
            <h4>🎲 Project Diversity: <span style="color: #764ba2; font-weight: bold;">{customer_data['Project_Diversity']}</span></h4>
            <h4>🏆 Top Service: <span style="color: #f093fb; font-weight: bold;">{customer_data['Top_Service_by_Volume']}</span></h4>
        </div>
        """, unsafe_allow_html=True)

    with col3:
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

        ocds_value = customer_data.get('OCDS', 0)
        total_offers = customer_data.get('Total_Offers_Sent', 0)
        if ocds_value <= 1.5:
            ocds_color = '#43e97b'
            ocds_label = 'Easy'
        elif ocds_value <= 3:
            ocds_color = '#ffbe0b'
            ocds_label = 'Moderate'
        else:
            ocds_color = '#fa709a'
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

        try:
            svc_tot = customer_data.get('Service_Total_Revenue', {})
            if isinstance(svc_tot, dict) and len(svc_tot) > 0:
                labels = list(svc_tot.keys())
                values = [v for v in svc_tot.values()]
                fig_rev = px.pie(names=labels, values=values, title="💸 Total Spent by Service (E£)", color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a', '#ffbe0b', '#8338ec', '#3a86ff'])
                fig_rev.update_traces(textinfo='label+value', textfont_size=14)
                fig_rev.update_layout(title_font_size=18, font=dict(size=14))
                st.plotly_chart(fig_rev, width='stretch')

            avg_rev = customer_data.get('Service_Avg_Revenue_Per_Project', {})
            if isinstance(avg_rev, dict) and len(avg_rev) > 0:
                labels = list(avg_rev.keys())
                values = [v for v in avg_rev.values()]
                fig_avg_rev = px.pie(names=labels, values=values, title="💵 Avg Revenue per Project by Service (E£)", color_discrete_sequence=['#667eea', '#43e97b', '#fa709a', '#ffbe0b', '#8338ec', '#3a86ff'])
                fig_avg_rev.update_traces(textinfo='label+value', textfont_size=14)
                fig_avg_rev.update_layout(title_font_size=18, font=dict(size=14))
                st.plotly_chart(fig_avg_rev, width='stretch')

            proj_div = customer_data.get('Project_Diversity_Breakdown', {})
            if isinstance(proj_div, dict) and len(proj_div) > 0:
                labels = list(proj_div.keys())
                values = [v for v in proj_div.values()]
                fig_freq = px.pie(names=labels, values=values, title="📊 Service Frequency per User (%)", color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a', '#ffbe0b', '#8338ec', '#3a86ff'])
                fig_freq.update_traces(textinfo='label+percent', textfont_size=14)
                fig_freq.update_layout(title_font_size=18, font=dict(size=14))
                st.plotly_chart(fig_freq, width='stretch')

            try:
                totals = customer_data.get('Service_Total_Revenue', {})
                avgs = customer_data.get('Service_Avg_Revenue_Per_Project', {})
                freqs = customer_data.get('Project_Diversity_Breakdown', {})
                all_services = sorted(set(list(totals.keys()) + list(avgs.keys()) + list(freqs.keys())))
                if all_services:
                    table_rows = []
                    for s in all_services:
                        table_rows.append({
                            'Service': s,
                            'Total_E£': totals.get(s, 0.0),
                            'Avg_E£_per_Project': avgs.get(s, 0.0),
                            'Frequency_%': freqs.get(s, 0.0) * 100,
                        })
                    _pd = pd
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

    if df_raw is not None:
        st.markdown("---")
        st.markdown("""
        <div class="stats-container">
            <h3>📋 Project Explorer</h3>
            <p>Select a project to view its services and quotation details</p>
        </div>
        """, unsafe_allow_html=True)

        try:
            customer_projects = df_raw[df_raw['ClientID'] == selected_customer].copy()
            if len(customer_projects) > 0:
                if 'Number' in customer_projects.columns:
                    customer_projects['Quote_ID'] = customer_projects['Number'].astype(str).str.rsplit('.', n=1).str[0]
                    customer_projects['Version_Number'] = customer_projects['Number'].astype(str).str.rsplit('.', n=1).str[1]
                else:
                    customer_projects['Quote_ID'] = customer_projects.index.astype(str)
                    customer_projects['Version_Number'] = '1'

                if 'Name' in customer_projects.columns:
                    project_mapping = customer_projects.groupby('Name')['Quote_ID'].first().to_dict()
                    unique_project_names = sorted(project_mapping.keys())
                    project_options = ["-- Select Project --"] + unique_project_names
                    selected_project_name = st.selectbox(
                        "Choose a project:", options=project_options, key=f"project_selector_{selected_customer}"
                    )

                    if selected_project_name and selected_project_name != "-- Select Project --":
                        project_data = customer_projects[customer_projects['Name'] == selected_project_name].copy()
                        num_quotations = len(project_data)
                        project_id = project_data['Quote_ID'].iloc[0] if 'Quote_ID' in project_data.columns else "N/A"
                        statuses = project_data['Estimate status'].unique() if 'Estimate status' in project_data.columns else ['Unknown']
                        final_status = 'Closed' if 'Closed' in statuses else (statuses[0] if len(statuses) > 0 else 'Unknown')

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

                        st.markdown(f"""
                        <div class="stats-container">
                            <h4>📁 Project ID</h4>
                            <p style="font-size: 16px; color: #667eea; font-weight: bold;">{project_id}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        exclude_cols = ['Date', 'Number', 'Estimate status', 'Taxable amount', 'ClientID', 'converted to invoice (AMOUNT)', 'Name', 'Quote_ID', 'Version_Number']
                        service_cols = [col for col in project_data.columns if col not in exclude_cols and pd.api.types.is_numeric_dtype(project_data[col])]

                        if service_cols:
                            st.markdown("""
                            <div class="stats-container">
                                <h4>🛠️ Services in this Project</h4>
                            </div>
                            """, unsafe_allow_html=True)

                        service_summary = []
                        for svc in service_cols:
                            total_value = project_data[svc].sum()
                            if total_value > 0:
                                service_summary.append({'Service': svc, 'Total_Value': total_value})

                        if service_summary:
                            service_df = pd.DataFrame(service_summary).sort_values('Total_Value', ascending=False)
                            cols = st.columns(min(3, len(service_summary)))
                            for i, (idx, row) in enumerate(service_df.iterrows()):
                                with cols[i % 3]:
                                    st.markdown(f"""
                                    <div class="stats-container" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                                        <h4>{row['Service']}</h4>
                                        <p><strong>Total:</strong> E£{row['Total_Value']:,.2f}</p>
                                    </div>
                                    """, unsafe_allow_html=True)

                            st.markdown("---")
                            st.markdown("**📜 Quotation Version History**")
                            version_display = project_data[['Version_Number', 'Date', 'Estimate status', 'Taxable amount'] + service_cols].copy()
                            if 'Date' in version_display.columns:
                                version_display['Date'] = pd.to_datetime(version_display['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
                            for col in ['Taxable amount'] + service_cols:
                                if col in version_display.columns:
                                    version_display[col] = version_display[col].apply(lambda x: f"E£{x:,.2f}" if pd.notna(x) and x > 0 else "-")
                            st.dataframe(version_display, width='stretch')
                        else:
                            st.info("No services found with values > 0 for this project.")
                else:
                    st.info("No 'Name' column found in data. Cannot search by project name.")
            else:
                st.warning("No project data found for this customer.")
        except Exception as e:
            st.error(f"Error loading project data: {e}")


