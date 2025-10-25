"""
ui/task_cards.py
---------------------------------------------------------
Task rendering components for Walk Today section.
---------------------------------------------------------
"""

import streamlit as st
from typing import Dict, List


def render_task_unit_row(unit_data: dict) -> None:
    """
    Render a single unit row for task display.
    
    Args:
        unit_data: Dict with keys: unit, unit_id, vendor, status
    """
    col1, col2, col3, col4 = st.columns([1, 2, 1.5, 1])
    
    with col1:
        st.markdown(f"<small><strong>Unit {unit_data.get('unit', 'N/A')}</strong></small>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<small>{unit_data.get('unit_id', '—')}</small>", unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"<small>Vendor: {unit_data.get('vendor', '—')}</small>", unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"<small>Status: {unit_data.get('status', '—')}</small>", unsafe_allow_html=True)


def render_task_hierarchy(task_name: str, hierarchy: Dict[str, Dict[str, List[Dict]]]) -> None:
    """
    Render task hierarchy: Phase → Building → Unit.
    
    Args:
        task_name: Name of the task type
        hierarchy: Nested dict {phase: {building: [units]}}
    """
    if not hierarchy:
        st.info(f"No {task_name} tasks to walk today")
        return
    
    total_units = sum(len(units) for phase_data in hierarchy.values() for units in phase_data.values())
    
    with st.expander(f"🔧 {task_name} — {total_units} units", expanded=False):
        for phase in sorted(hierarchy.keys()):
            phase_data = hierarchy[phase]
            phase_total = sum(len(units) for units in phase_data.values())
            
            st.markdown(f"**🧱 Phase {phase}** — {phase_total} units")
            
            for building in sorted(phase_data.keys()):
                units = phase_data[building]
                
                with st.expander(f"🏢 Building {building} — {len(units)} units", expanded=False):
                    for idx, unit_data in enumerate(units):
                        render_task_unit_row(unit_data)
                        if idx < len(units) - 1:
                            st.divider()
            
            st.divider()


def render_all_tasks(tasks_by_type: Dict[str, any], units_df: any) -> None:
    """
    Render all task types in one main expander.
    
    Args:
        tasks_by_type: Dict mapping task type to DataFrame
        units_df: Units DataFrame for context
    """
    from core.task_logic import group_tasks_by_hierarchy
    
    total_tasks = sum(len(df) for df in tasks_by_type.values())
    
    with st.expander(f"✅ Tasks to Walk Today — {total_tasks} total", expanded=True):
        if not tasks_by_type:
            st.info("No tasks to walk today")
            return
        
        for task_name, tasks_df in tasks_by_type.items():
            hierarchy = group_tasks_by_hierarchy(tasks_df)
            render_task_hierarchy(task_name, hierarchy)
