"""
State Street MF - Executive Dashboard
Live tracking of 29 prioritized mutual fund requirements
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import yaml
import os

# Import our custom modules
from jira_data_fetcher import fetch_all_jira_tickets, map_status_to_items
from excel_loader import load_prioritized_items, load_config

# Page config
st.set_page_config(
    page_title="State Street MF Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "State Street MF Dashboard - Executive Reporting"
    }
)

# Modern styling with better colors and layout
st.markdown("""
<style>
    /* Modern color scheme */
    :root {
        --primary-color: #0066cc;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
    }

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Metric cards styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }

    /* Make metric cards pop */
    [data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Header styling */
    h1 {
        color: #1e3a8a !important;
        font-weight: 700 !important;
        padding-bottom: 10px;
        border-bottom: 3px solid #0066cc;
    }

    h2 {
        color: #1e40af !important;
        font-weight: 600 !important;
        margin-top: 20px !important;
    }

    h3 {
        color: #3b82f6 !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Button styling */
    .stButton>button {
        background: linear-gradient(90deg, #0066cc 0%, #0052a3 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #0066cc 0%, #28a745 100%);
        height: 20px;
        border-radius: 10px;
    }

    /* Custom info boxes */
    .info-box {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 10px 0;
    }

    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
    }

    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
        border-left: 4px solid #ffc107;
    }

    .danger-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 4px solid #dc3545;
    }

    /* Feature tags */
    .feature-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 2px;
    }

    .tag-exchange { background: #e3f2fd; color: #1565c0; }
    .tag-drip { background: #f3e5f5; color: #6a1b9a; }
    .tag-pip { background: #e8f5e9; color: #2e7d32; }
    .tag-roa { background: #fff3e0; color: #e65100; }
</style>
""", unsafe_allow_html=True)

# Load config
config = load_config()

# Custom CSS
st.markdown("""
<style>
    .big-metric {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .status-green { color: #00c851; }
    .status-yellow { color: #ffbb33; }
    .status-red { color: #ff4444; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Sidebar
with st.sidebar:
    st.title("⚙️ Dashboard Settings")

    # Refresh button
    if st.button("🔄 Refresh Data", width="stretch"):
        st.cache_data.clear()
        st.session_state.last_refresh = datetime.now()
        st.rerun()

    st.caption(f"Last updated: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")

    st.divider()

    # Auth token input (for JIRA)
    auth_token = st.text_input(
        "JIRA Auth Token (Optional)",
        type="password",
        help="Enter your Atlassian API token for live data. Leave empty to use cached/demo data."
    )

    if auth_token:
        os.environ['JIRA_AUTH_TOKEN'] = auth_token

    st.divider()

    st.caption("**Dashboard Info:**")
    st.caption(f"📅 Q2 Deadline: {config['dashboard']['deadline']}")
    st.caption(f"🔄 Auto-refresh: {config['dashboard']['refresh_interval']}s")
    st.caption(f"📊 Total Items: 29")

# Main title with modern styling
st.markdown(f"""
<div style='text-align: center; padding: 20px 0;'>
    <h1 style='font-size: 2.5rem; margin: 0;'>📊 {config['dashboard']['title']}</h1>
    <p style='font-size: 1.1rem; color: #6b7280; margin-top: 10px;'>
        Real-time tracking of 29 prioritized mutual fund platform requirements
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Load data with caching
@st.cache_data(ttl=config['dashboard']['refresh_interval'])
def load_dashboard_data(_auth_token=None):
    """Load and combine Excel + JIRA data"""
    # Load Excel
    excel_data = load_prioritized_items()

    # Fetch JIRA status
    jira_statuses = fetch_all_jira_tickets(_auth_token)

    # Map to items
    dashboard_data = map_status_to_items(excel_data, jira_statuses)

    return dashboard_data, jira_statuses

# Load data
try:
    data, jira_info = load_dashboard_data(auth_token if auth_token else None)
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Calculate metrics
total_items = len(data)
completed = len(data[data['Live Status'].isin(['Done', 'Closed'])])
in_progress = len(data[data['Live Status'].isin(['In Build', 'In Progress', 'In Development'])])
not_started = len(data[data['Live Status'].isin(['Proposed', 'Not Started', 'To Do', 'Backlog'])])
unknown = len(data[data['Live Status'].isin(['Unknown', 'Error'])])

# Calculate days to deadline
deadline = datetime.strptime(config['dashboard']['deadline'], '%Y-%m-%d').date()
days_left = (deadline - date.today()).days

# Progress percentage
progress = completed / total_items if total_items > 0 else 0

# ========== SECTION 1: EXECUTIVE SUMMARY ==========
st.header("📈 Executive Summary")

# KPI Cards with enhanced styling
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div class='info-box' style='text-align: center;'>
        <div style='font-size: 3rem;'>📋</div>
        <div style='font-size: 2rem; font-weight: bold; color: #1e3a8a;'>{}</div>
        <div style='color: #6b7280;'>Total Items</div>
    </div>
    """.format(total_items), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='info-box success-box' style='text-align: center;'>
        <div style='font-size: 3rem;'>✅</div>
        <div style='font-size: 2rem; font-weight: bold; color: #28a745;'>{}</div>
        <div style='color: #155724;'>Completed</div>
        <div style='font-size: 0.9rem; color: #155724; margin-top: 5px;'>{:.1f}%</div>
    </div>
    """.format(completed, progress*100), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='info-box warning-box' style='text-align: center;'>
        <div style='font-size: 3rem;'>⚡</div>
        <div style='font-size: 2rem; font-weight: bold; color: #ff9800;'>{}</div>
        <div style='color: #856404;'>In Progress</div>
    </div>
    """.format(in_progress), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='info-box danger-box' style='text-align: center;'>
        <div style='font-size: 3rem;'>⏳</div>
        <div style='font-size: 2rem; font-weight: bold; color: #dc3545;'>{}</div>
        <div style='color: #721c24;'>Not Started</div>
    </div>
    """.format(not_started), unsafe_allow_html=True)

with col5:
    days_color = "#28a745" if days_left > 30 else "#ffc107" if days_left > 14 else "#dc3545"
    st.markdown("""
    <div class='info-box' style='text-align: center; border-left: 4px solid {};'>
        <div style='font-size: 3rem;'>📅</div>
        <div style='font-size: 2rem; font-weight: bold; color: {};'>{}</div>
        <div style='color: #6b7280;'>Days to Q2</div>
        <div style='font-size: 0.85rem; color: #6b7280; margin-top: 5px;'>June 30, 2026</div>
    </div>
    """.format(days_color, days_color, days_left), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Enhanced progress bar
st.markdown(f"""
<div class='info-box'>
    <h3 style='margin: 0 0 10px 0;'>Overall Progress</h3>
    <div style='background: #e9ecef; border-radius: 10px; overflow: hidden;'>
        <div style='
            width: {progress*100}%;
            background: linear-gradient(90deg, #0066cc 0%, #28a745 100%);
            height: 30px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 1s ease;
        '>
            {progress*100:.1f}%
        </div>
    </div>
    <p style='text-align: center; margin-top: 10px; color: #6b7280;'>
        {completed} of {total_items} items completed
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Charts
col1, col2 = st.columns(2)

with col1:
    # Status distribution - Modern donut chart
    status_counts = data['Live Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']

    fig = go.Figure(data=[go.Pie(
        labels=status_counts['Status'],
        values=status_counts['Count'],
        hole=0.4,
        marker=dict(
            colors=['#28a745', '#28a745', '#ff9800', '#ff9800', '#dc3545', '#dc3545', '#cccccc'],
            line=dict(color='white', width=2)
        ),
        textinfo='label+percent',
        textfont=dict(size=14, color='white'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title={
            'text': "📊 Status Distribution",
            'font': {'size': 20, 'color': '#1e3a8a', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=True,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )

    st.plotly_chart(fig, width="stretch", key="status_pie")

with col2:
    # Priority breakdown - Modern grouped bar chart
    priority_status = data.groupby(['Priority', 'Live Status']).size().reset_index(name='Count')

    fig = px.bar(
        priority_status,
        x='Priority',
        y='Count',
        color='Live Status',
        title="📈 Progress by Priority",
        barmode='group',
        labels={'Priority': 'Priority Level', 'Count': 'Number of Items'},
        color_discrete_map={
            'Done': '#28a745',
            'Closed': '#28a745',
            'In Build': '#ff9800',
            'In Progress': '#ff9800',
            'Proposed': '#dc3545',
            'Not Started': '#dc3545',
            'Unknown': '#cccccc'
        },
        text='Count'
    )

    fig.update_layout(
        title_font=dict(size=20, color='#1e3a8a', family='Arial Black'),
        title_x=0.5,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title_font=dict(size=14, color='#1e3a8a'),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title_font=dict(size=14, color='#1e3a8a'),
            tickfont=dict(size=12),
            gridcolor='#e9ecef'
        )
    )

    fig.update_traces(textposition='outside')

    st.plotly_chart(fig, width="stretch", key="priority_bar")

# Feature Area breakdown
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='info-box'>", unsafe_allow_html=True)
st.subheader("🎯 Progress by Feature Area")

feature_summary = data.groupby(['Feature Area', 'Live Status']).size().reset_index(name='Count')

fig = px.bar(
    feature_summary,
    x='Feature Area',
    y='Count',
    color='Live Status',
    title="",
    barmode='stack',
    color_discrete_map={
        'Done': '#28a745',
        'Closed': '#28a745',
        'In Build': '#ff9800',
        'In Progress': '#ff9800',
        'Proposed': '#dc3545',
        'Not Started': '#dc3545',
        'Unknown': '#cccccc'
    },
    text='Count'
)

fig.update_layout(
    height=350,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        title="",
        title_font=dict(size=14, color='#1e3a8a'),
        tickfont=dict(size=12, color='#374151'),
        tickangle=-45
    ),
    yaxis=dict(
        title="Number of Items",
        title_font=dict(size=14, color='#1e3a8a'),
        tickfont=dict(size=12),
        gridcolor='#e9ecef'
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

fig.update_traces(textposition='inside')

st.plotly_chart(fig, width="stretch", key="feature_bar")
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ========== SECTION 2: DETAILED STATUS TABLE ==========
st.header("📋 Detailed Status - All 29 Items")

# Filters with better styling
st.markdown("<div class='info-box'>", unsafe_allow_html=True)
st.subheader("🔍 Filter Items")

col1, col2, col3, col4 = st.columns(4)

with col1:
    priority_filter = st.multiselect(
        "📌 Priority",
        options=sorted(data['Priority'].dropna().unique().tolist()),
        default=sorted(data['Priority'].dropna().unique().tolist()),
        key="priority_filter"
    )

with col2:
    feature_areas = [fa for fa in data['Feature Area'].unique().tolist() if fa != 'Unknown']
    feature_filter = st.multiselect(
        "🎯 Feature Area",
        options=sorted(feature_areas),
        default=sorted(feature_areas),
        key="feature_filter"
    )

with col3:
    all_statuses = data['Live Status'].unique().tolist()
    status_filter = st.multiselect(
        "📊 Status",
        options=all_statuses,
        default=all_statuses,
        key="status_filter"
    )

with col4:
    # Search box
    search_term = st.text_input(
        "🔎 Search Functionality",
        placeholder="Type to search...",
        key="search_box"
    )

st.markdown("</div>", unsafe_allow_html=True)

# Apply filters
filtered_data = data.copy()

if priority_filter:
    filtered_data = filtered_data[filtered_data['Priority'].isin(priority_filter)]

if feature_filter:
    filtered_data = filtered_data[filtered_data['Feature Area'].isin(feature_filter)]

if status_filter:
    filtered_data = filtered_data[filtered_data['Live Status'].isin(status_filter)]

if search_term:
    filtered_data = filtered_data[
        filtered_data['Functionality'].str.contains(search_term, case=False, na=False)
    ]

st.markdown(f"""
<div style='background: linear-gradient(90deg, #0066cc 0%, #0052a3 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            margin: 15px 0;
            font-size: 1.1rem;
            font-weight: 600;'>
    📋 Showing {len(filtered_data)} of {total_items} items
</div>
""", unsafe_allow_html=True)

# Display table with better styling
display_cols = [
    'Status Color',
    'Functionality',
    'Category',
    'Sub Category',
    'Priority',
    'Live Status',
    'Feature Area',
    'JIRA Ticket #'
]

# Create a copy for display
display_df = filtered_data[display_cols].copy()

# Apply row styling based on priority
def style_priority(row):
    if row['Priority'] == 1:
        return ['background-color: #fff3cd'] * len(row)
    return [''] * len(row)

st.markdown("<div class='info-box'>", unsafe_allow_html=True)

# Show the dataframe with enhanced config
st.dataframe(
    display_df,
    width="stretch",
    hide_index=True,
    height=500,
    column_config={
        "Status Color": st.column_config.TextColumn("", width="small"),
        "Functionality": st.column_config.TextColumn("Functionality", width="large"),
        "Category": st.column_config.TextColumn("Category", width="medium"),
        "Sub Category": st.column_config.TextColumn("Sub Category", width="medium"),
        "Priority": st.column_config.NumberColumn("Priority", width="small"),
        "Live Status": st.column_config.TextColumn("JIRA Status", width="medium"),
        "Feature Area": st.column_config.TextColumn("Feature", width="medium"),
        "JIRA Ticket #": st.column_config.LinkColumn(
            "JIRA Link",
            width="medium",
            display_text=r"View Ticket"
        )
    }
)

st.markdown("</div>", unsafe_allow_html=True)

# JIRA ticket links section
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("🔗 Quick Links to JIRA Feature Tickets")

cols = st.columns(4)
for idx, (ticket, info) in enumerate(jira_info.items()):
    with cols[idx % 4]:
        # Determine status color
        status_emoji = "🟢" if info['status'] in ['Done', 'Closed'] else "🟡" if info['status'] in ['In Build', 'In Progress'] else "🔴"

        st.markdown(f"""
        <div class='info-box' style='text-align: center; min-height: 150px; display: flex; flex-direction: column; justify-content: center;'>
            <div style='font-size: 2rem; margin-bottom: 10px;'>{status_emoji}</div>
            <a href='https://apexclearing.atlassian.net/browse/{ticket}'
               target='_blank'
               style='font-size: 1.2rem; font-weight: bold; color: #0066cc; text-decoration: none;'>
                {ticket}
            </a>
            <div style='margin-top: 10px; color: #6b7280; font-size: 0.9rem;'>
                {info['status']}
            </div>
            <div style='color: #9ca3af; font-size: 0.85rem; margin-top: 5px;'>
                👤 {info['assignee']}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ========== SECTION 3: TIMELINE & RISKS ==========
st.header("⏰ Timeline & Risk Indicators")

col1, col2 = st.columns([1, 1])

with col1:
    # On-track indicator
    days_elapsed = (date.today() - date(2026, 4, 1)).days
    total_q2_days = (deadline - date(2026, 4, 1)).days
    expected_progress = days_elapsed / total_q2_days if total_q2_days > 0 else 0

    if progress >= expected_progress:
        track_status = "🟢 On Track"
        track_color = "#28a745"
        box_class = "success-box"
    elif progress >= expected_progress * 0.8:
        track_status = "🟡 At Risk"
        track_color = "#ffc107"
        box_class = "warning-box"
    else:
        track_status = "🔴 Behind Schedule"
        track_color = "#dc3545"
        box_class = "danger-box"

    st.markdown(f"""
    <div class='info-box {box_class}'>
        <h3 style='margin: 0 0 15px 0;'>📅 Q2 Deadline Tracker</h3>
        <div style='text-align: center; font-size: 2.5rem; margin: 20px 0;'>
            {track_status}
        </div>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px;'>
            <div style='text-align: center; padding: 15px; background: rgba(255,255,255,0.6); border-radius: 8px;'>
                <div style='font-size: 0.9rem; color: #6b7280;'>Expected Progress</div>
                <div style='font-size: 1.8rem; font-weight: bold; color: {track_color};'>{expected_progress*100:.1f}%</div>
            </div>
            <div style='text-align: center; padding: 15px; background: rgba(255,255,255,0.6); border-radius: 8px;'>
                <div style='font-size: 0.9rem; color: #6b7280;'>Actual Progress</div>
                <div style='font-size: 1.8rem; font-weight: bold; color: {track_color};'>{progress*100:.1f}%</div>
            </div>
        </div>
        <div style='text-align: center; margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.6); border-radius: 8px;'>
            <div style='font-size: 0.9rem; color: #6b7280;'>Variance</div>
            <div style='font-size: 1.5rem; font-weight: bold; color: {track_color};'>
                {(progress-expected_progress)*100:+.1f}%
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='info-box warning-box'>
        <h3 style='margin: 0 0 15px 0;'>⚠️ Known Risks & Dependencies</h3>

        <div style='background: rgba(255,255,255,0.7); padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <div style='font-weight: bold; color: #856404; margin-bottom: 8px; font-size: 1.1rem;'>
                🚨 Resource Constraints
            </div>
            <div style='color: #856404; margin-left: 15px;'>
                • Orders team understaffed (only 3 people)<br>
                • Managing trading, orders, and executions<br>
                • <strong>Impact:</strong> ASC-14277 (Exchange Orders)
            </div>
        </div>

        <div style='background: rgba(255,255,255,0.7); padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <div style='font-weight: bold; color: #856404; margin-bottom: 8px; font-size: 1.1rem;'>
                🔗 High Dependency Risk
            </div>
            <div style='color: #856404; margin-left: 15px;'>
                • Exchange orders have multiple dependencies<br>
                • Potential delays in implementation
            </div>
        </div>

        <div style='background: rgba(255,255,255,0.7); padding: 15px; border-radius: 8px;'>
            <div style='font-weight: bold; color: #856404; margin-bottom: 8px; font-size: 1.1rem;'>
                🎨 UI Priority Concerns
            </div>
            <div style='color: #856404; margin-left: 15px;'>
                • MF ranked 10th in wealth platform priorities<br>
                • UI delays anticipated for front-end work
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-top: 30px;'>
    <div style='font-size: 1.1rem; font-weight: 600; margin-bottom: 10px;'>
        💡 Dashboard Tips
    </div>
    <div style='font-size: 0.95rem; opacity: 0.9;'>
        • Click JIRA ticket numbers to view detailed requirements<br>
        • Use filters to focus on specific priorities or feature areas<br>
        • Dashboard auto-refreshes every {} minutes | Click 🔄 to refresh manually<br>
        • For live JIRA status, enter your API token in the sidebar
    </div>
    <div style='margin-top: 15px; font-size: 0.85rem; opacity: 0.7;'>
        State Street MF Dashboard | Built with Streamlit | Last Updated: {}
    </div>
</div>
""".format(
    config['dashboard']['refresh_interval'] // 60,
    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
), unsafe_allow_html=True)
