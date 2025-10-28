"""Test lifecycle_label computation"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.data_loader import load_units_sheet
from core.data_logic import compute_all_unit_fields
import pandas as pd
from datetime import datetime

# Load data
units_df = load_units_sheet()
print(f"Loaded {len(units_df)} units")
print(f"Original columns: {list(units_df.columns)}")

# Dashboard mapping
column_mapping = {
    'Move-out': 'move_out',
    'Move-in': 'move_in',
    'Unit': 'unit_id',
    'Phases': 'phase',
    'Building': 'building',
    'Status': 'status',
    'DV': 'days_vacant',
    'DTBR': 'days_to_be_ready'
}
units_df = units_df.rename(columns=column_mapping)
print(f"\nAfter first rename: {list(units_df.columns)}")

# Check if Status column exists and has data
if 'status' in units_df.columns:
    print(f"\n'status' column exists!")
    print(f"Status values: {units_df['status'].value_counts()}")
    print(f"Status sample (first 10):")
    print(units_df[['unit_id', 'status']].head(10))
else:
    print("\n'status' column MISSING!")

# Compute fields
today_ref = datetime.now().date()
units_df = compute_all_unit_fields(units_df, today=today_ref)
print(f"\nAfter compute_all_unit_fields: {list(units_df.columns)}")

# Check lifecycle_label
if 'lifecycle_label' in units_df.columns:
    print(f"\n'lifecycle_label' column exists!")
    print(f"Lifecycle counts: {units_df['lifecycle_label'].value_counts()}")
    print(f"Sample with status and lifecycle (first 10):")
    print(units_df[['unit_id', 'status', 'lifecycle_label']].head(10))
else:
    print("\n'lifecycle_label' column MISSING!")

# Rename back (like Dashboard does)
units_df = units_df.rename(columns={
    'move_out': 'Move-out',
    'move_in': 'Move-in',
    'unit_id': 'Unit',
    'phase': 'Phases',
    'building': 'Building'
})
print(f"\nAfter final rename: {list(units_df.columns)}")

# Check final state
print(f"\nFinal check - lifecycle_label in columns: {'lifecycle_label' in units_df.columns}")
if 'lifecycle_label' in units_df.columns:
    print(f"Final lifecycle counts: {units_df['lifecycle_label'].value_counts()}")
