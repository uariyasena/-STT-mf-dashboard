"""
State Street MF - Executive Dashboard
Clean, corporate style with innovative visualizations
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import os

# Import our custom modules
from jira_data_fetcher import fetch_all_jira_tickets, map_status_to_items
from excel_loader import load_prioritized_items, load_config

# Page config
st.set_page_config(
    page_title="State Street MF Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern, clean corporate styling
st.markdown("""
<style>
    /* Clean background */
    .stApp {
        background-color: #ffffff;
    }

    .block-container {
        padding-top: 1rem;
        max-width: 95%;
    }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 30px 40px;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Feature cards with hover effect */
    .feature-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 25px;
        margin: 10px 0;
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .feature-card:hover {
        border-color: #3b82f6;
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.2);
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    }

    /* Metric card with circular progress */
    .metric-circle {
        text-align: center;
        padding: 20px;
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
    }

    .badge-done { background: #d1fae5; color: #065f46; }
    .badge-progress { background: #fef3c7; color: #92400e; }
    .badge-todo { background: #fed7aa; color: #9a3412; }
    .badge-blocked { background: #fee2e2; color: #991b1b; }

    /* Timeline item */
    .timeline-item {
        padding: 15px;
        border-left: 3px solid #e5e7eb;
        margin-left: 20px;
        position: relative;
    }

    .timeline-item::before {
        content: '';
        position: absolute;
        left: -8px;
        top: 20px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #3b82f6;
        border: 2px solid white;
    }

    .timeline-item.done::before { background: #10b981; }
    .timeline-item.progress::before { background: #f59e0b; }
    .timeline-item.blocked::before { background: #ef4444; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: #f3f4f6;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 500;
        color: #6b7280;
    }

    .stTabs [aria-selected="true"] {
        background: white;
        color: #1e3a8a;
        box-shadow: 0 -2px 4px rgba(0,0,0,0.05);
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }

    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
""", unsafe_allow_html=True)

# Load config
config = load_config()

# Load data
@st.cache_data(ttl=300)
def load_dashboard_data():
    excel_data = load_prioritized_items()
    jira_statuses = fetch_all_jira_tickets()
    dashboard_data = map_status_to_items(excel_data, jira_statuses)
    return dashboard_data, jira_statuses

data, jira_info = load_dashboard_data()

# Calculate metrics first
total_items = len(data)
completed = len(data[data['Live Status'].isin(['Done', 'Closed'])])
in_progress = len(data[data['Live Status'].isin(['In Build', 'In Progress', 'In Development'])])
to_do = len(data[data['Live Status'].isin(['Proposed', 'To Do'])])
not_started = len(data[data['Live Status'].isin(['Not Started', 'Backlog'])])
progress_pct = (completed / total_items * 100) if total_items > 0 else 0

# Header
st.markdown(f"""<div class="main-header"><div><h1 style='margin: 0; font-size: 2rem; font-weight: 700;'>State Street Mutual Funds</h1><p style='margin: 5px 0 0 0; opacity: 0.9; font-size: 1.1rem;'>Delivery Tracker <span style='display: inline-block; margin-left: 8px; padding: 4px 12px; background: rgba(255,255,255,0.2); border-radius: 20px; font-size: 0.9rem; font-weight: 600;'>📦 {total_items} Items</span></p></div></div>""", unsafe_allow_html=True)

# Circular progress indicators
col1, col2, col3, col4 = st.columns(4)

def create_gauge_chart(value, max_value, title, color):
    """Create a circular gauge chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 14, 'color': '#374151'}},
        number = {'font': {'size': 32, 'color': '#1f2937'}},
        gauge = {
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "#e5e7eb"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e5e7eb",
            'steps': [
                {'range': [0, max_value], 'color': '#f3f4f6'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))

    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#374151", 'family': "Arial"}
    )
    return fig

with col1:
    fig = create_gauge_chart(completed, total_items, "✅ Completed", "#10b981")
    st.plotly_chart(fig, use_container_width=True, key="gauge1")

with col2:
    fig = create_gauge_chart(in_progress, total_items, "🔨 In Progress", "#f59e0b")
    st.plotly_chart(fig, use_container_width=True, key="gauge2")

with col3:
    fig = create_gauge_chart(to_do, total_items, "📋 To Do", "#3b82f6")
    st.plotly_chart(fig, use_container_width=True, key="gauge3")

with col4:
    fig = create_gauge_chart(not_started, total_items, "⏸️ Not Started", "#ef4444")
    st.plotly_chart(fig, use_container_width=True, key="gauge4")

st.markdown("<br>", unsafe_allow_html=True)

# Feature Area Cards
st.subheader("🎯 Feature Areas")

# Group by feature area
feature_summary = data.groupby('Feature Area').agg({
    'Functionality': 'count',
    'Live Status': lambda x: (x.isin(['Done', 'Closed'])).sum()
}).reset_index()
feature_summary.columns = ['Feature Area', 'Total', 'Completed']
feature_summary['Progress'] = (feature_summary['Completed'] / feature_summary['Total'] * 100).round(1)

# Create interactive feature cards
cols = st.columns(4)

feature_colors = {
    'Exchange': {'color': '#3b82f6', 'icon': '🔄', 'ticket': 'ASC-14277'},
    'DRIP': {'color': '#8b5cf6', 'icon': '💧', 'ticket': 'ASC-21779'},
    'PIP/SWIP': {'color': '#10b981', 'icon': '📈', 'ticket': 'ASC-21778'},
    'ROA/LOI': {'color': '#f59e0b', 'icon': '🎯', 'ticket': 'ASC-21783'}
}

# Filter to only show the 4 main feature areas (exclude "Other")
main_features = feature_summary[feature_summary['Feature Area'].isin(feature_colors.keys())]

# Ensure we show all 4 in the correct order
feature_order = ['Exchange', 'DRIP', 'PIP/SWIP', 'ROA/LOI']

for idx, feature_name in enumerate(feature_order):
    col = cols[idx]
    # Get data for this feature (or use zeros if not found)
    feature_data = main_features[main_features['Feature Area'] == feature_name]

    # Get data for this feature (or use defaults if not found)
    if len(feature_data) > 0:
        total = int(feature_data.iloc[0]['Total'])
        completed = int(feature_data.iloc[0]['Completed'])
        progress = float(feature_data.iloc[0]['Progress'])
    else:
        total = 0
        completed = 0
        progress = 0.0

    info = feature_colors[feature_name]
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div style='font-size: 2.5rem; margin-bottom: 10px;'>{info['icon']}</div>
            <h3 style='margin: 0; color: #1f2937; font-size: 1.1rem;'>{feature_name}</h3>
            <div style='margin: 15px 0;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                    <span style='color: #6b7280; font-size: 0.9rem;'>Progress</span>
                    <span style='color: {info["color"]}; font-weight: 700;'>{progress:.1f}%</span>
                </div>
                <div style='background: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden;'>
                    <div style='background: {info["color"]}; height: 100%; width: {progress}%; transition: width 1s;'></div>
                </div>
            </div>
            <div style='display: flex; justify-content: space-between; color: #6b7280; font-size: 0.85rem;'>
                <span>{completed}/{total} Items</span>
                <a href='https://apexclearing.atlassian.net/browse/{info["ticket"]}'
                   target='_blank'
                   style='color: {info["color"]}; text-decoration: none; font-weight: 600;'>
                    {info["ticket"]} →
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs with different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard View", "📋 Kanban Board", "📅 Timeline", "📈 Analytics"])

with tab1:
    # Priority breakdown with visual cards
    st.subheader("Priority Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Priority 1 (Critical)")
        p1_items = data[data['Priority'] == 1]

        for _, item in p1_items.iterrows():
            status_class = "done" if item['Live Status'] in ['Done', 'Closed'] else "progress" if item['Live Status'] in ['In Build', 'In Progress'] else "blocked"
            badge_class = f"badge-{status_class}"

            st.markdown(f"""
            <div class="timeline-item {status_class}">
                <div style='font-weight: 600; color: #1f2937; margin-bottom: 5px;'>{item['Functionality']}</div>
                <div style='font-size: 0.85rem; color: #6b7280; margin-bottom: 8px;'>{item['Category']}</div>
                <div>
                    <span class="status-badge {badge_class}">{item['Live Status']}</span>
                    {f"<span class='status-badge' style='background: #dbeafe; color: #1e40af;'>{item['JIRA Ticket #']}</span>" if pd.notna(item['JIRA Ticket #']) else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### Priority 2 (High)")
        p2_items = data[data['Priority'] == 2].head(7)  # Show first 7

        for _, item in p2_items.iterrows():
            status_class = "done" if item['Live Status'] in ['Done', 'Closed'] else "progress" if item['Live Status'] in ['In Build', 'In Progress'] else "blocked"
            badge_class = f"badge-{status_class}"

            st.markdown(f"""
            <div class="timeline-item {status_class}">
                <div style='font-weight: 600; color: #1f2937; margin-bottom: 5px;'>{item['Functionality']}</div>
                <div style='font-size: 0.85rem; color: #6b7280; margin-bottom: 8px;'>{item['Category']}</div>
                <div>
                    <span class="status-badge {badge_class}">{item['Live Status']}</span>
                    {f"<span class='status-badge' style='background: #dbeafe; color: #1e40af;'>{item['JIRA Ticket #']}</span>" if pd.notna(item['JIRA Ticket #']) else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)

        remaining = len(data[data['Priority'] == 2]) - 7
        if remaining > 0:
            st.caption(f"+ {remaining} more Priority 2 items")

with tab2:
    # Kanban board view
    st.subheader("Kanban Board")

    col1, col2, col3, col4 = st.columns(4)

    statuses = {
        'Not Started': col1,
        'To Do': col2,
        'In Progress': col3,
        'Done': col4
    }

    for status_name, col in statuses.items():
        with col:
            # Map live status to kanban columns
            if status_name == 'Not Started':
                items = data[data['Live Status'].isin(['Not Started', 'Backlog'])]
            elif status_name == 'To Do':
                items = data[data['Live Status'].isin(['Proposed', 'To Do'])]
            elif status_name == 'In Progress':
                items = data[data['Live Status'].isin(['In Build', 'In Progress', 'In Development'])]
            else:
                items = data[data['Live Status'].isin(['Done', 'Closed'])]

            st.markdown(f"""
            <div style='background: #f3f4f6; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
                <div style='font-weight: 700; color: #1f2937;'>{status_name}</div>
                <div style='color: #6b7280; font-size: 0.9rem;'>{len(items)} items</div>
            </div>
            """, unsafe_allow_html=True)

            # Scrollable container for all items
            items_html = ""
            for _, item in items.iterrows():
                priority_color = "#fbbf24" if item['Priority'] == 1 else "#cbd5e1"
                func_text = item['Functionality'][:40] if len(item['Functionality']) > 40 else item['Functionality']
                items_html += f"<div style='background: white; border: 1px solid #e5e7eb; border-left: 4px solid {priority_color}; padding: 12px; margin-bottom: 8px; border-radius: 6px; font-size: 0.85rem;'><div style='font-weight: 600; color: #374151; margin-bottom: 4px;'>{func_text}...</div><div style='color: #9ca3af; font-size: 0.75rem;'>{item['Feature Area']}</div></div>"

            st.markdown(f"<div style='max-height: 600px; overflow-y: auto; padding-right: 5px;'>{items_html}</div>", unsafe_allow_html=True)

with tab3:
    # Modern Roadmap Timeline
    st.subheader("Q2 2026 Delivery Roadmap")

    # Progress bar for overall timeline
    progress_html = f"""<div style='background: white; padding: 25px; border-radius: 12px; border: 2px solid #e5e7eb; margin-bottom: 30px;'>
<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
<div>
<div style='font-size: 1.3rem; font-weight: 700; color: #1f2937;'>Overall Progress</div>
<div style='color: #6b7280; font-size: 0.9rem;'>Q2 2026 Initiative</div>
</div>
<div style='text-align: right;'>
<div style='font-size: 2rem; font-weight: 700; color: #3b82f6;'>{progress_pct:.1f}%</div>
<div style='color: #6b7280; font-size: 0.85rem;'>{completed}/{total_items} Complete</div>
</div>
</div>
<div style='background: #e5e7eb; height: 12px; border-radius: 6px; overflow: hidden;'>
<div style='background: linear-gradient(90deg, #3b82f6, #10b981); height: 100%; width: {progress_pct}%; transition: width 1s;'></div>
</div>
</div>"""
    st.markdown(progress_html, unsafe_allow_html=True)

    # Swimlane roadmap by feature area
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

    for feature_name in feature_order:
        feature_items = data[data['Feature Area'] == feature_name]

        if len(feature_items) == 0:
            continue

        # Count by status
        done_count = len(feature_items[feature_items['Live Status'].isin(['Done', 'Closed'])])
        progress_count = len(feature_items[feature_items['Live Status'].isin(['In Build', 'In Progress', 'In Development'])])
        todo_count = len(feature_items[feature_items['Live Status'].isin(['Proposed', 'To Do'])])
        not_started_count = len(feature_items[feature_items['Live Status'].isin(['Not Started', 'Backlog'])])

        feature_info = feature_colors[feature_name]
        feature_progress = (done_count / len(feature_items) * 100) if len(feature_items) > 0 else 0

        feature_html = f"""<div style='background: white; border: 2px solid #e5e7eb; border-radius: 12px; padding: 25px; margin-bottom: 20px; position: relative; overflow: hidden;'>
<div style='position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: {feature_info["color"]};'></div>
<div style='display: flex; align-items: center; margin-bottom: 20px;'>
<div style='font-size: 2.5rem; margin-right: 15px;'>{feature_info["icon"]}</div>
<div style='flex: 1;'>
<div style='font-size: 1.2rem; font-weight: 700; color: #1f2937;'>{feature_name}</div>
<div style='color: #6b7280; font-size: 0.85rem; margin-top: 2px;'>
<a href='https://apexclearing.atlassian.net/browse/{feature_info["ticket"]}' target='_blank' style='color: {feature_info["color"]}; text-decoration: none;'>{feature_info["ticket"]}</a>
· {len(feature_items)} items total
</div>
</div>
<div style='text-align: right;'>
<div style='font-size: 1.5rem; font-weight: 700; color: {feature_info["color"]};'>{feature_progress:.0f}%</div>
</div>
</div>
<div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 20px;'>
<div style='background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 15px; text-align: center;'>
<div style='font-size: 1.8rem; font-weight: 700; color: #15803d;'>{done_count}</div>
<div style='font-size: 0.8rem; color: #15803d; font-weight: 600; margin-top: 5px;'>✅ COMPLETED</div>
</div>
<div style='background: #fefce8; border: 1px solid #fde047; border-radius: 8px; padding: 15px; text-align: center;'>
<div style='font-size: 1.8rem; font-weight: 700; color: #a16207;'>{progress_count}</div>
<div style='font-size: 0.8rem; color: #a16207; font-weight: 600; margin-top: 5px;'>🔨 IN PROGRESS</div>
</div>
<div style='background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 15px; text-align: center;'>
<div style='font-size: 1.8rem; font-weight: 700; color: #1e40af;'>{todo_count}</div>
<div style='font-size: 0.8rem; color: #1e40af; font-weight: 600; margin-top: 5px;'>📋 TO DO</div>
</div>
<div style='background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 15px; text-align: center;'>
<div style='font-size: 1.8rem; font-weight: 700; color: #b91c1c;'>{not_started_count}</div>
<div style='font-size: 0.8rem; color: #b91c1c; font-weight: 600; margin-top: 5px;'>⏸️ NOT STARTED</div>
</div>
</div>
<div style='background: #f9fafb; height: 8px; border-radius: 4px; margin-top: 20px; overflow: hidden;'>
<div style='background: {feature_info["color"]}; height: 100%; width: {feature_progress}%; transition: width 1s;'></div>
</div>
</div>"""
        st.markdown(feature_html, unsafe_allow_html=True)

with tab4:
    # Analytics
    st.subheader("Status Analytics")

    col1, col2 = st.columns(2)

    with col1:
        # Sunburst chart
        sunburst_data = data.groupby(['Feature Area', 'Live Status']).size().reset_index(name='Count')

        fig = px.sunburst(
            sunburst_data,
            path=['Feature Area', 'Live Status'],
            values='Count',
            title='Items by Feature Area & Status',
            height=550
        )

        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True, key="sunburst")

    with col2:
        # Category distribution
        category_data = data['Category'].value_counts().reset_index()
        category_data.columns = ['Category', 'Count']

        fig = px.bar(
            category_data.head(8),
            x='Count',
            y='Category',
            orientation='h',
            title='Items by Category',
            height=550
        )

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )

        fig.update_traces(marker_color='#3b82f6')

        st.plotly_chart(fig, use_container_width=True, key="category_bar")

# Footer
st.markdown("""
<div style='margin-top: 50px; padding: 20px; border-top: 2px solid #e5e7eb; text-align: center; color: #9ca3af;'>
    <div style='font-size: 0.9rem;'>Last updated: {}</div>
    <div style='font-size: 0.85rem; margin-top: 5px;'>
        Auto-refreshes every 5 minutes |
        <a href='https://apexclearing.atlassian.net/browse/ASC-21760' target='_blank' style='color: #3b82f6;'>View Initiative ASC-21760</a>
    </div>
</div>
""".format(datetime.now().strftime('%B %d, %Y at %I:%M %p')), unsafe_allow_html=True)
