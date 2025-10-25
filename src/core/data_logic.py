"""
core/data_logic.py
---------------------------------------------------------
Phase 1: Unit-level computations for DMRB.
Adds derived fields to the Units DataFrame and
normalizes readiness / vacancy logic.
---------------------------------------------------------
"""

import pandas as pd
from datetime import datetime, timedelta, date
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import log_event


# =======================================================
# 🧩  BASIC TIME UTILITIES
# =======================================================
def _today() -> pd.Timestamp:
    """Standard reference date for all calculations."""
    return pd.Timestamp("today").normalize()


def _safe_days_between(date1, date2) -> int | None:
    """Return integer day difference, handling NaT/None."""
    try:
        d1 = pd.to_datetime(date1)
        d2 = pd.to_datetime(date2)
        if pd.isna(d1) or pd.isna(d2):
            return None
        return int((d1 - d2).days)
    except Exception:
        return None


# =======================================================
# 🧩  CORE COMPUTATIONS (PER-UNIT)
# =======================================================
def compute_days_vacant(row: pd.Series) -> int | None:
    """Days since move-out (vacancy age)."""
    move_out = row.get("move_out")
    return _safe_days_between(_today(), move_out)


def compute_days_to_be_ready(row: pd.Series) -> int | None:
    """Days remaining until scheduled move-in."""
    move_in = row.get("move_in")
    return _safe_days_between(move_in, _today())


def compute_turn_level(row: pd.Series) -> str:
    """
    Classify unit’s time status.
    Distinguishes between Ready (vacant aging)
    and Not Ready (turn progress).
    """
    days_vacant = row.get("days_vacant") or 0
    lifecycle = str(row.get("status", "")).lower()
    nvm = str(row.get("nvm", "")).lower()

    # Ready but still vacant
    if lifecycle == "ready" and nvm == "vacant":
        if days_vacant <= 8:
            return "Fresh Ready"
        elif days_vacant <= 15:
            return "Idle Ready"
        elif days_vacant <= 25:
            return "Aging Ready"
        else:
            return "Stale Ready"

    # Not Ready → Turn Performance
    if days_vacant <= 8:
        return "On Track"
    elif days_vacant <= 15:
        return "Lagging"
    elif days_vacant <= 25:
        return "Delayed"
    elif days_vacant <= 30:
        return "Critical"
    return "Exception"


def compute_unit_blocked(row: pd.Series) -> bool:
    """Placeholder: blocked if condition or comment flag implies hold."""
    comment = str(row.get("comments", "")).lower()
    return any(word in comment for word in ["hold", "blocked", "issue"])


def compute_lifecycle_label(row: pd.Series) -> str:
    """Map Status to lifecycle label: Ready, In Turn, or Not Ready."""
    status = str(row.get("status", "")).lower().strip()
    
    # Status = "ready" → Ready
    if status == "ready":
        return "Ready"
    
    # Status = work in progress → In Turn
    if status in ["currently work", "started", "in progress"]:
        return "In Turn"
    
    # Everything else → Not Ready
    return "Not Ready"


# =======================================================
# 🧩  AGGREGATION WRAPPER
# =======================================================
def compute_all_unit_fields(df_units: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all per-unit computations and return
    enriched DataFrame ready for metrics.
    """
    if df_units.empty:
        log_event("WARNING", "Units DataFrame is empty in compute_all_unit_fields.")
        return df_units

    df = df_units.copy()

    # Ensure datetimes
    for col in ["move_out", "move_in"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Derived columns
    df["days_vacant"] = df.apply(compute_days_vacant, axis=1)  # type: ignore
    df["days_to_be_ready"] = df.apply(compute_days_to_be_ready, axis=1)  # type: ignore
    df["turn_level"] = df.apply(compute_turn_level, axis=1)  # type: ignore
    df["unit_blocked"] = df.apply(compute_unit_blocked, axis=1)  # type: ignore
    df["lifecycle_label"] = df.apply(compute_lifecycle_label, axis=1)  # type: ignore

    log_event("INFO", f"Computed derived fields for {len(df)} units.")
    return df


# =======================================================
# 🧩  SELF-TEST (optional)
# =======================================================
if __name__ == "__main__":
    sample = pd.DataFrame({
        "unit_id": [1, 2, 3],
        "nvm": ["vacant", "notice", "vacant"],
        "status": ["in turn", "ready", "ready"],
        "move_out": [datetime.now() - timedelta(days=5),
                     datetime.now() - timedelta(days=20),
                     datetime.now() - timedelta(days=30)],
        "move_in": [datetime.now() + timedelta(days=5),
                    datetime.now() + timedelta(days=10),
                    datetime.now() + timedelta(days=2)],
        "comments": ["ok", "blocked pipe", ""],
    })
    enriched = compute_all_unit_fields(sample)
    print(enriched[["unit_id", "days_vacant", "turn_level", "unit_blocked"]])
