"""
ui/sections.py
---------------------------------------------------------
Scalable sections & tabs framework.
Makes it easy to add new sections and tabs to any page.
---------------------------------------------------------
"""

import streamlit as st
from typing import Callable, Any
from dataclasses import dataclass


@dataclass
class Tab:
    """
    A single tab within a section.
    
    Args:
        label: Tab label shown to user
        key: Unique identifier for this tab
        render: Function to render tab content, receives context dict
        icon: Optional emoji/icon prefix
    """
    label: str
    key: str
    render: Callable[[dict], None]
    icon: str = ""
    
    @property
    def display_label(self) -> str:
        """Get display label with icon."""
        return f"{self.icon} {self.label}" if self.icon else self.label


@dataclass
class TabRow:
    """
    A row of tabs (rendered with st.tabs).
    
    Args:
        tabs: List of Tab objects
        key: Unique key for this tab row
    """
    tabs: list[Tab]
    key: str


@dataclass
class Section:
    """
    A page section with title and one or more tab rows.
    
    Args:
        id: Unique section identifier
        title: Section title
        icon: Section emoji/icon
        rows: List of TabRow objects
        show_header: Whether to show section header
    """
    id: str
    title: str
    icon: str
    rows: list[TabRow]
    show_header: bool = True


def render_tab_row(tab_row: TabRow, context: dict, section_id: str = "") -> None:
    """
    Render a single row of tabs.
    
    Args:
        tab_row: TabRow object with tabs to render
        context: Context dictionary passed to render functions
        section_id: Optional section ID for state management
    """
    # Create tabs
    tab_labels = [tab.display_label for tab in tab_row.tabs]
    streamlit_tabs = st.tabs(tab_labels)
    
    # Render each tab
    for tab, streamlit_tab in zip(tab_row.tabs, streamlit_tabs):
        with streamlit_tab:
            try:
                tab.render(context)
            except Exception as e:
                st.error(f"Error rendering tab '{tab.label}': {e}")


def render_section(section: Section, context: dict) -> None:
    """
    Render a complete section with all its tab rows.
    
    Args:
        section: Section object to render
        context: Context dictionary passed to render functions
    """
    # Section header (thin divider style)
    if section.show_header:
        from utils.styling import render_section_container_start
        render_section_container_start(section.title, section.icon)
    
    # Render each tab row
    for tab_row in section.rows:
        render_tab_row(tab_row, context, section_id=section.id)
        
        # Add spacing between rows
        if len(section.rows) > 1:
            st.divider()


def render_sections(sections: list[Section], context: dict) -> None:
    """
    Render multiple sections in sequence.
    
    Args:
        sections: List of Section objects
        context: Shared context dictionary
    """
    for idx, section in enumerate(sections):
        render_section(section, context)
        
        # Add divider between sections (not after last)
        if idx < len(sections) - 1:
            st.divider()


# ============================================================================
# HELPER: Create common section patterns
# ============================================================================

def create_simple_section(
    title: str,
    icon: str,
    tabs: list[tuple[str, Callable]],
    section_id: str = None
) -> Section:
    """
    Create a simple section with one row of tabs.
    
    Args:
        title: Section title
        icon: Section icon/emoji
        tabs: List of (label, render_function) tuples
        section_id: Optional section ID (auto-generated if None)
    
    Returns:
        Section object ready to render
    
    Example:
        section = create_simple_section(
            title="Move Activity",
            icon="🚚",
            tabs=[
                ("Move-Outs", render_move_outs),
                ("Move-Ins", render_move_ins)
            ]
        )
    """
    if section_id is None:
        section_id = title.lower().replace(" ", "_")
    
    tab_objects = [
        Tab(label=label, key=f"{section_id}_{label.lower().replace(' ', '_')}", render=render_fn)
        for label, render_fn in tabs
    ]
    
    tab_row = TabRow(tabs=tab_objects, key=f"{section_id}_row")
    
    return Section(
        id=section_id,
        title=title,
        icon=icon,
        rows=[tab_row]
    )


def create_multi_row_section(
    title: str,
    icon: str,
    rows: list[list[tuple[str, Callable]]],
    section_id: str = None
) -> Section:
    """
    Create a section with multiple rows of tabs.
    
    Args:
        title: Section title
        icon: Section icon/emoji
        rows: List of rows, each row is a list of (label, render_function) tuples
        section_id: Optional section ID
    
    Returns:
        Section object
    
    Example:
        section = create_multi_row_section(
            title="Units Overview",
            icon="🏢",
            rows=[
                [("Vacant", render_vacant), ("Occupied", render_occupied)],
                [("Ready", render_ready), ("In Turn", render_in_turn)]
            ]
        )
    """
    if section_id is None:
        section_id = title.lower().replace(" ", "_")
    
    tab_rows = []
    for row_idx, row_tabs in enumerate(rows):
        tab_objects = [
            Tab(label=label, key=f"{section_id}_row{row_idx}_{label.lower().replace(' ', '_')}", 
                render=render_fn)
            for label, render_fn in row_tabs
        ]
        tab_rows.append(TabRow(tabs=tab_objects, key=f"{section_id}_row_{row_idx}"))
    
    return Section(
        id=section_id,
        title=title,
        icon=icon,
        rows=tab_rows
    )
