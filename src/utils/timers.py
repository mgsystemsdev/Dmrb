"""
utils/timers.py
---------------------------------------------------------
Auto-refresh logic and timed reads for Streamlit.
---------------------------------------------------------
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import log_event


def setup_auto_refresh(interval_seconds: int = 300) -> None:
    """
    Setup automatic page refresh using Streamlit's experimental rerun.
    
    Args:
        interval_seconds: Refresh interval in seconds (default: 5 minutes)
    
    Note:
        This is a placeholder. Streamlit doesn't have built-in auto-refresh.
        Use st.experimental_rerun() in combination with time.sleep() in a separate thread,
        or implement client-side refresh via custom components.
    """
    # Placeholder for future implementation
    log_event("INFO", f"Auto-refresh configured for {interval_seconds}s intervals")


def get_last_refresh_time() -> str:
    """
    Get formatted timestamp of last data refresh.
    
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def render_refresh_controls(interval_minutes: int = 5, file_path: str = "data/DRMB.xlsx") -> None:
    """
    Render refresh controls in sidebar.
    
    DEPRECATED: Use src.ui.sidebar.render_sidebar_controls instead.
    
    Args:
        interval_minutes: Suggested refresh interval
        file_path: Path to data file
    """
    with st.sidebar:
        st.header("🔍 Controls")
        
        if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_button"):
            st.cache_data.clear()
            st.rerun()
        
        st.divider()
        
        st.markdown(f"""
        **Last Updated:**  
        {get_last_refresh_time()}
        
        **Data Source:**  
        `{file_path}`
        
        **Suggested Refresh:**  
        Every {interval_minutes} minutes
        """)
