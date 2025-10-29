# Customer Retention Analytics Dashboard

A powerful, interactive Streamlit dashboard for analyzing customer quotation data, retention metrics, and service revenue.

## Features

- 📊 **Customer Analytics**: CLV, Win Rate, Retention Rate, Churn analysis
- 🎯 **Customer Segmentation**: High/Medium/Low value customer classification
- 💰 **Service Revenue Analysis**: Per-service totals and averages
- 🔍 **Hierarchical Navigation**: Country → Company → Customer drill-down
- 📈 **Interactive Visualizations**: Charts, graphs, and exportable reports
- 📥 **CSV Export**: Download processed analytics

## Deployment (Streamlit Community Cloud)

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub repo, select `app.py` as the entrypoint
4. Click Deploy

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Data Format

Upload a CSV file with the following columns:
- `Date`: Quote date (DD/MM/YYYY)
- `Number`: Quote number (e.g., KSA.Abb.QU.1002.1)
- `ClientID`: Unique client identifier
- `Estimate status`: "Closed" or "Rejected"
- `Taxable amount`: Quote value
- `converted to invoice (AMOUNT)`: Converted amount
- Service columns: CME, Design, Med Com, Multichannel, Onsite Support, Other Services, Video, Webinars, Websites

## Security Note

⚠️ **Important**: If deploying publicly, do NOT commit sensitive customer data to GitHub. Use the file uploader feature in the app instead.

## License

Proprietary - Internal Use Only
