"""
utils/helpers.py
---------------------------------------------------------
Shared utility helpers for formatting, NVM normalization,
and small date computations used across pages and core.
---------------------------------------------------------
"""

from __future__ import annotations

from typing import Optional
import pandas as pd


def normalize_nvm(value: object) -> str:
    """Normalize NVM-like status strings to lower-case tokens."""
    if value is None:
        return ""
    return str(value).strip().lower()


def normalize_nvm_series(series: pd.Series) -> pd.Series:
    """Vectorized normalization for NVM columns."""
    return series.fillna("").astype(str).str.strip().str.lower()


def is_vacant(nvm_value: object) -> bool:
    """Return True if NVM value indicates vacancy (vacant or smi)."""
    n = normalize_nvm(nvm_value)
    return n in ("vacant", "smi")


def fmt_date(value: object, fmt: str = "%m/%d/%y") -> str:
    """Safely format a date-like value or return '—' if missing."""
    dt = pd.to_datetime(value, errors="coerce")
    if pd.notna(dt):
        return dt.strftime(fmt)
    return "—"


def days_between(later: object, earlier: object) -> Optional[int]:
    """Return integer day difference (later - earlier) or None on error."""
    try:
        d1 = pd.to_datetime(later)
        d2 = pd.to_datetime(earlier)
        if pd.isna(d1) or pd.isna(d2):
            return None
        return int((d1 - d2).days)
    except Exception:
        return None

