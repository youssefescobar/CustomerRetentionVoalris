import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def create_visualizations(df):
    col1, col2 = st.columns(2)

    with col1:
        segment_counts = df['Customer_Segment'].value_counts()
        colors = ['#4facfe', '#43e97b', '#fa709a']
        fig_pie = px.pie(
            values=segment_counts.values,
            names=segment_counts.index,
            title="🎯 Customer Segment Distribution",
            color_discrete_sequence=colors,
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont_size=16, marker=dict(line=dict(color='#FFFFFF', width=3)))
        fig_pie.update_layout(title_font_size=18, font=dict(size=14), title_x=0.5, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, width='stretch')

    with col2:
        fig_hist = px.histogram(
            df,
            x='Win_Rate_%',
            nbins=20,
            title="📈 Win Rate Distribution",
            color='Customer_Segment',
            color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a'],
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
            yaxis=dict(gridcolor='lightgray'),
        )
        st.plotly_chart(fig_hist, width='stretch')

    fig_scatter = px.scatter(
        df,
        x='Win_Rate_%',
        y='CLV',
        size='Total_Quotations',
        color='Customer_Segment',
        hover_data=['ClientID', 'Projects_Per_Year', 'Retention_Rate', 'Churn_Rate'],
        title="💰 Customer Lifetime Value vs Win Rate",
        color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a'],
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
        yaxis=dict(gridcolor='lightgray'),
    )
    fig_scatter.update_traces(marker=dict(line=dict(width=2, color='white'), opacity=0.8))
    st.plotly_chart(fig_scatter, width='stretch')

    col3, col4 = st.columns(2)

    with col3:
        fig_retention = px.histogram(
            df,
            x='Retention_Rate',
            nbins=15,
            title="🎯 Customer Retention Rate Distribution",
            color='Customer_Segment',
            color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a'],
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
            yaxis=dict(gridcolor='lightgray'),
        )
        st.plotly_chart(fig_retention, width='stretch')

    with col4:
        top_services = df['Top_Service_by_Volume'].value_counts().head(10)
        fig_bar = px.bar(
            x=top_services.index,
            y=top_services.values,
            title="🌟 Most Popular Services",
            color=top_services.values,
            color_continuous_scale='Viridis',
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
            yaxis=dict(gridcolor='lightgray'),
        )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, width='stretch')

    st.subheader("📊 Project Analysis")
    col5, col6 = st.columns(2)

    with col5:
        fig_projects = px.histogram(
            df,
            x='Total_Quotations',
            nbins=20,
            title="📁 Projects per Customer Distribution",
            color='Customer_Segment',
            color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a'],
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
            yaxis=dict(gridcolor='lightgray'),
        )
        st.plotly_chart(fig_projects, width='stretch')

    with col6:
        fig_conversion = px.scatter(
            df,
            x='Total_Quotations',
            y='Converted_Quotations',
            color='Customer_Segment',
            size='CLV',
            title="🎯 Project Conversion Analysis",
            color_discrete_sequence=['#4facfe', '#43e97b', '#fa709a'],
            hover_data=['ClientID', 'Win_Rate_%'],
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
            yaxis=dict(gridcolor='lightgray'),
        )
        fig_conversion.add_trace(
            go.Scatter(
                x=[0, df['Total_Quotations'].max()],
                y=[0, df['Total_Quotations'].max()],
                mode='lines',
                line=dict(dash='dash', color='gray'),
                name='100% Conversion',
                showlegend=True,
            )
        )
        st.plotly_chart(fig_conversion, width='stretch')


