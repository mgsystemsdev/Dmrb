"""
core/data_loader.py
---------------------------------------------------------
Reads DMRB.xlsx workbook and structures DataFrames.
Now supports both local files and Google Sheets via datasource.py
---------------------------------------------------------
"""

import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import log_event
from core.datasource import get_excel_file
from utils.constants import REQUIRED_SHEETS


def load_units_sheet(file_path: str = None) -> pd.DataFrame:
    """
    Load the Unit sheet from Excel (local or Google Sheets).
    
    Args:
        file_path: Legacy parameter, ignored (kept for backward compatibility)

    Returns:
        DataFrame with normalized column names (stripped whitespace).

    Raises:
        ValueError: If Unit sheet is missing.
    """
    try:
        xls = get_excel_file()
        df = pd.read_excel(xls, sheet_name="Unit")
        df.columns = df.columns.str.strip()

        log_event("INFO", f"Loaded {len(df)} units from data source")
        return df

    except Exception as e:
        log_event("ERROR", f"Failed to load units sheet: {e}")
        raise


def load_task_sheet(file_path: str = None) -> pd.DataFrame:
    """
    Load the Task sheet from Excel (local or Google Sheets).
    
    Args:
        file_path: Legacy parameter, ignored (kept for backward compatibility)

    Returns:
        DataFrame with normalized column names.

    Raises:
        ValueError: If Task sheet is missing.
    """
    try:
        xls = get_excel_file()
        df = pd.read_excel(xls, sheet_name="Task")
        df.columns = df.columns.str.strip()

        log_event("INFO", f"Loaded {len(df)} tasks from data source")
        return df

    except Exception as e:
        log_event("ERROR", f"Failed to load task sheet: {e}")
        raise


def load_all_sheets(file_path: str = None) -> dict[str, pd.DataFrame]:
    """
    Load all required sheets from Excel (local or Google Sheets).
    
    Args:
        file_path: Legacy parameter, ignored (kept for backward compatibility)

    Returns:
        Dictionary with sheet names as keys and DataFrames as values.
    """
    try:
        sheets = {}
        sheets["Unit"] = load_units_sheet()
        sheets["Task"] = load_task_sheet()

        log_event("INFO", f"Successfully loaded all {len(sheets)} required sheets")
        return sheets

    except Exception as e:
        log_event("ERROR", f"Failed to load workbook: {e}")
        raise


def validate_required_columns(df: pd.DataFrame, required_cols: list[str], sheet_name: str) -> bool:
    """
    Validate that required columns exist in DataFrame.

    Args:
        df: DataFrame to validate
        required_cols: List of required column names
        sheet_name: Name of sheet (for error messages)

    Returns:
        True if all columns exist

    Raises:
        ValueError: If required columns are missing
    """
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        error_msg = f"{sheet_name} sheet missing required columns: {missing}"
        log_event("ERROR", error_msg)
        raise ValueError(error_msg)

    return True
