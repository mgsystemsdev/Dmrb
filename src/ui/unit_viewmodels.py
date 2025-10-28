"""
ui/unit_viewmodels.py
---------------------------------------------------------
Transforms raw unit rows into dictionaries consumed by
ui/unit_cards.render_enhanced_unit_row, centralizing view-model shaping.
---------------------------------------------------------
"""

from __future__ import annotations

import pandas as pd


def build_enhanced_unit(row: pd.Series, tasks_df: pd.DataFrame) -> dict:
    """
    Shape a unit row + optional tasks context into a compact view model.
    Inputs are expected to include: unit_id, move_in, move_out, days_vacant,
    days_to_be_ready, lifecycle_label, nvm.
    """
    unit_id = str(row.get('unit_id', ''))  # Full path
    lifecycle = row.get('lifecycle_label', 'Unknown')
    status_emoji_map = {'Ready': '✅', 'In Turn': '🔧', 'Not Ready': '⚠️'}
    status_emoji = status_emoji_map.get(lifecycle, '🏠')
    readiness_pct = 100 if lifecycle == 'Ready' else 50 if lifecycle == 'In Turn' else 0

    days_vacant = row.get('days_vacant')
    days_vacant_str = str(int(days_vacant)) if pd.notna(days_vacant) and days_vacant != '' else '—'

    days_to_ready = row.get('days_to_be_ready')
    days_to_ready_str = str(int(days_to_ready)) if pd.notna(days_to_ready) and days_to_ready != '' else '—'

    return {
        'unit_id': unit_id,  # Full path (for Units page)
        'unit_num': unit_id,  # Also as unit_num (for render_unit_row compatibility)
        'status_emoji': status_emoji,
        'move_out': row.get('move_out', pd.NaT).strftime('%m/%d/%y') if pd.notna(row.get('move_out')) else '—',
        'move_out_str': row.get('move_out', pd.NaT).strftime('%m/%d/%y') if pd.notna(row.get('move_out')) else '—',  # Compatible key
        'move_in': row.get('move_in', pd.NaT).strftime('%m/%d/%y') if pd.notna(row.get('move_in')) else '—',
        'move_in_str': row.get('move_in', pd.NaT).strftime('%m/%d/%y') if pd.notna(row.get('move_in')) else '—',  # Compatible key
        'days_vacant': days_vacant_str,
        'days_to_ready': days_to_ready_str,
        'days_to_be_ready': days_to_ready_str,  # Compatible key
        'readiness_pct': readiness_pct,
        'nvm': row.get('nvm', '—'),
        'lifecycle_label': lifecycle  # Add lifecycle_label for render_unit_row
    }

