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
from utils.constants import EXCEL_FILE_PATH, TOTAL_UNITS
from utils.timers import render_refresh_controls
from ui.hero_cards import render_kpi_card, render_kpi_card_with_progress
from ui.expanders import render_phase_expander, render_unit_row
from ui.dividers import render_section_header
from ui.toggle_controls import render_expand_collapse_controls, get_expanded_state
from ui.sections import create_simple_section, render_section
from ui.refresh_controls import render_refresh_controls
from core.logger import log_event

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
    units_df = load_units_sheet(EXCEL_FILE_PATH)
    # Compute lifecycle labels and other derived fields
    column_mapping = {
        'Move-out': 'move_out',
        'Move-in': 'move_in',
        'Nvm': 'nvm',
        'Unit': 'unit_id',
        'Phases': 'phase',
        'Building': 'building'
    }
    units_df = units_df.rename(columns=column_mapping)
    units_df = compute_all_unit_fields(units_df)
    # Rename back for compatibility
    units_df = units_df.rename(columns={
        'move_out': 'Move-out',
        'move_in': 'Move-in',
        'nvm': 'Nvm',
        'unit_id': 'Unit',
        'phase': 'Phases',
        'building': 'Building'
    })
except Exception as e:
    st.error(f"❌ Failed to load Excel data: {e}")
    st.stop()

# --- Validate Required Columns ---
required_cols = ["Nvm", "Unit", "Phases", "Building", "Move-out", "Move-in"]
missing_cols = [col for col in required_cols if col not in units_df.columns]
if missing_cols:
    st.error(f"❌ Missing required columns: {missing_cols}")
    st.stop()

# --- Vacancy Calculation ---
nvm_normalized = units_df["Nvm"].fillna("").astype(str).str.strip().str.lower()
vacant_units = nvm_normalized.isin(["vacant", "smi"]).sum()

# --- Occupancy Calculation ---
occupied_units = TOTAL_UNITS - vacant_units
occupancy_pct = round((occupied_units / TOTAL_UNITS) * 100, 1) if TOTAL_UNITS else 0

# --- Sidebar Controls ---
with st.sidebar:
    st.header("🔍 Controls")
    
    if st.button("🔄 Refresh Data", use_container_width=True, key="dash_refresh"):
        st.cache_data.clear()
        log_event("INFO", "Dashboard data cache cleared")
        st.rerun()
    
    st.divider()
    
    st.markdown(f"""
    **Last Updated:**  
    {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    **Data Source:**  
    `{EXCEL_FILE_PATH}`
    """)
    
    st.divider()
    
    st.markdown("**Suggested Refresh:**")
    st.caption("Every 5 minutes")

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
                'days_to_rent': '—',
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
                'days_to_rent': '—',
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
    tasks_df = load_task_sheet(EXCEL_FILE_PATH)
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

# Calculate phase data
phase_data = []
today = datetime.now().date()

