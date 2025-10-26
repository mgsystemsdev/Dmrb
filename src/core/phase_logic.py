"""
core/phase_logic.py
---------------------------------------------------------
Phase-level and list aggregations for Units data.
Builds structures consumed by UI components while relying
on canonical calculators from core.data_logic and helpers.
---------------------------------------------------------
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Any, Dict, List
import pandas as pd

from utils.helpers import normalize_nvm_series, is_vacant, fmt_date, days_between


def build_phase_overview(units_df: pd.DataFrame, today: date | None = None) -> List[Dict[str, Any]]:
    """
    Construct Phase → Building overview with vacancy counts, move events,
    and compact unit summaries for vacant units.

    Expects columns: 'Phases','Building','Unit','Move-out','Move-in','lifecycle_label'.
    Note: 'nvm' is a computed column (lowercase) added by compute_all_unit_fields().
    Returns list of dicts: [{ 'phase_label', 'buildings': [...] }].
    """
    if today is None:
        today = datetime.now().date()

    phase_data: List[Dict[str, Any]] = []

    for phase in sorted(units_df['Phases'].dropna().unique(), key=str):
        phase_units = units_df[units_df['Phases'] == phase].copy()

        buildings: List[Dict[str, Any]] = []
        for building in sorted(phase_units['Building'].dropna().unique(), key=str):
            building_units = phase_units[phase_units['Building'] == building].copy()

            nvm_norm = normalize_nvm_series(building_units['nvm']) if 'nvm' in building_units.columns else pd.Series(dtype=str)
            
            # Calculate NVM classification counts
            notice_count = int(nvm_norm.str.contains('notice', na=False).sum())
            vacant_count = int(nvm_norm.isin(['vacant', 'smi']).sum())
            move_in_count = int((nvm_norm == 'move in').sum())
            
            total = len(building_units)
            
            # Keep old counts for backward compatibility (deprecated)
            vacant = vacant_count
            occupied = total - vacant_count
            vacant_mask = nvm_norm.isin(['vacant', 'smi'])

            vacant_units_list: List[Dict[str, Any]] = []
            for _, row in building_units[vacant_mask].iterrows():
                move_out_str = fmt_date(row.get('Move-out'))
                move_in_str = fmt_date(row.get('Move-in'))

                # Derive simple integers for days; keep '—' if unknown
                dv = days_between(datetime.now(), row.get('Move-out'))
                dr = days_between(row.get('Move-in'), datetime.now())
                days_vacant = dv if dv is not None else '—'
                days_to_be_ready = dr if dr is not None else '—'

                vacant_units_list.append({
                    'unit_num': str(row.get('Unit', '')).strip(),
                    'status_emoji': '🔴',
                    'move_out_str': move_out_str,
                    'days_vacant': days_vacant,
                    'move_in_str': move_in_str,
                    'days_to_be_ready': days_to_be_ready,
                    'lifecycle_label': row.get('lifecycle_label', 'Not Ready'),
                    'nvm': row.get('nvm', '—'),
                })

            move_events: List[str] = []

            # Move-outs today
            if 'Move-out' in building_units.columns:
                move_out_dates = pd.to_datetime(building_units['Move-out'], errors='coerce')
                same_day = building_units[move_out_dates.dt.date == today]
                for _, r in same_day.iterrows():
                    unit_label = str(r.get('Unit', '')).strip()
                    move_date = fmt_date(r.get('Move-out'), '%Y-%m-%d')
                    if unit_label and move_date != '—':
                        move_events.append(f"🟥 Unit {unit_label} - Move Out {move_date}")

            # Move-ins today
            if 'Move-in' in building_units.columns:
                move_in_dates = pd.to_datetime(building_units['Move-in'], errors='coerce')
                same_day = building_units[move_in_dates.dt.date == today]
                for _, r in same_day.iterrows():
                    unit_label = str(r.get('Unit', '')).strip()
                    move_date = fmt_date(r.get('Move-in'), '%Y-%m-%d')
                    if unit_label and move_date != '—':
                        move_events.append(f"🟩 Unit {unit_label} - Move In {move_date}")

            buildings.append({
                'label': f'B{building}',
                'total_units': total,
                'notice_count': notice_count,
                'vacant_count': vacant_count,
                'move_in_count': move_in_count,
                'vacant': vacant,  # Deprecated
                'occupied': occupied,  # Deprecated
                'move_events': move_events,
                'vacant_units': vacant_units_list,
            })

        # Safe phase label generation
        try:
            phase_label = f'Phase {int(phase)}'
        except (ValueError, TypeError):
            phase_label = f'Phase {phase}'

        phase_data.append({'phase_label': phase_label, 'buildings': buildings})

    return phase_data


def build_all_units(units_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Build a flat list of units suitable for compact list views.
    Uses existing columns; attempts to avoid recomputation drift.
    """
    all_units: List[Dict[str, Any]] = []
    now = datetime.now()

    for _, row in units_df.iterrows():
        unit_num = str(row.get('Unit', '')).strip()
        if not unit_num:
            continue

        move_out_str = fmt_date(row.get('Move-out'))
        move_in_str = fmt_date(row.get('Move-in'))
        dv = days_between(now, row.get('Move-out'))
        dr = days_between(row.get('Move-in'), now)

        nvm_val = row.get('nvm', '')
        status_emoji = '🔴' if is_vacant(nvm_val) else '🟢'

        all_units.append({
            'unit_num': unit_num,
            'status_emoji': status_emoji,
            'move_out_str': move_out_str,
            'days_vacant': dv if dv is not None else '—',
            'days_vacant_sort': dv if dv is not None else -1,
            'move_in_str': move_in_str,
            'days_to_be_ready': dr if dr is not None else '—',
            'nvm': row.get('nvm', '—'),
        })

    # Sort by days vacant (descending - oldest first)
    all_units.sort(key=lambda x: x['days_vacant_sort'], reverse=True)
    return all_units
