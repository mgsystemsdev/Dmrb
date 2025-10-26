import os
import streamlit as st
from pathlib import Path

from core.logger import log_event


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
