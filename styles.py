import streamlit as st


def set_page():
    st.set_page_config(
        page_title="Customer Analytics Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_css():
    st.markdown(
        """
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
    .metric-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 1.5rem; border-radius: 12px; text-align: center; margin: 0.5rem 0; box-shadow: 0 4px 15px 0 rgba(31, 38, 135, 0.2); transform: translateY(0px); transition: transform 0.3s ease; }
    .metric-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px 0 rgba(31, 38, 135, 0.3); }
    .high-value { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important; color: white !important; font-weight: bold; padding: 0.5rem; border-radius: 8px; text-align: center; animation: glow 2s ease-in-out infinite alternate; }
    .medium-value { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important; color: white !important; font-weight: bold; padding: 0.5rem; border-radius: 8px; text-align: center; }
    .low-value { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%) !important; color: white !important; font-weight: bold; padding: 0.5rem; border-radius: 8px; text-align: center; }
    .retention-high { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; padding: 0.8rem; border-radius: 10px; border-left: 5px solid #00ff88; font-weight: bold; box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3); }
    .retention-medium { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%) !important; color: #333 !important; padding: 0.8rem; border-radius: 10px; border-left: 5px solid #ffaa00; font-weight: bold; box-shadow: 0 4px 15px rgba(255, 170, 0, 0.3); }
    .retention-low { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%) !important; color: #333 !important; padding: 0.8rem; border-radius: 10px; border-left: 5px solid #ff4757; font-weight: bold; box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3); }
    .customer-highlight { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; box-shadow: 0 8px 32px 0 rgba(102, 126, 234, 0.37); border: 2px solid rgba(255, 255, 255, 0.2); }
    .stats-container { background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.2) 100%); backdrop-filter: blur(10px); padding: 1.5rem; border-radius: 15px; border: 1px solid rgba(255,255,255,0.2); margin: 1rem 0; }
    @keyframes glow { from { box-shadow: 0 0 5px #4facfe, 0 0 10px #4facfe, 0 0 15px #4facfe; } to { box-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe, 0 0 30px #00f2fe; } }
    .stDataFrame { border: 2px solid transparent; border-radius: 12px; background: linear-gradient(white, white) padding-box, linear-gradient(135deg, #667eea, #764ba2) border-box; }
    .sidebar-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem; }
    .success-highlight { background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%); color: white; padding: 1rem; border-radius: 10px; text-align: center; font-weight: bold; margin: 1rem 0; }
    .warning-highlight { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 1rem; border-radius: 10px; text-align: center; font-weight: bold; margin: 1rem 0; }
</style>
        """,
        unsafe_allow_html=True,
    )


