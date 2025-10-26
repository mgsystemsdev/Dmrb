"""
pages/2_🏢_Units.py
---------------------------------------------------------
Units Lifecycle Page: mirrors Dashboard's phase styling.
Renders Phase → Building → Unit hierarchy and lifecycle tabs.
Relies on core calculators and shared UI components.
---------------------------------------------------------
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path
import re
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.data_loader import load_units_sheet, load_task_sheet
from core.data_logic import compute_all_unit_fields
from utils.constants import EXCEL_FILE_PATH, TOTAL_UNITS, NVM_EMOJI_MAP
from ui.unit_cards import render_unit_kpi_cards
from ui.expanders import render_unit_row
from ui.sections import create_simple_section, render_section
from core.logger import log_event
from utils.styling import inject_css, render_section_container_start, render_section_container_end
from ui.refresh_controls import render_refresh_controls
from ui.unit_viewmodels import build_enhanced_unit

# --- Page Setup ---
st.set_page_config(
    page_title="Units Lifecycle | Thousand Oaks",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Inject Global CSS ---
inject_css()

# --- Load Data ---
try:
    units_df = load_units_sheet(EXCEL_FILE_PATH)
    column_mapping = {
        'Move-out': 'move_out',
        'Move-in': 'move_in',
        'Unit': 'unit_number',
        'Unit id': 'unit_id',  # Full path like P-5 / Bld-1 / U-210
        'Phases': 'phase',
        'Building': 'building',
        'Status': 'status'  # Map Status column for lifecycle calculation
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
    render_refresh_controls(key_prefix="units", auto_refresh=True)

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
not_ready_units = units_df['lifecycle_label'].isin(['Not Ready']).sum() if 'lifecycle_label' in units_df.columns else 0

kpi_metrics = {
    'total_units': total_units,
    'vacant_units': vacant_units,
    'occupied_units': occupied_units,
    'occupancy_pct': occupancy_pct,
    'vacancy_pct': vacancy_pct,
    'avg_days_vacant': avg_days_vacant,
    'active_turns': active_turns,
    'units_ready': units_ready,
    'not_ready_units': not_ready_units
}

render_section_container_start("Key Performance Indicators", "📊")
render_unit_kpi_cards(kpi_metrics)
render_section_container_end()

st.divider()

# --- Lifecycle Breakdown Section ---
render_section_container_start("Lifecycle Status Breakdown", "🔄")

# Calculate lifecycle counts
lifecycle_counts = units_df['lifecycle_label'].value_counts()
ready_count = lifecycle_counts.get('Ready', 0)
in_turn_count = lifecycle_counts.get('In Turn', 0)
not_ready_count = lifecycle_counts.get('Not Ready', 0)
total_count = len(units_df)

# Calculate percentages
ready_pct = (ready_count / total_count * 100) if total_count > 0 else 0
in_turn_pct = (in_turn_count / total_count * 100) if total_count > 0 else 0
not_ready_pct = (not_ready_count / total_count * 100) if total_count > 0 else 0

# Render lifecycle status cards
col_a, col_b, col_c = st.columns(3, gap="medium")

with col_a:
    st.metric("✅ Ready", f"{ready_count} units", f"{ready_pct:.0f}%")

with col_b:
    st.metric("🔧 In Turn", f"{in_turn_count} units", f"{in_turn_pct:.0f}%")

with col_c:
    st.metric("⚠️ Not Ready", f"{not_ready_count} units", f"{not_ready_pct:.0f}%")

render_section_container_end()
st.divider()

"""
# NVM vs Lifecycle Cards: render cards if there are any NVM statuses;
# otherwise, skip the section entirely to avoid an empty container.
"""

# Build card-style distribution by NVM status
nvm_series = units_df.get('nvm', pd.Series(dtype=str)).fillna('').astype(str)
lifecycle_series = units_df.get('lifecycle_label', pd.Series(dtype=str)).fillna('Not Ready').astype(str)

# Normalize for grouping
nvm_norm = nvm_series.str.lower().str.strip()

# Preserve appearance order of NVM statuses and skip blanks
seen = []
for val in nvm_series:
    key = str(val).lower().strip()
    if key and key not in seen:
        seen.append(key)

if len(seen) > 0:
    render_section_container_start("NVM Status vs Lifecycle Distribution", "🧩")

    def pretty_label(key: str) -> str:
        raw = key.strip()
        display = raw.upper() if raw else 'UNKNOWN'
        emoji = NVM_EMOJI_MAP.get(key, '')
        return f"{emoji} {display}".strip()

    # Render cards in rows of 3
    cards_per_row = 3
    for i in range(0, len(seen), cards_per_row):
        batch = seen[i:i + cards_per_row]
        cols = st.columns(len(batch), gap="small")
        for col, status_key in zip(cols, batch):
            with col:
                mask = (nvm_norm == status_key)
                total = int(mask.sum())
                ready = int(((lifecycle_series == 'Ready') & mask).sum())
                in_turn = int(((lifecycle_series == 'In Turn') & mask).sum())
                not_ready = int(((lifecycle_series == 'Not Ready') & mask).sum())

                st.markdown(
                    f"""
                    <div style="border: 1px solid var(--gray-400); border-radius: var(--radius-md); padding: 0.75rem; background: var(--gray-050);">
                        <div style="font-weight: 700; color: var(--gray-900); margin-bottom: 0.5rem;">{pretty_label(status_key)}</div>
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem;">
                            <div><div style="font-size: 0.75rem; color: var(--gray-700);">Ready</div><div style="font-weight:700;">{ready}</div></div>
                            <div><div style="font-size: 0.75rem; color: var(--gray-700);">In Turn</div><div style="font-weight:700;">{in_turn}</div></div>
                            <div><div style="font-size: 0.75rem; color: var(--gray-700);">Not Ready</div><div style="font-weight:700;">{not_ready}</div></div>
                            <div><div style="font-size: 0.75rem; color: var(--gray-700);">Total</div><div style="font-weight:700;">{total}</div></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    render_section_container_end()

