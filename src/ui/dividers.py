"""
ui/dividers.py
---------------------------------------------------------
Consistent section breaks and visual separators.
---------------------------------------------------------
"""

import streamlit as st


def render_divider(style: str = "default") -> None:
    """
    Render a visual divider.
    
    Args:
        style: One of "default", "thick", "dotted"
    """
    if style == "thick":
        st.markdown('<div style="border-bottom: 2px solid var(--gray-500); margin: 1rem 0;"></div>', unsafe_allow_html=True)
    elif style == "dotted":
        st.markdown('<div style="border-bottom: 1px dotted var(--gray-500); margin: 0.5rem 0;"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="border-bottom: 1px solid var(--gray-500); margin: 0.5rem 0; opacity: 0.6;"></div>', unsafe_allow_html=True)


def render_section_header(title: str, emoji: str = "") -> None:
    """
    Render a section header with consistent styling.
    
    Args:
        title: Section title text
        emoji: Optional emoji prefix
    """
    st.markdown(f"""
    <h3 style="color: var(--gray-900); margin-top: 1rem; margin-bottom: 1rem; font-size: 1.5rem;">
        {emoji} {title}
    </h3>
    """, unsafe_allow_html=True)
