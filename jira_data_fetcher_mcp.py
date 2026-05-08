"""
JIRA Data Fetcher using Claude MCP
Pulls live status from JIRA using Atlassian MCP integration
"""

import pandas as pd
import yaml
import os
import subprocess
import json

def load_config():
    """Load configuration from config.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_jira_status_mcp(ticket_id):
    """
    Fetch live status from JIRA using Claude MCP

    Args:
        ticket_id: JIRA ticket ID (e.g., 'ASC-14277')

    Returns:
        dict with ticket status info
    """
    config = load_config()
    cloud_id = config['jira']['cloud_id']

    try:
        # Use Claude CLI to call MCP tool
        cmd = [
            'claude',
            'mcp',
            'call',
            'atlassian',
            'getJiraIssue',
            '--cloudId', cloud_id,
            '--issueIdOrKey', ticket_id,
            '--responseContentFormat', 'adf'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # Parse the JSON response
            data = json.loads(result.stdout)

            # Extract status from the response
            if isinstance(data, list) and len(data) > 0:
                issue_data = json.loads(data[0]['text'])
                fields = issue_data.get('fields', {})

                return {
                    'ticket': ticket_id,
                    'status': fields.get('status', {}).get('name', 'Unknown'),
                    'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                    'due_date': fields.get('duedate'),
                    'updated': fields.get('updated'),
                    'summary': fields.get('summary', '')
                }

        # If MCP call fails, return Unknown
        print(f"Warning: MCP call failed for {ticket_id}")
        return {
            'ticket': ticket_id,
            'status': 'Unknown',
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

def fetch_all_jira_tickets():
    """
    Fetch status for all 4 Feature tickets using MCP

    Returns:
        dict mapping ticket_id -> status info
    """
    config = load_config()
    tickets = config['jira']['feature_tickets']

    jira_data = {}
    for ticket_id in tickets:
        status_info = get_jira_status_mcp(ticket_id)
        if status_info:
            jira_data[ticket_id] = status_info

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
        elif status in ['Proposed', 'Not Started', 'To Do', 'Backlog']:
            return '🔴'
        else:
            return '⚪'  # Unknown

    result['Status Color'] = result['Live Status'].apply(get_color)

    return result

if __name__ == "__main__":
    # Test the JIRA fetcher
    print("Fetching JIRA status using MCP...")
    jira_data = fetch_all_jira_tickets()

    print(f"\nFound {len(jira_data)} tickets:")
    for ticket_id, info in jira_data.items():
        print(f"  {ticket_id}: {info['status']} (Assigned to: {info['assignee']})")
