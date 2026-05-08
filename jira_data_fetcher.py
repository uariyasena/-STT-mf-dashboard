"""
JIRA Data Fetcher
Pulls live status from JIRA using REST API
"""

import requests
from datetime import datetime
import pandas as pd
import yaml
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_config():
    """Load configuration from config.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_jira_status(ticket_id, auth_token=None):
    """
    Fetch live status from JIRA REST API

    Args:
        ticket_id: JIRA ticket ID (e.g., 'ASC-14277')
        auth_token: Bearer token for authentication (optional, will use env var if not provided)

    Returns:
        dict with ticket status info or None if error
    """
    config = load_config()
    cloud_id = config['jira']['cloud_id']

    # Get auth token from environment if not provided
    if auth_token is None:
        auth_token = os.environ.get('JIRA_AUTH_TOKEN')

    if not auth_token:
        print(f"Warning: No JIRA auth token provided for {ticket_id}")
        return {
            'ticket': ticket_id,
            'status': 'Unknown',
            'assignee': 'Unknown',
            'due_date': None,
            'updated': None
        }

    # Call JIRA API
    url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/issue/{ticket_id}"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            fields = data.get('fields', {})

            return {
                'ticket': ticket_id,
                'status': fields.get('status', {}).get('name', 'Unknown'),
                'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                'due_date': fields.get('duedate'),
                'updated': fields.get('updated'),
                'summary': fields.get('summary', '')
            }
        else:
            print(f"Error fetching {ticket_id}: HTTP {response.status_code}")
            return {
                'ticket': ticket_id,
                'status': 'Error',
                'assignee': 'Unknown',
                'due_date': None,
                'updated': None
            }

    except Exception as e:
        print(f"Exception fetching {ticket_id}: {str(e)}")
        return {
            'ticket': ticket_id,
            'status': 'Error',
            'assignee': 'Unknown',
            'due_date': None,
            'updated': None
        }

def fetch_all_jira_tickets(auth_token=None):
    """
    Fetch status for all 4 Feature tickets

    NOTE: Currently using static data from JIRA as of 2026-04-23
    All 4 tickets assigned to David Dickson, due 2026-06-15

    Returns:
        dict mapping ticket_id -> status info
    """
    # Static JIRA data - updated 2026-04-23
    jira_data = {
        'ASC-14277': {
            'ticket': 'ASC-14277',
            'status': 'In Build',
            'assignee': 'David Dickson',
            'due_date': '2026-06-15',
            'updated': '2026-04-22T15:25:04.765-0500',
            'summary': 'Mutual Fund Exchange/Switch Orders'
        },
        'ASC-21778': {
            'ticket': 'ASC-21778',
            'status': 'Proposed',
            'assignee': 'David Dickson',
            'due_date': '2026-06-15',
            'updated': '2026-04-22T15:30:23.662-0500',
            'summary': 'Periodic Investment/Withdrawal Plans (PIP/SWIP)'
        },
        'ASC-21779': {
            'ticket': 'ASC-21779',
            'status': 'Proposed',
            'assignee': 'David Dickson',
            'due_date': '2026-06-15',
            'updated': '2026-04-17T10:50:51.968-0500',
            'summary': 'Dividend Reinvestment Election Maintenance'
        },
        'ASC-21783': {
            'ticket': 'ASC-21783',
            'status': 'Proposed',
            'assignee': 'David Dickson',
            'due_date': '2026-06-15',
            'updated': '2026-04-22T16:11:21.308-0500',
            'summary': 'Rights of Accumulation (ROA) & Letter of Intent (LOI) Enhancements'
        }
    }

    return jira_data

def map_status_to_items(excel_df, jira_statuses):
    """
    Map JIRA status to each of the 29 Excel items

    Args:
        excel_df: DataFrame with Excel data
        jira_statuses: dict of JIRA status info

    Returns:
        DataFrame with live status added
    """
    result = excel_df.copy()

    # Map status from JIRA tickets
    def get_status(ticket):
        if pd.isna(ticket) or ticket == 'TBD':
            return 'Not Started'
        jira_info = jira_statuses.get(ticket, {})
        return jira_info.get('status', 'Unknown')

    result['Live Status'] = result['JIRA Ticket #'].apply(get_status)

    # Add status color emoji
    def get_color(status):
        if status in ['Done', 'Closed']:
            return '🟢'
        elif status in ['In Build', 'In Progress', 'In Development']:
            return '🟡'
        elif status in ['Proposed', 'To Do']:
            return '🔵'  # Proposed (in To Do column)
        elif status in ['Not Started', 'Backlog']:
            return '🔴'
        else:
            return '⚪'  # Unknown

    result['Status Color'] = result['Live Status'].apply(get_color)

    return result

if __name__ == "__main__":
    # Test the JIRA fetcher
    print("Fetching JIRA status...")
    jira_data = fetch_all_jira_tickets()

    print(f"\nFound {len(jira_data)} tickets:")
    for ticket_id, info in jira_data.items():
        print(f"  {ticket_id}: {info['status']} (Assigned to: {info['assignee']})")
