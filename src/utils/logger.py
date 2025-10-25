import os
import datetime
from pathlib import Path

# Optional: mirror logs in Streamlit if running in that environment
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def _get_log_path() -> Path:
    """Return today's log file path."""
    today = datetime.date.today().strftime("%Y%m%d")
    return LOG_DIR / f"app_{today}.log"


def log_event(level: str, message: str) -> None:
    """
    Log an event to console, file, and Streamlit (if available).
    Format: 2025-10-23 14:32:10 | INFO | message
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | {level.upper():<5} | {message}"

    # --- Console ---
    print(line)

    # --- File ---
    with open(_get_log_path(), "a", encoding="utf-8") as log_file:
        log_file.write(line + "\n")

    # --- Streamlit Mirror (if running in app) ---
    # Suppress INFO-level output in the UI to avoid noisy banners.
    # Only surface warnings and errors to the Streamlit interface.
    if STREAMLIT_AVAILABLE:
        level_up = level.upper()
        if level_up in ("WARN", "WARNING"):
            st.warning(message)
        elif level_up == "ERROR":
            st.error(message)
