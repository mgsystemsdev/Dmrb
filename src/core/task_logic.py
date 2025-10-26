"""
task_logic.py
---------------------------------------------------------
Task processing logic for DMRB Dashboard.
Handles task filtering, parsing Unit IDs, and grouping.
Used by: Dashboard page (Walk of the Day) and task UI components.
---------------------------------------------------------
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


def parse_unit_id(unit_id: str) -> Tuple[str, str, str]:
    """
    Parse Unit ID string into Phase, Building, Unit.

    Inputs: unit_id like "P-5 / Bld-1 / U-210".
    Outputs: (phase, building, unit) as strings.
    Used by: get_tasks_for_date() to enrich task rows for UI grouping.
    """
    try:
        parts = unit_id.split('/')
        phase = parts[0].replace('P-', '').strip()
        building = parts[1].replace('Bld-', '').strip()
        unit = parts[2].replace('U-', '').strip()
        return phase, building, unit
    except:
        return '', '', ''


def get_tasks_for_date(tasks_df: pd.DataFrame, target_date: datetime.date) -> Dict[str, pd.DataFrame]:
    """
    Get all tasks with dates matching target_date, grouped by task type.

    Inputs: tasks_df (raw Task sheet), target_date (python date).
    Outputs: Dict[str, DataFrame] keyed by task type, with Phase/Building/Unit columns added.
    Used by: get_yesterday_tasks, Dashboard page.
    """
    # Define task types and their date columns
    task_types = {
        'Inspections': 'Inspection Date',
        'Bids': 'Bids Date',
        'Paint': 'Paint Date',
        'Make Ready': 'MR date',
        'Housekeeping': 'HK Date',
        'Flooring/Carpet': 'F/C Date',
        'Other Task': 'Other Task Date',
        'Other Task 2': 'O/T Date',
        'Final Walk': 'Final walk Date'
    }
    
    results = {}
    
    for task_name, date_col in task_types.items():
        if date_col not in tasks_df.columns:
            continue
        
        # Filter tasks where date matches target_date
        task_dates = pd.to_datetime(tasks_df[date_col], errors='coerce')
        matching_tasks = tasks_df[task_dates.dt.date == target_date].copy()
        
        if len(matching_tasks) > 0:
            # Parse Unit ID into components
            matching_tasks[['Phase', 'Building', 'Unit']] = matching_tasks['Unit ID'].apply(
                lambda x: pd.Series(parse_unit_id(x))
            )
            results[task_name] = matching_tasks
    
    return results


def get_yesterday_tasks(tasks_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Get all tasks due yesterday.

    Inputs: tasks_df (raw Task sheet).
    Outputs: Dict[str, DataFrame] for tasks matching yesterday's date per type.
    Used by: Dashboard Walk of the Day.
    """
    yesterday = datetime.now().date() - timedelta(days=1)
    return get_tasks_for_date(tasks_df, yesterday)


def group_tasks_by_hierarchy(tasks: pd.DataFrame) -> Dict[str, Dict[str, List[Dict]]]:
    """
    Group tasks by Phase → Building → Unit hierarchy.

    Inputs: DataFrame with Phase, Building, Unit columns present.
    Outputs: Nested dict {phase: {building: [units]}} for UI rendering.
    Used by: ui.task_cards.render_all_tasks.
    """
    hierarchy = {}
    
    for _, row in tasks.iterrows():
        phase = str(row.get('Phase', ''))
        building = str(row.get('Building', ''))
        unit = str(row.get('Unit', ''))
        
        if not phase or not building or not unit:
            continue
        
        if phase not in hierarchy:
            hierarchy[phase] = {}
        
        if building not in hierarchy[phase]:
            hierarchy[phase][building] = []
        
        hierarchy[phase][building].append({
            'unit': unit,
            'unit_id': row.get('Unit ID', ''),
            'vendor': row.get('Vendor / Employee', '—'),
            'status': row.get('Task Status', '—')
        })
    
    return hierarchy
