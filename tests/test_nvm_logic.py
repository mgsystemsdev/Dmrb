"""
Test NVM Status Calculation Logic
Validates the compute_nvm_status function against all scenarios.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
from datetime import datetime, timedelta
from core.data_logic import compute_nvm_status
from utils.constants import (
    NVM_STATUS_MOVE_IN,
    NVM_STATUS_SMI,
    NVM_STATUS_VACANT,
    NVM_STATUS_NOTICE_SMI,
    NVM_STATUS_NOTICE,
    NVM_STATUS_BLANK
)


def test_nvm_move_in():
    """Test: Tenant has already moved in (MI <= TODAY)"""
    row = pd.Series({
        'move_out': datetime.now() - timedelta(days=10),
        'move_in': datetime.now() - timedelta(days=2)  # Moved in 2 days ago
    })
    result = compute_nvm_status(row)
    assert result == NVM_STATUS_MOVE_IN, f"Expected MOVE IN, got {result}"
    print("✅ MOVE IN test passed")


def test_nvm_smi():
    """Test: Unit vacant, move-in scheduled (MO <= TODAY, MI > TODAY)"""
    row = pd.Series({
        'move_out': datetime.now() - timedelta(days=5),  # Moved out 5 days ago
        'move_in': datetime.now() + timedelta(days=3)     # Move-in in 3 days
    })
    result = compute_nvm_status(row)
    assert result == NVM_STATUS_SMI, f"Expected SMI, got {result}"
    print("✅ SMI test passed")


def test_nvm_vacant():
    """Test: Unit vacant, no move-in scheduled (MO <= TODAY, MI blank)"""
    row = pd.Series({
        'move_out': datetime.now() - timedelta(days=7),  # Moved out 7 days ago
        'move_in': None  # No move-in scheduled
    })
    result = compute_nvm_status(row)
    assert result == NVM_STATUS_VACANT, f"Expected VACANT, got {result}"
    print("✅ VACANT test passed")


def test_nvm_notice_smi():
    """Test: Still occupied, next tenant scheduled (MO > TODAY, MI > TODAY)"""
    row = pd.Series({
        'move_out': datetime.now() + timedelta(days=5),  # Moving out in 5 days
        'move_in': datetime.now() + timedelta(days=10)   # Next tenant in 10 days
    })
    result = compute_nvm_status(row)
    assert result == NVM_STATUS_NOTICE_SMI, f"Expected NOTICE + SMI, got {result}"
    print("✅ NOTICE + SMI test passed")


def test_nvm_notice():
    """Test: Still occupied, tenant gave notice (MO > TODAY, MI blank)"""
    row = pd.Series({
        'move_out': datetime.now() + timedelta(days=15),  # Moving out in 15 days
        'move_in': None  # No next tenant scheduled
    })
    result = compute_nvm_status(row)
    assert result == NVM_STATUS_NOTICE, f"Expected NOTICE, got {result}"
    print("✅ NOTICE test passed")


def test_nvm_blank():
    """Test: No valid dates - blank status"""
    row = pd.Series({
        'move_out': None,
        'move_in': None
    })
    result = compute_nvm_status(row)
    assert result == NVM_STATUS_BLANK, f"Expected blank, got {result}"
    print("✅ BLANK test passed")


def test_priority_order():
    """Test: Priority order - MOVE IN should win when MI is in the past"""
    # Use .date() to get midnight timestamps
    today = datetime.now().date()
    row = pd.Series({
        'move_out': pd.Timestamp(today) - timedelta(days=10),
        'move_in': pd.Timestamp(today) - timedelta(days=1)  # Moved in yesterday
    })
    result = compute_nvm_status(row)
    assert result == NVM_STATUS_MOVE_IN, f"Priority test failed: Expected MOVE IN, got {result}"
    print("✅ Priority order test passed")


def run_all_tests():
    """Run all NVM status tests"""
    print("\n🧪 Running NVM Status Calculation Tests\n")
    print("=" * 60)
    
    test_nvm_move_in()
    test_nvm_smi()
    test_nvm_vacant()
    test_nvm_notice_smi()
    test_nvm_notice()
    test_nvm_blank()
    test_priority_order()
    
    print("=" * 60)
    print("\n✅ All NVM tests passed!\n")


if __name__ == "__main__":
    run_all_tests()
