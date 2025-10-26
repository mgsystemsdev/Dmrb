#!/usr/bin/env python3
"""
NVM Implementation Verification Script
Validates the complete NVM implementation across all modules.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("\n" + "="*70)
print("🔍 NVM IMPLEMENTATION VERIFICATION")
print("="*70 + "\n")

# Test 1: Import all modules
print("1️⃣  Testing module imports...")
try:
    from core.data_logic import compute_nvm_status, compute_all_unit_fields
    from utils.constants import (
        NVM_STATUS_MOVE_IN,
        NVM_STATUS_SMI,
        NVM_STATUS_VACANT,
        NVM_STATUS_NOTICE_SMI,
        NVM_STATUS_NOTICE,
        NVM_STATUS_BLANK,
        NVM_EMOJI_MAP,
        VACANT_STATUSES
    )
    from ui.expanders import render_unit_row
    from ui.unit_cards import render_enhanced_unit_row
    from core.phase_logic import build_phase_overview, build_all_units
    print("   ✅ All imports successful\n")
except Exception as e:
    print(f"   ❌ Import failed: {e}\n")
    sys.exit(1)

# Test 2: Verify constants
print("2️⃣  Verifying NVM constants...")
try:
    assert NVM_STATUS_MOVE_IN == "MOVE IN"
    assert NVM_STATUS_SMI == "SMI"
    assert NVM_STATUS_VACANT == "VACANT"
    assert NVM_STATUS_NOTICE_SMI == "NOTICE + SMI"
    assert NVM_STATUS_NOTICE == "NOTICE"
    assert NVM_STATUS_BLANK == ""
    assert VACANT_STATUSES == ['vacant', 'smi']
    assert len(NVM_EMOJI_MAP) == 7
    print("   ✅ All constants verified\n")
except AssertionError as e:
    print(f"   ❌ Constant verification failed: {e}\n")
    sys.exit(1)

# Test 3: Test NVM calculation
print("3️⃣  Testing NVM calculation logic...")
try:
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Create test DataFrame
    test_data = pd.DataFrame({
        'move_out': [
            datetime.now() - timedelta(days=10),  # Past
            datetime.now() - timedelta(days=5),   # Past
            datetime.now() - timedelta(days=7),   # Past
            datetime.now() + timedelta(days=5),   # Future
            datetime.now() + timedelta(days=15),  # Future
            None
        ],
        'move_in': [
            datetime.now() - timedelta(days=2),   # Past (MOVE IN)
            datetime.now() + timedelta(days=3),   # Future (SMI)
            None,                                  # None (VACANT)
            datetime.now() + timedelta(days=10),  # Future (NOTICE + SMI)
            None,                                  # None (NOTICE)
            None                                   # None (BLANK)
        ]
    })
    
    result_df = compute_all_unit_fields(test_data)
    
    expected_statuses = [
        NVM_STATUS_MOVE_IN,
        NVM_STATUS_SMI,
        NVM_STATUS_VACANT,
        NVM_STATUS_NOTICE_SMI,
        NVM_STATUS_NOTICE,
        NVM_STATUS_BLANK
    ]
    
    for idx, expected in enumerate(expected_statuses):
        actual = result_df.iloc[idx]['nvm']
        assert actual == expected, f"Row {idx}: Expected {expected}, got {actual}"
    
    print("   ✅ All NVM calculations correct\n")
except Exception as e:
    print(f"   ❌ NVM calculation test failed: {e}\n")
    sys.exit(1)

# Test 4: Verify 'nvm' column is created
print("4️⃣  Verifying 'nvm' column creation...")
try:
    assert 'nvm' in result_df.columns
    assert 'days_vacant' in result_df.columns
    assert 'days_to_be_ready' in result_df.columns
    assert 'lifecycle_label' in result_df.columns
    print("   ✅ All computed columns present\n")
except AssertionError as e:
    print(f"   ❌ Column verification failed: {e}\n")
    sys.exit(1)

# Test 5: Verify emoji mapping
print("5️⃣  Verifying emoji mapping...")
try:
    assert NVM_EMOJI_MAP['move in'] == '🟢'
    assert NVM_EMOJI_MAP['smi'] == '🔴'
    assert NVM_EMOJI_MAP['vacant'] == '🟢'
    assert NVM_EMOJI_MAP['notice + smi'] == '📢🔴'
    assert NVM_EMOJI_MAP['notice'] == '📢'
    assert NVM_EMOJI_MAP[''] == '⚪'
    print("   ✅ All emoji mappings correct\n")
except AssertionError as e:
    print(f"   ❌ Emoji mapping verification failed: {e}\n")
    sys.exit(1)

# Test 6: Verify vacancy logic
print("6️⃣  Testing vacancy calculation...")
try:
    vacant_count = result_df[
        result_df['nvm'].str.lower().isin([s.lower() for s in VACANT_STATUSES])
    ].shape[0]
    
    # Should be 2 (SMI and VACANT)
    assert vacant_count == 2, f"Expected 2 vacant units, got {vacant_count}"
    print("   ✅ Vacancy calculation correct\n")
except Exception as e:
    print(f"   ❌ Vacancy calculation failed: {e}\n")
    sys.exit(1)

# Test 7: Syntax check all pages
print("7️⃣  Checking page file syntax...")
try:
    import py_compile
    
    pages = [
        'pages/0_🏠_Home.py',
        'pages/1_📊_Dashboard.py',
        'pages/2_🏢_Units.py'
    ]
    
    for page in pages:
        py_compile.compile(page, doraise=True)
    
    print("   ✅ All page files have valid syntax\n")
except Exception as e:
    print(f"   ❌ Syntax check failed: {e}\n")
    sys.exit(1)

# Final summary
print("="*70)
print("✅ NVM IMPLEMENTATION VERIFICATION COMPLETE")
print("="*70)
print("\n📊 Summary:")
print("   • All modules import successfully")
print("   • All constants are correctly defined")
print("   • NVM calculation logic works correctly")
print("   • All 6 NVM status values are generated correctly")
print("   • Emoji mapping is consistent")
print("   • Vacancy calculation is accurate")
print("   • All page files have valid syntax")
print("\n🎉 System is PRODUCTION READY!\n")
