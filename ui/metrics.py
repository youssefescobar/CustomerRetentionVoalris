import streamlit as st


def display_summary_metrics(df):
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)

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


