"""
ui/hero_cards.py
---------------------------------------------------------
KPI visualization components (top & footer cards).
Renders dashboard metrics in styled card layouts.
---------------------------------------------------------
"""

import streamlit as st


def render_kpi_card(label: str, value: str | int | float, subtitle: str = "", emoji: str = "") -> None:
    """
    Render a single KPI card with black & gray theme.
    
    Args:
        label: KPI label text
        value: KPI value to display
        subtitle: Optional subtitle text
        emoji: Optional emoji prefix
    """
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{emoji} {label}</div>
        <div class='kpi-value'>{value}</div>
        {f"<div class='kpi-subtitle'>{subtitle}</div>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def render_kpi_card_with_progress(label: str, value: float, max_value: float = 100, emoji: str = "") -> None:
    """
    Render a KPI card with a progress bar.
    
    Args:
        label: KPI label text
        value: Current value (percentage)
        max_value: Maximum value for progress calculation
        emoji: Optional emoji prefix
    """
    percentage = (value / max_value) * 100 if max_value > 0 else 0
    
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{emoji} {label}</div>
        <div class='kpi-value'>{value:.1f}%</div>
        <div class='kpi-progress'><div class='kpi-progress-fill' style='width: {percentage}%;'></div></div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_row(kpis: list[dict]) -> None:
    """
    Render a row of KPI cards.
    
    Args:
        kpis: List of KPI dictionaries with keys: label, value, subtitle (optional), emoji (optional)
    """
    cols = st.columns(len(kpis), gap="small")
    
    for col, kpi in zip(cols, kpis):
        with col:
            render_kpi_card(
                label=kpi.get("label", ""),
                value=kpi.get("value", ""),
                subtitle=kpi.get("subtitle", ""),
                emoji=kpi.get("emoji", "")
            )
