"""
core/datasource.py
---------------------------------------------------------
Google Sheets data source handler for DMRB Dashboard.
Loads Excel from Google Sheets export URL only.
---------------------------------------------------------
"""

from io import BytesIO
from datetime import datetime
import streamlit as st
import pandas as pd

try:
    import requests
except ImportError:
    requests = None

from core.logger import log_event


def get_gdrive_url() -> str:
    """
    Get Google Sheets export URL from Streamlit secrets.
    
    Returns:
        Google Sheets export URL
    """
    # Try Streamlit secrets
    if hasattr(st, 'secrets') and 'GDRIVE_XLSX_URL' in st.secrets:
        return st.secrets["GDRIVE_XLSX_URL"]
    
    # Fallback to hardcoded URL
    return "https://docs.google.com/spreadsheets/d/1alxeq1eGB6nbDXWhKh5O34FQkFcXkYOI/export?format=xlsx"


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_excel_bytes() -> tuple[bytes, datetime]:
    """
    Load Excel file bytes from Google Sheets.
    
    Returns:
        Tuple of (excel_bytes, timestamp)
    
    Raises:
        ImportError: If requests library not installed
        requests.HTTPError: If Google Sheets download fails
    """
    if not requests:
        raise ImportError("requests library required. Install with: pip install requests")
    
    url = get_gdrive_url()
    timestamp = datetime.now()
    
    log_event("INFO", f"Loading data from Google Sheets")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        excel_bytes = response.content
        
        log_event("INFO", f"Loaded {len(excel_bytes)} bytes from Google Sheets")
        return excel_bytes, timestamp
    
    except requests.RequestException as e:
        error_msg = f"Failed to download from Google Sheets: {e}"
        log_event("ERROR", error_msg)
        raise


def get_excel_file() -> pd.ExcelFile:
    """
    Get pandas ExcelFile object from Google Sheets.
    
    Returns:
        pd.ExcelFile object ready for sheet reading
    """
    excel_bytes, timestamp = load_excel_bytes()
    
    # Store timestamp in session state for display
    st.session_state.last_data_update = timestamp
    
    return pd.ExcelFile(BytesIO(excel_bytes))


def clear_data_cache():
    """Clear the cached Excel data to force reload."""
    load_excel_bytes.clear()
    log_event("INFO", "Data cache cleared")


def get_last_updated() -> datetime:
    """
    Get timestamp of last data load.
    
    Returns:
        datetime object of last update, or current time if not available
    """
    return st.session_state.get('last_data_update', datetime.now())


def get_data_source_info() -> str:
    """
    Get human-readable info about current data source.
    
    Returns:
        String describing the data source
    """
    url = get_gdrive_url()
    
    # Extract sheet ID if possible
    if 'spreadsheets/d/' in url:
        sheet_id = url.split('spreadsheets/d/')[1].split('/')[0]
        return f"☁️ Google Sheets: ...{sheet_id[-8:]}"
    
    return "☁️ Google Sheets"
