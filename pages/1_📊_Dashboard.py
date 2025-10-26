"""
pages/dashboard.py
---------------------------------------------------------
Property-level snapshot & daily KPIs.
Main dashboard view with occupancy metrics and phase overview.
---------------------------------------------------------
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Internal Imports ---
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.data_loader import load_units_sheet, load_task_sheet
from core.data_logic import compute_all_unit_fields
from utils.styling import inject_css
from utils.constants import TOTAL_UNITS
from ui.hero_cards import render_kpi_card, render_kpi_card_with_progress
from ui.expanders import render_phase_expander, render_unit_row
from ui.toggle_controls import render_expand_collapse_controls, get_expanded_state
from ui.sections import create_simple_section, render_section
from ui.refresh_controls import render_refresh_controls
from core.logger import log_event
from core.phase_logic import build_phase_overview, build_all_units

# --- Page Setup ---
st.set_page_config(
    page_title="Thousand Oaks Dashboard",
    page_icon="🍁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Inject Global CSS ---
inject_css()

# --- Constants (imported from utils.constants) ---

# --- Load Data ---
try:
    units_df = load_units_sheet()
    # Compute lifecycle labels and other derived fields
    column_mapping = {
        'Move-out': 'move_out',
        'Move-in': 'move_in',
        'Unit': 'unit_id',
        'Phases': 'phase',
        'Building': 'building'
    }
    units_df = units_df.rename(columns=column_mapping)
    # Compute all derived fields including NVM status
    units_df = compute_all_unit_fields(units_df)
    # Rename back for compatibility (nvm is computed, stays lowercase)
    units_df = units_df.rename(columns={
        'move_out': 'Move-out',
        'move_in': 'Move-in',
        'unit_id': 'Unit',
        'phase': 'Phases',
        'building': 'Building'
    })
except Exception as e:
    st.error(f"❌ Failed to load Excel data: {e}")
    st.stop()

# --- Validate Required Columns ---
required_cols = ["Unit", "Phases", "Building", "Move-out", "Move-in"]
missing_cols = [col for col in required_cols if col not in units_df.columns]
if missing_cols:
    st.error(f"❌ Missing required columns: {missing_cols}")
    st.stop()

# --- Vacancy Calculation ---
from utils.constants import VACANT_STATUSES
nvm_normalized = units_df["nvm"].fillna("").astype(str).str.strip().str.lower()
vacant_units = nvm_normalized.isin([s.lower() for s in VACANT_STATUSES]).sum()

# --- Occupancy Calculation ---
occupied_units = TOTAL_UNITS - vacant_units
occupancy_pct = round((occupied_units / TOTAL_UNITS) * 100, 1) if TOTAL_UNITS else 0

# --- Sidebar Controls ---
with st.sidebar:
    render_refresh_controls(key_prefix="dash", auto_refresh=True)

# --- Header ---
st.markdown("""
<style>
    .main-title {
        font-size: 6rem;
        font-weight: 1000;
        text-align: center;
        color: var(--gray-900);
        letter-spacing: 2px;
        margin-top: -10px;
        margin-bottom: 0px;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
    }
    .caption-centered {
        text-align: center;
        color: var(--gray-700);
        font-size: 1rem;
        margin-top: 0px;
        margin-bottom: 25px;
    }
</style>

<h1 class="main-title">🍁 Thousand Oaks</h1>
<div class="caption-centered">
    Operational Dashboard
</div>
""", unsafe_allow_html=True)
st.divider()

# --- KPI Section ---
st.markdown("""
<div style="background: var(--gray-100); border: 2px solid var(--gray-400); border-radius: var(--radius-lg); padding: var(--spacing-xl); margin-bottom: 2rem; box-shadow: var(--shadow-xl);">
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    render_kpi_card(
        label="🏢 Total Units",
        value=f"{TOTAL_UNITS:,}",
        emoji=""
    )

with col2:
    render_kpi_card(
        label="🟩 Vacant Units",
        value=f"{vacant_units:,}",
        emoji=""
    )

with col3:
    render_kpi_card(
        label="🟥 Occupied Units",
        value=f"{occupied_units:,}",
        emoji=""
    )

with col4:
    render_kpi_card_with_progress(
        label="📊 Occupancy %",
        value=occupancy_pct,
        max_value=100,
        emoji=""
    )

st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# --- Move Activity Section ---

# Define render functions for Move Activity tabs
def render_move_outs_today(context):
    """Show units with move-outs today or later."""
    units_df = context['units_df']
    today = context['today']
    
    move_out_dates = pd.to_datetime(units_df['Move-out'], errors='coerce')
    move_outs = units_df[move_out_dates.dt.date >= today].copy()
    move_outs = move_outs.sort_values('Move-out')
    
    st.markdown(f"**{len(move_outs)} move-outs** today and upcoming")
    st.divider()
    
    if len(move_outs) > 0:
        for _, row in move_outs.iterrows():
            move_out_date = pd.to_datetime(row.get('Move-out'), errors='coerce')
            unit = {
                'unit_num': str(row.get('Unit', '')),
                'status_emoji': '🟥',
                'move_out_str': move_out_date.strftime('%m/%d/%y') if pd.notna(move_out_date) else '—',
                'days_vacant': '—',
                'move_in_str': '—',
                'days_to_be_ready': '—',
                'nvm': row.get('Nvm', '—')
            }
            render_unit_row(unit)
    else:
        st.info("No upcoming move-outs")

