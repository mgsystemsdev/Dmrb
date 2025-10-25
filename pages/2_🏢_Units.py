# pages/2_🏢_Units.py
# ---------------------------------------------------------
# Units Lifecycle Page: same polished style as Dashboard Phase Overview
# Phase → Building → Unit hierarchy throughout.
# ---------------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.data_loader import load_units_sheet, load_task_sheet
from core.data_logic import compute_all_unit_fields
from utils.constants import EXCEL_FILE_PATH, TOTAL_UNITS
from ui.unit_cards import render_enhanced_unit_row, render_unit_kpi_cards
from ui.sections import create_simple_section, render_section
from ui.refresh_controls import render_refresh_controls
from core.logger import log_event

# --- Page Setup ---
st.set_page_config(
    page_title="Units Lifecycle | Thousand Oaks",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Inject Style to Match Dashboard Phase Overview ---
st.markdown("""
<style>
.phase-section {
    background: var(--gray-100);
    border: 2px solid var(--gray-400);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    margin-bottom: 2rem;
    box-shadow: var(--shadow-xl);
}
.phase-section h3 {
    color: var(--gray-900);
    margin-top: 0;
    margin-bottom: 1.25rem;
    font-size: 1.5rem;
    font-weight: 700;
}
.streamlit-expanderHeader {
    background-color: rgba(255, 255, 255, 0.6) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
/* Center only page/section titles */
h1, h2, h3, h4 { text-align: center !important; }
/* Make unit rows thinner without changing font sizes */
.phase-section [data-testid="stMetric"] { margin: 0.1rem 0 !important; padding: 0 !important; }
.phase-section [data-testid="stMetricLabel"] { margin-bottom: 0.1rem !important; }
.phase-section [data-testid="stMetricValue"] { line-height: 1.1 !important; }
.phase-section [data-testid="stCaptionContainer"] { margin: 0.1rem 0 0 0 !important; }
.phase-section [data-testid="column"] { padding-left: 0.25rem !important; padding-right: 0.25rem !important; }
.phase-section [data-testid="stMarkdownContainer"] p { margin: 0.1rem 0 !important; }
.phase-section div[role="progressbar"] { height: 6px !important; }
hr {
    border-top: 1px solid var(--gray-300);
    margin-top: 0.75rem;
    margin-bottom: 0.75rem;
}
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
try:
    units_df = load_units_sheet(EXCEL_FILE_PATH)
    column_mapping = {
        'Move-out': 'move_out',
        'Move-in': 'move_in',
        'Nvm': 'nvm',
        'Unit': 'unit_id',
        'Phases': 'phase',
        'Building': 'building'
    }
    units_df = units_df.rename(columns=column_mapping)
    # Keep status as-is (will be NaN if not populated in Excel)
    units_df = compute_all_unit_fields(units_df)
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

try:
    tasks_df = load_task_sheet(EXCEL_FILE_PATH)
except:
    tasks_df = pd.DataFrame()

# --- Sidebar ---
with st.sidebar:
    st.header("Controls")
    if st.button("🔄 Refresh Data", use_container_width=True, key="units_refresh"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.caption(f"**Updated:** {datetime.now().strftime('%H:%M:%S')}")

# --- Header ---
st.markdown("<h1 style='text-align: center;'>🏢 Units Lifecycle Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--gray-700);'>Phase → Building → Unit | Notice → Vacant → In Turn → Ready</p>", unsafe_allow_html=True)
st.divider()

# --- KPIs ---
# Use TOTAL_UNITS constant (1300) for calculations like Dashboard
nvm_norm = units_df['nvm'].fillna('').astype(str).str.lower()
vacant_units = nvm_norm.isin(['vacant', 'smi']).sum()
occupied_units = TOTAL_UNITS - vacant_units
occupancy_pct = (occupied_units / TOTAL_UNITS * 100) if TOTAL_UNITS else 0
vacancy_pct = (vacant_units / TOTAL_UNITS * 100) if TOTAL_UNITS else 0
total_units = TOTAL_UNITS  # Use constant for display
avg_days_vacant = units_df['days_vacant'].mean() if 'days_vacant' in units_df.columns else 0
active_turns = units_df['lifecycle_label'].isin(['In Turn']).sum() if 'lifecycle_label' in units_df.columns else 0
units_ready = units_df['lifecycle_label'].isin(['Ready']).sum() if 'lifecycle_label' in units_df.columns else 0

kpi_metrics = {
    'total_units': total_units,
    'vacant_units': vacant_units,
    'occupied_units': occupied_units,
    'occupancy_pct': occupancy_pct,
    'vacancy_pct': vacancy_pct,
    'avg_days_vacant': avg_days_vacant,
    'active_turns': active_turns,
    'units_ready': units_ready
}

with st.container():
    render_unit_kpi_cards(kpi_metrics)

st.divider()

# --- Helper Function ---
def build_enhanced_unit(row, tasks_df) -> dict:
    unit_id = str(row.get('unit_id', ''))
    unit_tasks = tasks_df[tasks_df.get('Unit', '') == unit_id] if not tasks_df.empty and 'Unit' in tasks_df.columns else pd.DataFrame()
    lifecycle = row.get('lifecycle_label', 'Unknown')
    status_emoji_map = {
        'Ready': '✅',
        'In Turn': '🔧',
        'Not Ready': '⚠️'
    }
    status_emoji = status_emoji_map.get(lifecycle, '🏠')
    readiness_pct = 100 if lifecycle == 'Ready' else 50 if lifecycle == 'In Turn' else 0

    days_vacant = row.get('days_vacant')
    days_vacant_str = str(int(days_vacant)) if pd.notna(days_vacant) and days_vacant != '' else '—'

    days_to_ready = row.get('days_to_be_ready')
    days_to_ready_str = str(int(days_to_ready)) if pd.notna(days_to_ready) and days_to_ready != '' else '—'

    return {
        'unit_id': unit_id,
        'status_emoji': status_emoji,
        'move_out': row.get('move_out', pd.NaT).strftime('%m/%d/%y') if pd.notna(row.get('move_out')) else '—',
        'move_in': row.get('move_in', pd.NaT).strftime('%m/%d/%y') if pd.notna(row.get('move_in')) else '—',
        'days_vacant': days_vacant_str,
        'days_to_ready': days_to_ready_str,
        'readiness_pct': readiness_pct,
        'status': lifecycle  # Add status to display at end
    }

# --- Render Helper: Phase > Building > Units ---
def render_units_by_hierarchy(units_subset, tasks_df, title_prefix=""):
    """Render units grouped by Phase > Building with nested expanders."""
    if len(units_subset) == 0:
        st.info("No units to display")
        return

    # Wrap in styled container matching dashboard
    st.markdown("""
<div class="phase-section" style="background: var(--gray-100); border: 2px solid var(--gray-400); border-radius: var(--radius-lg); padding: var(--spacing-xl); margin-bottom: 2rem; box-shadow: var(--shadow-xl);">
""", unsafe_allow_html=True)

    st.caption(f"**{len(units_subset)} units** {title_prefix}")
    st.divider()

    for phase in sorted(units_subset['phase'].dropna().unique()):
        phase_units = units_subset[units_subset['phase'] == phase]

        # Phase expander
        with st.expander(f"🧱 Phase {int(phase)} — {len(phase_units)} units", expanded=False):
            for building in sorted(phase_units['building'].dropna().unique()):
                building_units = phase_units[phase_units['building'] == building]
                
                # Calculate building stats
                nvm_norm = building_units['nvm'].fillna('').astype(str).str.lower()
                vacant_count = nvm_norm.isin(['vacant', 'smi']).sum()
                occupied_count = len(building_units) - vacant_count

                # Building expander inside phase
                with st.expander(f"🏢 Building {int(building)} — {len(building_units)} units | 🟥 {occupied_count} occ | 🟩 {vacant_count} vac", expanded=False):
                    # Each unit in its own row with a subtle hairline between rows
                    for idx, (_, unit_row) in enumerate(building_units.iterrows()):
                        render_enhanced_unit_row(build_enhanced_unit(unit_row, tasks_df))
                        if idx < len(building_units) - 1:  # No divider after last unit
                            st.markdown('<div class="hairline"></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- Tab Renderers ---
def render_active_units_tab(context):
    units_df, tasks_df = context['units_df'], context['tasks_df']
    # Active = Not Ready or In Turn (anything not fully Ready)
    active = units_df[units_df['lifecycle_label'].isin(['Not Ready', 'In Turn'])].copy()
    active = active.sort_values('days_vacant', ascending=False, na_position='last')
    render_units_by_hierarchy(active, tasks_df, "in active pipeline")

def render_nvm_tab(context):
    units_df, tasks_df = context['units_df'], context['tasks_df']
    
    nvm_tabs = st.tabs(["📢 Notice", "🔴 Vacant", "📦 Moving"])

    with nvm_tabs[0]:
        # Notice = nvm column contains 'notice'
        nvm_norm = units_df['nvm'].fillna('').astype(str).str.lower()
        notice = units_df[nvm_norm == 'notice'].copy()
        notice = notice.sort_values('days_vacant', ascending=False, na_position='last')
        render_units_by_hierarchy(notice, tasks_df, "on notice")

    with nvm_tabs[1]:
        # Vacant = nvm column contains 'vacant' or 'smi'
        nvm_norm = units_df['nvm'].fillna('').astype(str).str.lower()
        vacant = units_df[nvm_norm.isin(['vacant', 'smi'])].copy()
        vacant = vacant.sort_values('days_vacant', ascending=False, na_position='last')
        render_units_by_hierarchy(vacant, tasks_df, "vacant")

    with nvm_tabs[2]:
        # Moving = move-in within next 72 hours
        move_in_dates = pd.to_datetime(units_df['move_in'], errors='coerce')
        next_72h = datetime.now() + timedelta(hours=72)
        moving = units_df[move_in_dates <= next_72h].copy()
        moving = moving.sort_values('days_vacant', ascending=False, na_position='last')
        render_units_by_hierarchy(moving, tasks_df, "moving in 72h")

def render_ready_vs_not_tab(context):
    units_df, tasks_df = context['units_df'], context['tasks_df']
    ready_tabs = st.tabs(["✅ Ready", "⚠️ Not Ready"])

    with ready_tabs[0]:
        ready = units_df[units_df['lifecycle_label'] == 'Ready'].copy()
        ready = ready.sort_values('days_vacant', ascending=False, na_position='last')
        render_units_by_hierarchy(ready, tasks_df, "ready")

    with ready_tabs[1]:
        # Not Ready includes both 'Not Ready' and 'In Turn'
        not_ready = units_df[units_df['lifecycle_label'].isin(['Not Ready', 'In Turn'])].copy()
        not_ready = not_ready.sort_values('days_vacant', ascending=False, na_position='last')
        render_units_by_hierarchy(not_ready, tasks_df, "not ready")

def render_all_units_tab(context):
    units_df, tasks_df = context['units_df'], context['tasks_df']
    all_units = units_df.sort_values('days_vacant', ascending=False, na_position='last')
    render_units_by_hierarchy(all_units, tasks_df, "total")

# --- Main Sections ---
units_section = create_simple_section(
    title="Units Overview",
    icon="🏠",
    tabs=[
        ("Active Pipeline", render_active_units_tab),
        ("Notice / Vacant / Moving", render_nvm_tab),
        ("Ready vs Not Ready", render_ready_vs_not_tab),
        ("All Units", render_all_units_tab)
    ]
)

context = {
    'units_df': units_df,
    'tasks_df': tasks_df,
    'today': datetime.now().date()
}

render_section(units_section, context)

st.divider()

# --- Footer KPIs ---
st.subheader("Performance Summary")

footer_col1, footer_col2, footer_col3, footer_col4 = st.columns(4)

sla_compliant = units_df[units_df['days_vacant'] <= 8].shape[0] if 'days_vacant' in units_df.columns else 0
sla_pct = (sla_compliant / vacant_units * 100) if vacant_units > 0 else 0
units_at_risk = units_df[(units_df['days_vacant'] > 25) & (units_df['lifecycle_label'] != 'Ready')].shape[0] if 'days_vacant' in units_df.columns else 0
health_status = "🟢 Healthy" if avg_days_vacant <= 10 else "🟡 Lagging" if avg_days_vacant <= 20 else "🔴 Critical"

with footer_col1:
    st.metric("Units in View", total_units)

with footer_col2:
    st.metric("SLA Compliance", f"{sla_pct:.0f}%", help=f"{sla_compliant} units ≤ 8 days")

with footer_col3:
    st.metric("Units At Risk", units_at_risk, help="> 25 days vacant")

with footer_col4:
    st.metric("Health Status", health_status)

st.divider()
st.caption("© 2025 Thousand Oaks | Units Lifecycle")

log_event("INFO", "Units page loaded")
