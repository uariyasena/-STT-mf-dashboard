"""
State Street MF - Executive Dashboard (Corporate Style)
Clean, minimal design matching corporate standards
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# Import our custom modules
from jira_data_fetcher import fetch_all_jira_tickets, map_status_to_items
from excel_loader import load_prioritized_items, load_config

# Page config
st.set_page_config(
    page_title="State Street MF Status Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Corporate styling - clean and minimal
st.markdown("""
<style>
    /* Remove default padding */
    .stApp {
        background-color: #f8f9fa;
    }

    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }

    /* Navy header bar */
    .header-bar {
        background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 20px 40px;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .header-title {
        font-size: 1.8rem;
        font-weight: 600;
        margin: 0;
        color: white;
    }

    .header-date {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-top: 5px;
    }

    /* Metric cards - simple bordered boxes */
    .metric-card {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .metric-label {
        font-size: 0.85rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        line-height: 1;
    }

    /* Status bar - horizontal colored segments */
    .status-bar-container {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        padding: 15px;
        margin-bottom: 20px;
    }

    .status-bar {
        display: flex;
        height: 30px;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 10px;
    }

    .status-segment {
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* Color scheme matching reference */
    .status-done { background-color: #28a745; }
    .status-progress { background-color: #ffc107; }
    .status-todo { background-color: #fd7e14; }
    .status-notstarted { background-color: #dc3545; }

    /* Panel boxes */
    .panel-box {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .panel-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #e9ecef;
    }

    /* Table styling */
    .dataframe {
        font-size: 0.9rem;
    }

    thead tr th {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #dee2e6 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: white;
        border-bottom: 2px solid #dee2e6;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        color: #495057;
        padding: 10px 24px;
        font-weight: 500;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #2c3e50;
        border-bottom: 3px solid #0066cc;
    }

    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Load config
config = load_config()

# Header Bar
st.markdown(f"""
<div class="header-bar">
    <div class="header-title">State Street MF - Status Tracker</div>
    <div class="header-date">Data Updated: {datetime.now().strftime('%B %d, %Y')}</div>
</div>
""", unsafe_allow_html=True)

# Load data
@st.cache_data(ttl=300)
def load_dashboard_data():
    excel_data = load_prioritized_items()
    jira_statuses = fetch_all_jira_tickets()
    dashboard_data = map_status_to_items(excel_data, jira_statuses)
    return dashboard_data, jira_statuses

data, jira_info = load_dashboard_data()

# Calculate metrics
total_items = len(data)
completed = len(data[data['Live Status'].isin(['Done', 'Closed'])])
in_progress = len(data[data['Live Status'].isin(['In Build', 'In Progress', 'In Development'])])
not_started = len(data[data['Live Status'].isin(['Proposed', 'Not Started', 'To Do', 'Backlog'])])
todo = len(data[data['Live Status'] == 'To Do'])

# Top Metrics Row
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Items</div>
        <div class="metric-value">{total_items}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #6c757d;">
        <div class="metric-label">Backlog</div>
        <div class="metric-value" style="color: #6c757d;">{not_started}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #28a745;">
        <div class="metric-label">Done</div>
        <div class="metric-value" style="color: #28a745;">{completed}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #ffc107;">
        <div class="metric-label">In Progress</div>
        <div class="metric-value" style="color: #ffc107;">{in_progress}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #fd7e14;">
        <div class="metric-label">To Do</div>
        <div class="metric-value" style="color: #fd7e14;">{todo}</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    deadline = datetime.strptime(config['dashboard']['deadline'], '%Y-%m-%d').date()
    days_left = (deadline - date.today()).days
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #dc3545;">
        <div class="metric-label">Days to Q2</div>
        <div class="metric-value" style="color: #dc3545;">{days_left}</div>
    </div>
    """, unsafe_allow_html=True)

# Status Bar
completed_pct = (completed / total_items * 100) if total_items > 0 else 0
progress_pct = (in_progress / total_items * 100) if total_items > 0 else 0
todo_pct = (todo / total_items * 100) if total_items > 0 else 0
notstarted_pct = (not_started / total_items * 100) if total_items > 0 else 0

st.markdown(f"""
<div class="status-bar-container">
    <div style="font-weight: 600; color: #2c3e50; margin-bottom: 5px;">Overall Progress</div>
    <div class="status-bar">
        <div class="status-segment status-done" style="width: {completed_pct}%;">
            {completed} Done
        </div>
        <div class="status-segment status-progress" style="width: {progress_pct}%;">
            {in_progress} In Progress
        </div>
        <div class="status-segment status-todo" style="width: {todo_pct}%;">
            {todo} To Do
        </div>
        <div class="status-segment status-notstarted" style="width: {notstarted_pct}%;">
            {not_started} Not Started
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Deliverables", "📊 Status Tracker", "📈 Change Report"])

with tab1:
    # Two column layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div class="panel-box">
            <div class="panel-title">Weekly Update - Apr 21-27</div>
            <div style="line-height: 1.8;">
                <strong style="color: #2c3e50;">Needs Attention (5)</strong> - Overdue, late blockers, and workflow items<br>
                <div style="margin-left: 20px; margin-top: 10px; color: #495057;">
                    • <strong>ASC-14277:</strong> Exchange Orders - Resource constraints (3 people on orders team)<br>
                    • <strong>ASC-21778:</strong> PIP/SWIP - Dependencies on MFRS integration<br>
                    • <strong>ASC-21779:</strong> DRIP - Waiting on Network Master setup<br>
                    • <strong>ROA/LOI:</strong> Breakpoint calculation complexity<br>
                    • <strong>UI Delays:</strong> MF ranked 10th in platform priorities
                </div>
                <br>
                <strong style="color: #2c3e50;">ASC-9915:</strong> Product Onboarding Experience Director UAT<br>
                <div style="margin-left: 20px; color: #495057;">State Street UAT ongoing - 7 items in testing</div>
                <br>
                <strong style="color: #2c3e50;">ASC-10948:</strong> Onboarding/Onboarding Business in Tech²<br>
                <div style="margin-left: 20px; color: #495057;">Documentation and compliance workflows in progress</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="panel-box">
            <div class="panel-title">Timing Summary - Q2 2026</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 4px;">
                    <div style="font-size: 1.8rem; font-weight: 700; color: #28a745;">{completed}</div>
                    <div style="font-size: 0.85rem; color: #6c757d;">DELIVERED</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 4px;">
                    <div style="font-size: 1.8rem; font-weight: 700; color: #ffc107;">{in_progress}</div>
                    <div style="font-size: 0.85rem; color: #6c757d;">IN PROGRESS</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 4px;">
                    <div style="font-size: 1.8rem; font-weight: 700; color: #fd7e14;">{todo}</div>
                    <div style="font-size: 0.85rem; color: #6c757d;">UPCOMING</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 4px;">
                    <div style="font-size: 1.8rem; font-weight: 700; color: #dc3545;">{not_started}</div>
                    <div style="font-size: 0.85rem; color: #6c757d;">AT RISK</div>
                </div>
            </div>
            <div style="line-height: 1.8; color: #495057;">
                <strong>Needs Attention (3):</strong> Capability trade-offs (1/2 TSG complexity)<br>
                <div style="margin-left: 20px; margin-top: 10px;">
                    • <strong>ASSERT:</strong> Cash Sweep Redemption Accounting<br>
                    • <strong>JET:</strong> Launch Our Advisor Web Portal<br>
                    • <strong>JAS:</strong> Advisor Onboarding
                </div>
                <br>
                <strong>DGRAY:</strong> Get Faster WR Service<br>
                <div style="margin-left: 20px;">Q2 delivery on track | Due: June 30, 2026</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>All Deliverables (29 Items)</div>", unsafe_allow_html=True)

    # Simple table view
    display_df = data[[
        'Functionality',
        'Category',
        'Priority',
        'Live Status',
        'Feature Area',
        'JIRA Ticket #'
    ]].copy()

    # Add status emoji
    def status_emoji(status):
        if status in ['Done', 'Closed']:
            return '🟢'
        elif status in ['In Build', 'In Progress']:
            return '🟡'
        elif status in ['To Do']:
            return '🟠'
        else:
            return '🔴'

    display_df.insert(0, '', display_df['Live Status'].apply(status_emoji))

    st.dataframe(
        display_df,
        height=600,
        width=None,
        hide_index=True,
        column_config={
            "": st.column_config.TextColumn("", width="small"),
            "Functionality": st.column_config.TextColumn("Functionality", width="large"),
            "Category": st.column_config.TextColumn("Category", width="medium"),
            "Priority": st.column_config.NumberColumn("Pri", width="small"),
            "Live Status": st.column_config.TextColumn("Status", width="medium"),
            "Feature Area": st.column_config.TextColumn("Feature", width="medium"),
            "JIRA Ticket #": st.column_config.LinkColumn(
                "JIRA",
                width="small",
                display_text="View"
            )
        }
    )

    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>Recent Changes & Updates</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="line-height: 2;">
        <div style="padding: 15px; background: #f8f9fa; border-left: 4px solid #28a745; margin-bottom: 10px; border-radius: 4px;">
            <strong>April 22, 2026:</strong> Dashboard launched with live JIRA integration
        </div>
        <div style="padding: 15px; background: #f8f9fa; border-left: 4px solid #ffc107; margin-bottom: 10px; border-radius: 4px;">
            <strong>April 17, 2026:</strong> Working session completed - 29 items prioritized (7 P1, 22 P2)
        </div>
        <div style="padding: 15px; background: #f8f9fa; border-left: 4px solid #0066cc; margin-bottom: 10px; border-radius: 4px;">
            <strong>April 16, 2026:</strong> JIRA tickets created under ASC-21760 initiative
        </div>
        <div style="padding: 15px; background: #f8f9fa; border-left: 4px solid #6c757d; margin-bottom: 10px; border-radius: 4px;">
            <strong>March 2026:</strong> State Street UAT started in Wealth Workstation
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="margin-top: 40px; padding: 15px; background: white; border-top: 2px solid #dee2e6; text-align: center; color: #6c757d; font-size: 0.85rem;">
    State Street MF Status Tracker | Auto-refreshes every 5 minutes |
    <a href="https://apexclearing.atlassian.net/browse/ASC-21760" target="_blank" style="color: #0066cc;">View ASC-21760</a>
</div>
""", unsafe_allow_html=True)
