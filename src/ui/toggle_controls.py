"""
ui/toggle_controls.py
---------------------------------------------------------
Global collapse/expand controls for hierarchical views.
Provides buttons to expand/collapse all sections at once.
---------------------------------------------------------
"""

import streamlit as st


def render_expand_collapse_controls(
    section_name: str = "sections",
    key_prefix: str = "toggle"
) -> tuple[bool, bool]:
    """
    Render expand all / collapse all buttons.
    
    Args:
        section_name: Name of sections being controlled (e.g., "phases", "units")
        key_prefix: Unique prefix for button keys
    
    Returns:
        Tuple of (expand_all_clicked, collapse_all_clicked)
    """
    col1, col2 = st.columns(2, gap="small")
    
    with col1:
        expand_all = st.button(
            f"📂 Expand All {section_name.title()}",
            use_container_width=True,
            key=f"{key_prefix}_expand_all"
        )
    
    with col2:
        collapse_all = st.button(
            f"📁 Collapse All {section_name.title()}",
            use_container_width=True,
            key=f"{key_prefix}_collapse_all"
        )
    
    return expand_all, collapse_all


def get_expanded_state(
    default: bool = False,
    expand_all: bool = False,
    collapse_all: bool = False
) -> bool:
    """
    Determine if a section should be expanded based on button clicks.
    
    Args:
        default: Default expanded state
        expand_all: Whether expand all was clicked
        collapse_all: Whether collapse all was clicked
    
    Returns:
        Boolean indicating if section should be expanded
    """
    if expand_all:
        return True
    elif collapse_all:
        return False
    else:
        return default


def render_filter_toggle(
    label: str,
    key: str,
    default: bool = True,
    emoji: str = ""
) -> bool:
    """
    Render a simple toggle filter.
    
    Args:
        label: Toggle label
        key: Unique key
        default: Default state
        emoji: Optional emoji prefix
    
    Returns:
        Boolean state of toggle
    """
    return st.checkbox(
        f"{emoji} {label}" if emoji else label,
        value=default,
        key=key
    )


def render_view_options(key_prefix: str = "view") -> dict:
    """
    Render common view options (show/hide elements).
    
    Args:
        key_prefix: Unique prefix for option keys
    
    Returns:
        Dictionary with view option states
    """
    with st.expander("⚙️ View Options", expanded=False):
        options = {}
        
        options['show_vacant_only'] = st.checkbox(
            "🔴 Show Vacant Units Only",
            value=False,
            key=f"{key_prefix}_vacant_only"
        )
        
        options['show_move_events'] = st.checkbox(
            "📅 Show Move Events",
            value=True,
            key=f"{key_prefix}_move_events"
        )
        
        options['show_days_vacant'] = st.checkbox(
            "⏱️ Show Days Vacant",
            value=True,
            key=f"{key_prefix}_days_vacant"
        )
        
        options['compact_view'] = st.checkbox(
            "📋 Compact View",
            value=False,
            key=f"{key_prefix}_compact"
        )
        
        return options


def render_sort_controls(
    options: list[str],
    default: str = None,
    key: str = "sort_by"
) -> str:
    """
    Render sort dropdown.
    
    Args:
        options: List of sort options
        default: Default sort option
        key: Unique key
    
    Returns:
        Selected sort option
    """
    default_idx = 0
    if default and default in options:
        default_idx = options.index(default)
    
    return st.selectbox(
        "🔄 Sort By",
        options=options,
        index=default_idx,
        key=key
    )


def render_hierarchical_controls(
    section_name: str = "phases",
    key_prefix: str = "controls",
    show_view_options: bool = True,
    sort_options: list[str] = None
) -> dict:
    """
    Render complete set of hierarchical view controls.
    
    Args:
        section_name: Name of sections (e.g., "phases", "units")
        key_prefix: Unique prefix for all keys
        show_view_options: Whether to show view options
        sort_options: Optional list of sort options
    
    Returns:
        Dictionary with all control states
    """
    controls = {}
    
    # Expand/Collapse buttons
    expand_all, collapse_all = render_expand_collapse_controls(
        section_name=section_name,
        key_prefix=key_prefix
    )
    controls['expand_all'] = expand_all
    controls['collapse_all'] = collapse_all
    
    st.divider()
    
    # Sort controls
    if sort_options:
        controls['sort_by'] = render_sort_controls(
            options=sort_options,
            key=f"{key_prefix}_sort"
        )
    
    # View options
    if show_view_options:
        controls['view_options'] = render_view_options(key_prefix=key_prefix)
    
    return controls
