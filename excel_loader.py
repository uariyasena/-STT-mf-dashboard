"""
Excel Data Loader
Loads the 29 prioritized MF items from the Excel file
"""

import pandas as pd
import yaml
import os

def load_config():
    """Load configuration from config.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_prioritized_items():
    """
    Load the 29 prioritized MF items from Excel
    Returns: pandas DataFrame
    """
    config = load_config()

    # Build full path to Excel file
    excel_path = os.path.join(
        os.path.dirname(__file__),
        config['excel']['file_path']
    )

    # Read Excel
    df = pd.read_excel(
        excel_path,
        sheet_name=config['excel']['sheet_name']
    )

    # Ensure required columns exist
    required_cols = ['Category', 'Sub Category', 'Functionality', 'Priority', 'JIRA Ticket #']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Add Feature Area mapping based on JIRA ticket
    def get_feature_area(ticket):
        if pd.isna(ticket):
            return 'Unknown'
        if ticket == 'ASC-14277':
            return 'Exchange'
        elif ticket == 'ASC-21778':
            return 'PIP/SWIP'
        elif ticket == 'ASC-21779':
            return 'DRIP'
        elif ticket == 'ASC-21783':
            return 'ROA/LOI'
        else:
            return 'Other'

    df['Feature Area'] = df['JIRA Ticket #'].apply(get_feature_area)

    return df

if __name__ == "__main__":
    # Test the loader
    data = load_prioritized_items()
    print(f"Loaded {len(data)} items")
    print(f"\nColumns: {data.columns.tolist()}")
    print(f"\nFirst 5 rows:")
    print(data.head())
    print(f"\nFeature Area breakdown:")
    print(data['Feature Area'].value_counts())