def render_move_ins_tomorrow(context):
    """Show units with move-ins tomorrow."""
    units_df = context['units_df']
    tomorrow = context['today'] + timedelta(days=1)
    
    move_in_dates = pd.to_datetime(units_df['Move-in'], errors='coerce')
    move_ins = units_df[move_in_dates.dt.date == tomorrow].copy()
    
    st.markdown(f"**{len(move_ins)} move-ins** scheduled for tomorrow")
    st.divider()
    
    if len(move_ins) > 0:
        for _, row in move_ins.iterrows():
            move_in_date = pd.to_datetime(row.get('Move-in'), errors='coerce')
            unit = {
                'unit_num': str(row.get('Unit', '')),
                'status_emoji': '🟩',
                'move_out_str': '—',
                'days_vacant': '—',
                'move_in_str': move_in_date.strftime('%m/%d/%y') if pd.notna(move_in_date) else '—',
                'days_to_be_ready': '—',
                'nvm': row.get('Nvm', '—')
            }
            render_unit_row(unit)
    else:
        st.info("No move-ins tomorrow")

# Create Move Activity section
move_activity_section = create_simple_section(
    title="Move Activity",
    icon="🚚",
    tabs=[
        ("Move-Outs Today+", render_move_outs_today),
        ("Move-Ins Tomorrow", render_move_ins_tomorrow)
    ]
)

# Prepare context
move_context = {
    'units_df': units_df,
    'today': datetime.now().date()
}

# Render Move Activity section
render_section(move_activity_section, move_context)

st.divider()


# --- Walk of the Day Section ---

# Load Task sheet
try:
    tasks_df = load_task_sheet()
except Exception as e:
    tasks_df = pd.DataFrame()
    log_event("WARNING", f"Could not load tasks: {e}")

# Render Walk of the Day section
from core.task_logic import get_yesterday_tasks
from ui.task_cards import render_all_tasks

st.markdown("""
<div style="background: var(--gray-100); border: 2px solid var(--gray-400); border-radius: var(--radius-lg); padding: var(--spacing-xl); margin-bottom: 2rem; box-shadow: var(--shadow-xl);">
    <h3 style="color: var(--gray-900); margin-top: 0; margin-bottom: 1.25rem; font-size: 1.5rem;">🚶 Walk of the Day</h3>
""", unsafe_allow_html=True)

if not tasks_df.empty:
    # Get yesterday's tasks grouped by type
    yesterday_tasks = get_yesterday_tasks(tasks_df)
    
    # Render all tasks in hierarchical structure
    render_all_tasks(yesterday_tasks, units_df)
else:
    st.warning("Task sheet not available")

st.markdown('</div>', unsafe_allow_html=True)

st.divider()
# --- Phase Overview Section ---
st.markdown("""
<div style="background: var(--gray-100); border: 2px solid var(--gray-400); border-radius: var(--radius-lg); padding: var(--spacing-xl); margin-bottom: 2rem; box-shadow: var(--shadow-xl);">
    <h3 style="color: var(--gray-900); margin-top: 0; margin-bottom: 1.25rem; font-size: 1.5rem;">🧱 Phase Overview</h3>
""", unsafe_allow_html=True)

# Expand/Collapse controls
expand_all, collapse_all = render_expand_collapse_controls(
    section_name="phases",
    key_prefix="phase_overview"
)

st.divider()

today = datetime.now().date()
phase_data = build_phase_overview(units_df, today=today)

# Render phase cards
if phase_data:
    for phase in phase_data:
        # Determine if this phase should be expanded
        is_expanded = get_expanded_state(
            default=False,
            expand_all=expand_all,
            collapse_all=collapse_all
        )
        render_phase_expander(phase, expanded=is_expanded)
else:
    st.info("No phase data available.")

st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# --- All Units Section ---
st.markdown("""
<div style="background: var(--gray-100); border: 2px solid var(--gray-400); border-radius: var(--radius-lg); padding: var(--spacing-xl); margin-bottom: 2rem; box-shadow: var(--shadow-xl);">
    <h3 style="color: var(--gray-900); margin-top: 0; margin-bottom: 1.25rem; font-size: 1.5rem;">📋 All Units</h3>
""", unsafe_allow_html=True)

all_units = build_all_units(units_df)

with st.expander(f"📋 View All Units ({len(all_units)} total)", expanded=False):
    for idx, unit in enumerate(all_units):
        render_unit_row(unit)
        if idx < len(all_units) - 1:
            st.divider()

st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.divider()
st.caption("© 2025 Thousand Oaks | Local MVP | Internal Use Only")

log_event("INFO", "Dashboard page loaded successfully")
