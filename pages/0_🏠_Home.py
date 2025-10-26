"""
pages/0_🏠_Home.py
---------------------------------------------------------
Home page with community overview and module navigation.
---------------------------------------------------------
"""

import streamlit as st
from utils.styling import inject_css
from core.logger import log_event
from utils.constants import APP_NAME, APP_VERSION, TOTAL_UNITS

# --- Page Configuration ---
st.set_page_config(
    page_title="Thousand Oaks",
    page_icon="🍁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Inject Global CSS ---
inject_css()

# --- Sidebar ---
with st.sidebar:
    st.header("📍 Navigation")
    st.info("Use the menu above to navigate")

# --- Header ---
st.title("🍁 Thousand Oaks")
st.caption(f"{APP_NAME} · v{APP_VERSION}")
st.divider()

# --- Overview Stats ---
st.subheader("🏢 Community Overview")

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown(f'''
    <div style='background: var(--gray-200); border: 1px solid var(--gray-400); border-radius: var(--radius-md); padding: var(--spacing-md); text-align: center; box-shadow: var(--shadow-md);'>
        <div style='color: var(--gray-700); font-size: 0.75rem; font-weight: 600; text-transform: uppercase;'>Total Units</div>
        <div style='color: var(--gray-900); font-size: 2.5rem; font-weight: 800; margin: 0.5rem 0;'>{TOTAL_UNITS:,}</div>
        <div style='color: var(--gray-700); font-size: 0.875rem;'>Apartment Units</div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background: var(--gray-200); border: 1px solid var(--gray-400); border-radius: var(--radius-md); padding: var(--spacing-md); text-align: center; box-shadow: var(--shadow-md);'>
        <div style='color: var(--gray-700); font-size: 0.75rem; font-weight: 600; text-transform: uppercase;'>Operational Nodes</div>
        <div style='color: var(--gray-900); font-size: 2.5rem; font-weight: 800; margin: 0.5rem 0;'>1,000</div>
        <div style='color: var(--gray-700); font-size: 0.875rem;'>Touchpoints</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background: var(--gray-200); border: 1px solid var(--gray-400); border-radius: var(--radius-md); padding: var(--spacing-md); text-align: center; box-shadow: var(--shadow-md);'>
        <div style='color: var(--gray-700); font-size: 0.75rem; font-weight: 600; text-transform: uppercase;'>Active Phases</div>
        <div style='color: var(--gray-900); font-size: 2.5rem; font-weight: 800; margin: 0.5rem 0;'>3</div>
        <div style='color: var(--gray-700); font-size: 0.875rem;'>Property Segments</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- Dashboard Modules ---
st.subheader("📍 Dashboard Modules")

col_a, col_b = st.columns(2, gap="large")

with col_a:
    st.markdown("""
    <div class='phase-card'>
        <div style='color: var(--gray-900); font-size: 1.25rem; font-weight: 700; margin-bottom: 0.75rem;'>📊 Dashboard</div>
        <p style='color: var(--gray-700); line-height: 1.6;'>
            Real-time occupancy metrics, KPIs, and operational insights. 
            Monitor vacant units, move activity, and phase performance.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Go to Dashboard", use_container_width=True, key="nav_dashboard"):
        st.switch_page("pages/1_📊_Dashboard.py")

with col_b:
    st.markdown("""
    <div class='phase-card'>
        <div style='color: var(--gray-900); font-size: 1.25rem; font-weight: 700; margin-bottom: 0.75rem;'>🏢 Units Manager</div>
        <p style='color: var(--gray-700); line-height: 1.6;'>
            Track unit-level readiness and move schedules. Manage building 
            assignments and monitor unit conditions.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Go to Units Lifecycle", use_container_width=True, key="nav_units"):
        st.switch_page("pages/2_🏢_Units.py")

st.divider()

# --- About Section ---
with st.expander("💡 About", expanded=False):
    st.markdown(f"""
    **Thousand Oaks Make-Ready Dashboard**
    
    Version: {APP_VERSION}
    
    This operational cockpit provides real-time visibility into property operations. 
    Use the sidebar menu above to navigate between modules.
    
    **Data Source:** `data/DRMB.xlsx`  
    **Manager:** Miguel González Almonte
    """)

st.divider()
st.caption("© 2025 Thousand Oaks | Internal Use Only")

log_event("INFO", "Home page loaded")
