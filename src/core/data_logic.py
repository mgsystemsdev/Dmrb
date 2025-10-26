"""
core/data_logic.py
---------------------------------------------------------
Phase 1: Unit-level computations for DMRB.
Adds derived fields to the Units DataFrame and
normalizes readiness / vacancy logic.
---------------------------------------------------------
"""

import pandas as pd
from datetime import datetime, timedelta
from core.logger import log_event
from utils.constants import (
    NVM_STATUS_MOVE_IN,
    NVM_STATUS_SMI,
    NVM_STATUS_VACANT,
    NVM_STATUS_NOTICE_SMI,
    NVM_STATUS_NOTICE,
    NVM_STATUS_BLANK
)


# =======================================================
# 🧩  BASIC TIME UTILITIES
# =======================================================
def _today() -> pd.Timestamp:
    """Standard reference date for all calculations."""
    return pd.Timestamp("today").normalize()


def _norm_today(today: object | None) -> pd.Timestamp:
    """Normalize an external 'today' to midnight if provided, else system today."""
    if today is None:
        return _today()
    try:
        return pd.to_datetime(today).normalize()
    except Exception:
        return _today()


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
def compute_days_vacant(row: pd.Series, today: object | None = None) -> int | None:
    """Days since move-out (vacancy age)."""
    move_out = row.get("move_out")
    return _safe_days_between(_norm_today(today), move_out)


def compute_days_to_be_ready(row: pd.Series, today: object | None = None) -> int | None:
    """Days remaining until scheduled move-in."""
    move_in = row.get("move_in")
    return _safe_days_between(move_in, _norm_today(today))


def compute_turn_level(row: pd.Series) -> str:
    """
    Classify unit’s time status.
    Distinguishes between Ready (vacant aging)
    and Not Ready (turn progress).
    Used by: pages (Units), any UI that buckets readiness.
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
    if status in ["in turn", "currently work", "started", "in progress"]:
        return "In Turn"
    
    # Everything else → Not Ready
    return "Not Ready"


def compute_nvm_status(row: pd.Series, today: object | None = None) -> str:
    """
    Compute NVM status based on Move-Out/Move-In dates and TODAY().
    
    Priority order (evaluated top to bottom):
    1. MOVE IN - Tenant has already moved in
    2. SMI - Unit vacant, move-in scheduled
    3. VACANT - Unit vacant, no move-in scheduled
    4. NOTICE + SMI - Still occupied, next tenant scheduled
    5. NOTICE - Still occupied, tenant gave notice
    6. blank - No status (invalid/missing dates)
    
    Args:
        row: DataFrame row with move_out and move_in columns
        
    Returns:
        NVM status string
    """
    today = _norm_today(today)
    
    move_out = pd.to_datetime(row.get('move_out'), errors='coerce')
    move_in = pd.to_datetime(row.get('move_in'), errors='coerce')
    
    mo_valid = pd.notna(move_out)
    mi_valid = pd.notna(move_in)
    
    # Priority 1: MOVE IN (tenant has moved in)
    if mi_valid and move_in <= today:
        return NVM_STATUS_MOVE_IN
    
    # Priority 2: SMI (unit vacant, move-in scheduled)
    if mo_valid and move_out <= today and mi_valid and move_in > today:
        return NVM_STATUS_SMI
    
    # Priority 3: VACANT (unit vacant, no move-in scheduled)
    if mo_valid and move_out <= today and not mi_valid:
        return NVM_STATUS_VACANT
    
    # Priority 4: NOTICE + SMI (still occupied, next tenant scheduled)
    if mo_valid and move_out > today and mi_valid and move_in > today:
        return NVM_STATUS_NOTICE_SMI
    
    # Priority 5: NOTICE (still occupied, tenant gave notice)
    if mo_valid and move_out > today and not mi_valid:
        return NVM_STATUS_NOTICE
    
    # Default: blank (no valid status)
    return NVM_STATUS_BLANK


# =======================================================
# 🧩  AGGREGATION WRAPPER
# =======================================================
def compute_all_unit_fields(df_units: pd.DataFrame, today: object | None = None) -> pd.DataFrame:
    """
    Apply all per-unit computations and return
    enriched DataFrame ready for metrics.
    Inputs: DataFrame with at least move_in/move_out/status columns (if present).
    Outputs: Adds days_vacant, days_to_be_ready, turn_level, unit_blocked, lifecycle_label, nvm.
    Used by: Pages (Dashboard, Units) and any aggregator in core.phase_logic.
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
    t = _norm_today(today)

    # Use Excel columns if available (DV, DTBR), otherwise calculate
    if "days_vacant" not in df.columns or df["days_vacant"].isna().all():
        df["days_vacant"] = df.apply(lambda r: compute_days_vacant(r, today=t), axis=1)  # type: ignore
    
    if "days_to_be_ready" not in df.columns or df["days_to_be_ready"].isna().all():
        df["days_to_be_ready"] = df.apply(lambda r: compute_days_to_be_ready(r, today=t), axis=1)  # type: ignore
    else:
        # Excel DTBR is inverted (negative values), flip the sign
        df["days_to_be_ready"] = df["days_to_be_ready"] * -1
    
    # Always compute these fields
    df["turn_level"] = df.apply(compute_turn_level, axis=1)  # type: ignore
    df["unit_blocked"] = df.apply(compute_unit_blocked, axis=1)  # type: ignore
    df["lifecycle_label"] = df.apply(compute_lifecycle_label, axis=1)  # type: ignore
    df["nvm"] = df.apply(lambda r: compute_nvm_status(r, today=t), axis=1)  # type: ignore - COMPUTED NVM STATUS

    log_event("INFO", f"Computed derived fields for {len(df)} units (days_vacant/days_to_be_ready from Excel if available).")
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