for phase in sorted(units_df['Phases'].dropna().unique()):
    phase_units = units_df[units_df['Phases'] == phase].copy()
    
    buildings = []
    for building in sorted(phase_units['Building'].dropna().unique(), key=str):
        building_units = phase_units[phase_units['Building'] == building]
        
        # Calculate vacant/occupied
        nvm_norm = building_units['Nvm'].fillna('').astype(str).str.strip().str.lower()
        vacant_mask = nvm_norm.isin(['vacant', 'smi'])
        vacant = int(vacant_mask.sum())
        total = len(building_units)
        occupied = total - vacant
        
        # Get vacant unit details
        vacant_units_list = []
        for _, row in building_units[vacant_mask].iterrows():
            unit_num = str(row.get('Unit', '')).strip()
            
            # Move-out date and days vacant
            move_out = pd.to_datetime(row.get('Move-out'), errors='coerce')  # type: ignore
            if pd.notna(move_out):
                days_vacant = (datetime.now() - move_out).days  # type: ignore
                move_out_str = move_out.strftime('%m/%d/%y')  # type: ignore
            else:
                days_vacant = '—'
                move_out_str = '—'
            
            # Move-in date and days to rent
            move_in = pd.to_datetime(row.get('Move-in'), errors='coerce')  # type: ignore
            if pd.notna(move_in):
                days_to_rent = (move_in - datetime.now()).days  # type: ignore
                move_in_str = move_in.strftime('%m/%d/%y')  # type: ignore
            else:
                days_to_rent = '—'
                move_in_str = '—'
            
            lifecycle = row.get('lifecycle_label', 'Not Ready')
            
            vacant_units_list.append({
                'unit_num': unit_num,
                'status_emoji': '🔴',
                'move_out_str': move_out_str,
                'days_vacant': days_vacant,
                'move_in_str': move_in_str,
                'days_to_rent': days_to_rent,
                'lifecycle_label': lifecycle
            })
        
        # Move events for THIS building only
        move_events = []
        
        # Check move-outs
        if 'Move-out' in building_units.columns:
            move_out_dates = pd.to_datetime(building_units['Move-out'], errors='coerce')
            for _, row in building_units[move_out_dates.dt.date == today].iterrows():
                unit_label = str(row.get('Unit', '')).strip()
                move_date = row['Move-out'].strftime('%Y-%m-%d') if pd.notna(row['Move-out']) else ''  # type: ignore
                if unit_label and move_date:
                    move_events.append(f"🟥 Unit {unit_label} - Move Out {move_date}")
        
        # Check move-ins
        if 'Move-in' in building_units.columns:
            move_in_dates = pd.to_datetime(building_units['Move-in'], errors='coerce')
            for _, row in building_units[move_in_dates.dt.date == today].iterrows():
                unit_label = str(row.get('Unit', '')).strip()
                move_date = row['Move-in'].strftime('%Y-%m-%d') if pd.notna(row['Move-in']) else ''  # type: ignore
                if unit_label and move_date:
                    move_events.append(f"🟩 Unit {unit_label} - Move In {move_date}")
        
        buildings.append({
            'label': f'B{building}',
            'total_units': total,
            'vacant': vacant,
            'occupied': occupied,
            'move_events': move_events,
            'vacant_units': vacant_units_list
        })
    
    # Safe phase label generation
    try:
        phase_label = f'Phase {int(phase)}'
    except (ValueError, TypeError):
        phase_label = f'Phase {phase}'
    
    phase_data.append({
        'phase_label': phase_label,
        'buildings': buildings
    })

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

# Process all units and sort by days vacant
all_units = []
for idx, unit_row in units_df.iterrows():
    unit_num = str(unit_row.get('Unit', '')).strip()
    if not unit_num:
        continue
    
    # Move-out date and days vacant
    move_out = pd.to_datetime(unit_row.get('Move-out'), errors='coerce')  # type: ignore
    if pd.notna(move_out):
        days_vacant = (datetime.now() - move_out).days  # type: ignore
        days_vacant_sort = days_vacant
        move_out_str = move_out.strftime('%m/%d/%y')  # type: ignore
    else:
        days_vacant = '—'
        days_vacant_sort = -1
        move_out_str = '—'
    
    # Move-in date and days to rent
    move_in = pd.to_datetime(unit_row.get('Move-in'), errors='coerce')  # type: ignore
    if pd.notna(move_in):
        days_to_rent = (move_in - datetime.now()).days  # type: ignore
        move_in_str = move_in.strftime('%m/%d/%y')  # type: ignore
    else:
        days_to_rent = '—'
        move_in_str = '—'
    
    # Determine vacancy status
    nvm_val = str(unit_row.get('Nvm', '')).strip().lower()
    status_emoji = "🔴" if nvm_val in ['vacant', 'smi'] else "🟢"
    
    all_units.append({
        'unit_num': unit_num,
        'status_emoji': status_emoji,
        'move_out_str': move_out_str,
        'days_vacant': days_vacant,
        'days_vacant_sort': days_vacant_sort,
        'move_in_str': move_in_str,
        'days_to_rent': days_to_rent,
        'nvm': unit_row.get('Nvm', '—')
    })

# Sort by days vacant (descending - oldest first)
all_units.sort(key=lambda x: x['days_vacant_sort'], reverse=True)

with st.expander(f"📋 View All Units ({len(all_units)} total)", expanded=False):
    for unit in all_units:
        render_unit_row(unit)

st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.divider()
st.caption("© 2025 Thousand Oaks | Local MVP | Internal Use Only")

log_event("INFO", "Dashboard page loaded successfully")