st.divider()

# (build_enhanced_unit moved to ui/unit_viewmodels)

# --- Render Helper: Phase > Building > Units ---
def render_units_by_hierarchy(units_subset, tasks_df, title_prefix=""):
    """Render units grouped by Phase > Building with nested expanders."""
    if len(units_subset) == 0:
        st.info("No units to display")
        return

    # Helpers to safely handle mixed string/numeric identifiers like "Phase_5"
    def _safe_numeric_label(value) -> str:
        """Return a human-friendly numeric label if digits exist, else the raw string."""
        try:
            return str(int(value))
        except Exception:
            s = str(value)
            m = re.search(r"\d+", s)
            return m.group(0) if m else s

    def _numeric_sort_key(value):
        """Sort primarily by first integer found, else by string value."""
        s = str(value)
        m = re.search(r"\d+", s)
        if m:
            return (0, int(m.group(0)))
        return (1, s)

    # Content only - no wrapper
    st.caption(f"**{len(units_subset)} units** {title_prefix}")
    st.divider()

    for phase in sorted(units_subset['phase'].dropna().unique(), key=_numeric_sort_key):
        phase_units = units_subset[units_subset['phase'] == phase]

        # Phase expander
        with st.expander(f"🧱 Phase {_safe_numeric_label(phase)} — {len(phase_units)} units", expanded=False):
            for building in sorted(phase_units['building'].dropna().unique(), key=_numeric_sort_key):
                building_units = phase_units[phase_units['building'] == building]
                
                # Calculate building stats
                nvm_norm = building_units['nvm'].fillna('').astype(str).str.lower()
                vacant_count = nvm_norm.isin(['vacant', 'smi']).sum()
                occupied_count = len(building_units) - vacant_count

                # Building expander inside phase
                with st.expander(f"🏢 Building {_safe_numeric_label(building)} — {len(building_units)} units | 🟥 {occupied_count} occ | 🟩 {vacant_count} vac", expanded=False):
                    # Each unit in its own row with a subtle hairline between rows
                    for idx, (_, unit_row) in enumerate(building_units.iterrows()):
                        render_unit_row(build_enhanced_unit(unit_row, tasks_df))
                        if idx < len(building_units) - 1:  # No divider after last unit
                            st.markdown('<div class="hairline"></div>', unsafe_allow_html=True)


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
        # Notice = nvm contains 'notice' (includes NOTICE and NOTICE + SMI)
        nvm_norm = units_df['nvm'].fillna('').astype(str).str.lower()
        notice = units_df[nvm_norm.str.contains('notice', na=False)].copy()
        notice = notice.sort_values('days_vacant', ascending=False, na_position='last')
        render_units_by_hierarchy(notice, tasks_df, "on notice")

    with nvm_tabs[1]:
        # Vacant = nvm column contains 'vacant' or 'smi'
        nvm_norm = units_df['nvm'].fillna('').astype(str).str.lower()
        vacant = units_df[nvm_norm.isin(['vacant', 'smi'])].copy()
        vacant = vacant.sort_values('days_vacant', ascending=False, na_position='last')
        render_units_by_hierarchy(vacant, tasks_df, "vacant")

    with nvm_tabs[2]:
        # Moving = 72-hour hold after move-in (from move-in day through day 3)
        move_in_dates = pd.to_datetime(units_df['move_in'], errors='coerce')
        now = datetime.now()
        past_72h = now - timedelta(hours=72)
        moving = units_df[(move_in_dates <= now) & (move_in_dates >= past_72h)].copy()
        
        # Add time remaining in 72h window
        if len(moving) > 0:
            moving_with_time = []
            for idx, row in moving.iterrows():
                mi = pd.to_datetime(row['move_in'])
                hours_since = (now - mi).total_seconds() / 3600
                hours_remaining = 72 - hours_since
                days_remaining = int(hours_remaining / 24)
                hours_rem = int(hours_remaining % 24)
                moving_with_time.append({
                    'unit': row.get('unit_number', 'N/A'),
                    'time_display': f"Day {3 - days_remaining} of 3 ({hours_rem}h remaining)"
                })
        
        moving = moving.sort_values('move_in', ascending=False, na_position='last')
        
        st.caption(f"**{len(moving)} units** in 72-hour post-move-in hold")
        st.info("💡 Units remain in 'Moving' status for 72 hours (3 days) after move-in date")
        st.divider()
        
        if len(moving) > 0:
            render_units_by_hierarchy(moving, tasks_df, "in 72h hold period")
        else:
            st.info("No units currently in 72-hour move-in hold period")

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

render_section_container_start("Units Overview", "🏠")
render_section(units_section, context)
render_section_container_end()

st.divider()

# --- Footer KPIs ---
render_section_container_start("Performance Summary", "📈")

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

render_section_container_end()

st.divider()
st.caption("© 2025 Thousand Oaks | Units Lifecycle")

log_event("INFO", "Units page loaded")
