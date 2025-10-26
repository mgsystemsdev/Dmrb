"""
ui/expanders.py
---------------------------------------------------------
Hierarchical Phase → Building → Unit display components.
Renders nested collapsible sections for data exploration.
---------------------------------------------------------
"""

import streamlit as st
from utils.constants import NVM_EMOJI_MAP

def render_unit_row(unit: dict) -> None:
    """
    Render a single, compact unit row with Nvm at the end.

    Args:
        unit: Dictionary with keys: unit_num, status_emoji, move_out_str, days_vacant,
              move_in_str, days_to_be_ready, nvm
    """
    nvm_text = unit.get('nvm', '—')
    nvm_normalized = str(nvm_text).lower().strip()
    nvm_emoji = NVM_EMOJI_MAP.get(nvm_normalized, '🟢')
    
    st.markdown(f"""
<div class='unit-card'>
  <div class='row-grid' style='grid-template-columns: 1.1fr 1fr 0.9fr 1fr 0.9fr 1fr;'>
    <div>
      <div class='meta-value'>{unit['unit_num']}</div>
    </div>
    <div style='text-align:center;'>
      <div class='meta-label'>Move Out</div>
      <div class='meta-value' style='font-weight:600;'>{unit['move_out_str']}</div>
    </div>
    <div style='text-align:center;'>
      <div class='meta-label'>Days Vac</div>
      <div class='meta-value'>{unit['days_vacant']}</div>
    </div>
    <div style='text-align:center;'>
      <div class='meta-label'>Move In</div>
      <div class='meta-value' style='font-weight:600;'>{unit['move_in_str']}</div>
    </div>
    <div style='text-align:center;'>
      <div class='meta-label'>Days Ready</div>
      <div class='meta-value'>{unit['days_to_be_ready']}</div>
    </div>
    <div style='text-align:center;'>
      <div class='meta-label'>Nvm</div>
      <div class='meta-value'>{nvm_emoji} {nvm_text}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

def render_building_expander(building: dict, expanded: bool = False) -> None:
    """
    Render a building expander with NVM classification counts.

    Args:
        building: Dictionary with keys: label, total_units, notice_count, vacant_count, move_in_count, vacant_units, move_events
        expanded: Whether expander starts open (default: False)
    """
    notice = building.get('notice_count', 0)
    vacant = building.get('vacant_count', 0)
    move_in = building.get('move_in_count', 0)
    
    building_label = f"🏢 {building['label']} — {building['total_units']} units | 📢 Notice {notice} | 🟢 Vacant {vacant} | 🔴 Move-In {move_in}"
    with st.expander(building_label, expanded=expanded):
        # Vacant units section
        if building.get('vacant_units'):
            with st.expander(f"🔴 Vacant Units ({len(building['vacant_units'])})", expanded=False):
                for unit in building['vacant_units']:
                    render_unit_row(unit)
        else:
            st.markdown("---")

        # Move events section
        move_events = building.get('move_events', [])
        with st.expander(f"📅 Today's Moves ({len(move_events)})", expanded=False):
            if move_events:
                for event in move_events:
                    st.markdown(f"- {event}")
            else:
                st.markdown("---")

def render_phase_expander(phase: dict, expanded: bool = False) -> None:
    """
    Render a phase expander with buildings.

    Args:
        phase: Dictionary with keys: phase_label, buildings
        expanded: Whether expander starts open (default: False)
    """
    with st.expander(f"🧱 {phase['phase_label']}", expanded=expanded):
        if phase.get('buildings'):
            for idx, building in enumerate(phase['buildings']):
                render_building_expander(building)

                # Divider between buildings (not after last)
                if idx < len(phase['buildings']) - 1:
                    st.markdown('<div class="hairline"></div>', unsafe_allow_html=True)
        else:
            st.markdown("---")
