"""
core/datasource.py
---------------------------------------------------------
Unified data source handler for DMRB Dashboard.
Supports loading Excel from local file or Google Sheets URL.
---------------------------------------------------------
"""

import os
from io import BytesIO
from datetime import datetime
from pathlib import Path
import streamlit as st
import pandas as pd

try:
    import requests
except ImportError:
    requests = None

from core.logger import log_event


def get_data_source_config() -> dict:
    """
    Get data source configuration from environment or Streamlit secrets.
    
    Returns:
        Dict with 'mode' and 'url' or 'path'
    """
    # Try Streamlit secrets first, then env vars
    if hasattr(st, 'secrets') and 'data' in st.secrets:
        mode = st.secrets.data.get("DATA_SOURCE", "local")
        gdrive_url = st.secrets.data.get("GDRIVE_XLSX_URL", "")
        local_path = st.secrets.data.get("LOCAL_FILE_PATH", "data/DRMB.xlsx")
    else:
        mode = os.getenv("DATA_SOURCE", "local")
        gdrive_url = os.getenv("GDRIVE_XLSX_URL", "")
        local_path = os.getenv("LOCAL_FILE_PATH", "data/DRMB.xlsx")
    
    return {
        'mode': mode.lower(),
        'gdrive_url': gdrive_url,
        'local_path': local_path
    }


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_excel_bytes() -> tuple[bytes, datetime]:
    """
    Load Excel file bytes from configured data source.
    
    Returns:
        Tuple of (excel_bytes, timestamp)
    
    Raises:
        ValueError: If data source is invalid
        FileNotFoundError: If local file doesn't exist
        requests.HTTPError: If Google Sheets download fails
    """
    config = get_data_source_config()
    mode = config['mode']
    timestamp = datetime.now()
    
    log_event("INFO", f"Loading data from source: {mode}")
    
    if mode == "local":
        # Load from local file
        file_path = config['local_path']
        if not Path(file_path).exists():
            error_msg = f"Local Excel file not found: {file_path}"
            log_event("ERROR", error_msg)
            raise FileNotFoundError(error_msg)
        
        with open(file_path, "rb") as f:
            excel_bytes = f.read()
        
        log_event("INFO", f"Loaded {len(excel_bytes)} bytes from local file: {file_path}")
        return excel_bytes, timestamp
    
    elif mode == "gdrive":
        # Load from Google Sheets export URL
        if not requests:
            raise ImportError("requests library required for gdrive mode. Install with: pip install requests")
        
        url = config['gdrive_url']
        if not url:
            raise ValueError("GDRIVE_XLSX_URL not configured in secrets or environment")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            excel_bytes = response.content
            
            log_event("INFO", f"Loaded {len(excel_bytes)} bytes from Google Sheets: {url[:50]}...")
            return excel_bytes, timestamp
        
        except requests.RequestException as e:
            error_msg = f"Failed to download from Google Sheets: {e}"
            log_event("ERROR", error_msg)
            raise
    
    else:
        raise ValueError(f"Invalid DATA_SOURCE: {mode}. Must be 'local' or 'gdrive'")


def get_excel_file() -> pd.ExcelFile:
    """
    Get pandas ExcelFile object from configured data source.
    
    Returns:
        pd.ExcelFile object ready for sheet reading
    """
    excel_bytes, timestamp = load_excel_bytes()
    
    # Store timestamp in session state for display
    if 'last_data_update' not in st.session_state:
        st.session_state.last_data_update = timestamp
    else:
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
    config = get_data_source_config()
    mode = config['mode']
    
    if mode == "local":
        return f"📁 Local: {config['local_path']}"
    elif mode == "gdrive":
        url = config['gdrive_url']
        # Extract sheet ID if possible
        if 'spreadsheets/d/' in url:
            sheet_id = url.split('spreadsheets/d/')[1].split('/')[0]
            return f"☁️ Google Sheets: ...{sheet_id[-8:]}"
        return "☁️ Google Sheets"
    else:
        return f"❓ Unknown: {mode}"
