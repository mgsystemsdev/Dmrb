"""
ui/unit_cards.py
---------------------------------------------------------
Clean unit cards using Streamlit-native components only.
Professional, compact design for Community Cloud.
---------------------------------------------------------
"""

import streamlit as st

def render_enhanced_unit_row(unit: dict) -> None:
    """
    Render unit row in horizontal layout using columns - ultra compact with Status.

    Args:
        unit: Dictionary with unit data (unit_id, status_emoji, move_out, days_vacant, move_in, days_to_ready, status)
    """
    col1, col2, col3, col4, col5, col6 = st.columns([1.5, 1, 0.8, 1, 0.8, 1])

    with col1:
        st.markdown(f"<small>{unit.get('status_emoji', '🏠')} <strong>{unit.get('unit_id', 'N/A')}</strong></small>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<small><strong>Move Out</strong><br>{unit.get('move_out', '—')}</small>", unsafe_allow_html=True)

    with col3:
        st.markdown(f"<small><strong>Days Vac</strong><br>{unit.get('days_vacant', '—')}</small>", unsafe_allow_html=True)

    with col4:
        st.markdown(f"<small><strong>Move In</strong><br>{unit.get('move_in', '—')}</small>", unsafe_allow_html=True)

    with col5:
        st.markdown(f"<small><strong>Days Rent</strong><br>{unit.get('days_to_ready', '—')}</small>", unsafe_allow_html=True)
    
    with col6:
        status_text = unit.get('status', 'Not Ready')
        status_emoji_map = {
            'Ready': '✅',
            'In Turn': '🔧',
            'Not Ready': '⚠️'
        }
        status_emoji = status_emoji_map.get(status_text, '⚠️')
        st.markdown(f"<small><strong>Status</strong><br>{status_emoji} {status_text}</small>", unsafe_allow_html=True)

def render_unit_kpi_cards(metrics: dict) -> None:
    """
    Compact KPI cards using native Streamlit metrics.

    Args:
        metrics: Dictionary with KPI values
    """
    col1, col2, col3, col4 = st.columns(4, gap="small")

    with col1:
        st.metric("Total Units", f"{metrics.get('total_units', 0):,}")

    with col2:
        st.metric("Vacant", f"{metrics.get('vacant_units', 0):,}")

    with col3:
        st.metric("Occupied", f"{metrics.get('occupied_units', 0):,}")

    with col4:
        st.metric("Occupancy", f"{metrics.get('occupancy_pct', 0):.1f}%")

    # Second row
    col5, col6, col7, col8 = st.columns(4, gap="small")

    with col5:
        st.metric("Avg Days Vacant", f"{metrics.get('avg_days_vacant', 0):.1f}")

    with col6:
        st.metric("In Turn", f"{metrics.get('active_turns', 0):,}")

    with col7:
        st.metric("Ready", f"{metrics.get('units_ready', 0):,}")

    with col8:
        st.metric("Vacancy %", f"{metrics.get('vacancy_pct', 0):.1f}%")
