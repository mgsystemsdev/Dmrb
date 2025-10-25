"""
ui/refresh_controls.py
---------------------------------------------------------
Data refresh controls for DMRB Dashboard.
Provides manual refresh button and auto-refresh timer.
---------------------------------------------------------
"""

import streamlit as st
from datetime import datetime

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

from core.datasource import clear_data_cache, get_last_updated, get_data_source_info
from core.logger import log_event


def render_refresh_controls(key_prefix: str = "main", auto_refresh: bool = True):
    """
    Render data refresh controls in sidebar.
    
    Args:
        key_prefix: Unique key prefix for this instance
        auto_refresh: Enable auto-refresh every 5 minutes
    """
    st.markdown("### 🔄 Data Controls")
    
    # Manual refresh button
    if st.button("🔄 Refresh Data", use_container_width=True, key=f"{key_prefix}_refresh"):
        clear_data_cache()
        st.cache_data.clear()
        log_event("INFO", "Manual data refresh triggered")
        st.rerun()
    
    st.divider()
    
    # Data source info
    source_info = get_data_source_info()
    st.caption(f"**Source:** {source_info}")
    
    # Last updated timestamp
    last_updated = get_last_updated()
    st.caption(f"**Updated:** {last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Auto-refresh timer
    if auto_refresh and st_autorefresh:
        st.caption("🔁 Auto-refresh: 5 min")
        # Auto-refresh every 5 minutes (300,000 ms)
        st_autorefresh(interval=5 * 60 * 1000, key=f"{key_prefix}_auto")
    elif auto_refresh and not st_autorefresh:
        st.caption("⚠️ Install streamlit-autorefresh for auto-refresh")


def render_compact_refresh(key_prefix: str = "compact"):
    """
    Render compact refresh controls (button only).
    
    Args:
        key_prefix: Unique key prefix for this instance
    """
    if st.button("🔄 Refresh", use_container_width=True, key=f"{key_prefix}_refresh_compact"):
        clear_data_cache()
        st.cache_data.clear()
        log_event("INFO", "Manual data refresh triggered (compact)")
        st.rerun()


def render_last_updated_banner():
    """Render a banner showing last update time at top of page."""
    last_updated = get_last_updated()
    source_info = get_data_source_info()
    
    st.markdown(f"""
<div style='background: var(--gray-200); padding: 0.5rem 1rem; border-radius: var(--radius-md); margin-bottom: 1rem; text-align: center;'>
    <small><strong>Data Source:</strong> {source_info} | <strong>Last Updated:</strong> {last_updated.strftime('%Y-%m-%d %H:%M:%S')}</small>
</div>
""", unsafe_allow_html=True)
