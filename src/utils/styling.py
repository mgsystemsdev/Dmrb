import os
import streamlit as st
from pathlib import Path

from core.logger import log_event


# ============================================================================
# STANDARD CONTAINER STYLES
# ============================================================================

def render_section_container_start(title: str, icon: str = "") -> None:
    """
    Render the start of a standard section container.
    
    Args:
        title: Section title text
        icon: Optional emoji icon
    
    Usage:
        render_section_container_start("Key Metrics", "📊")
        # ... content ...
        render_section_container_end()
    """
    title_text = f"{icon} {title}" if icon else title
    st.markdown(f"""
<div style="background: var(--gray-100); border: 2px solid var(--gray-400); border-radius: var(--radius-lg); padding: var(--spacing-xl); margin-bottom: 2rem; box-shadow: var(--shadow-xl);">
    <h3 style="color: var(--gray-900); margin-top: 0; margin-bottom: 1.25rem; font-size: 1.5rem;">{title_text}</h3>
""", unsafe_allow_html=True)


def render_section_container_end() -> None:
    """Render the end of a standard section container."""
    st.markdown('</div>', unsafe_allow_html=True)


def inject_css(path: str = None) -> None:
    """
    Inject a CSS file into the Streamlit app.
    Loads styles.css from same directory by default, logs results,
    and fails gracefully with a warning if the file isn't found.
    """
    try:
        # Resolve CSS path relative to this file if not provided
        if path is None:
            css_path = Path(__file__).parent / "styles.css"
        else:
            css_path = Path(path)
        
        if not css_path.exists():
            log_event("WARNING", f"[styling] CSS file not found at: {css_path}")
            return

        with open(css_path, "r", encoding="utf-8") as css_file:
            css = css_file.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
            log_event("INFO", f"[styling] CSS loaded from {css_path}")

    except Exception as e:
        log_event("ERROR", f"[styling] Error injecting CSS: {e}")
