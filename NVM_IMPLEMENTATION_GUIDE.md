# 🏷️ NVM Status Implementation Guide

**Status:** ✅ PARTIALLY IMPLEMENTED  
**Date:** 2025-10-26

---

## ✅ **What's Been Done**

### 1. **Added NVM Calculation Logic**
- ✅ Created `compute_nvm_status()` in [src/core/data_logic.py](file:///Users/miguelgonzalez/Documents/ActiveProjects/DMRB/src/core/data_logic.py#L113-L161)
- ✅ Integrated into `compute_all_unit_fields()` 
- ✅ NVM is now a **computed field** (not read from Excel)

### 2. **Centralized NVM Constants**
- ✅ Added to [src/utils/constants.py](file:///Users/miguelgonzalez/Documents/ActiveProjects/DMRB/src/utils/constants.py#L26-L48):
  - `NVM_STATUS_*` constants
  - `NVM_EMOJI_MAP` (centralized emoji mapping)
  - `VACANT_STATUSES` list

### 3. **Updated UI Components**
- ✅ [src/ui/expanders.py](file:///Users/miguelgonzalez/Documents/ActiveProjects/DMRB/src/ui/expanders.py#L10) - Uses `NVM_EMOJI_MAP`
- ✅ [src/ui/unit_cards.py](file:///Users/miguelgonzalez/Documents/ActiveProjects/DMRB/src/ui/unit_cards.py#L10) - Uses `NVM_EMOJI_MAP`

---

## 🔧 **NVM Business Logic (IMPLEMENTED)**

```python
def compute_nvm_status(row: pd.Series) -> str:
    """
    Priority order (evaluated top to bottom):
    1. MOVE IN - MI valid AND MI <= TODAY()
    2. SMI - MO valid AND MO <= TODAY() AND MI valid AND MI > TODAY()
    3. VACANT - MO valid AND MO <= TODAY() AND (MI blank OR invalid)
    4. NOTICE + SMI - MO valid AND MO > TODAY() AND MI valid AND MI > TODAY()
    5. NOTICE - MO valid AND MO > TODAY() AND (MI blank OR invalid)
    6. blank - anything else
    """
```

### **Status Definitions**

| Status | Trigger Logic | Meaning | Vacant? |
|--------|--------------|---------|---------|
| **MOVE IN** | `MI valid AND MI <= TODAY()` | Tenant has moved in | ❌ No |
| **SMI** | `MO valid AND MO <= TODAY() AND MI valid AND MI > TODAY()` | Unit vacant, move-in scheduled | ✅ Yes |
| **VACANT** | `MO valid AND MO <= TODAY() AND (MI blank OR invalid)` | Unit vacant, no move-in | ✅ Yes |
| **NOTICE + SMI** | `MO valid AND MO > TODAY() AND MI valid AND MI > TODAY()` | Occupied, next tenant scheduled | ❌ No |
| **NOTICE** | `MO valid AND MO > TODAY() AND (MI blank OR invalid)` | Occupied, tenant gave notice | ❌ No |
| **blank** | anything else | No valid status | ❌ No |

---

## 🚧 **Remaining Work**

### 1. **Update Dashboard Page**

**File:** `pages/1_📊_Dashboard.py`

**Current (Line 47-65):**
```python
column_mapping = {
    'Move-out': 'move_out',
    'Move-in': 'move_in',
    'Nvm': 'nvm',  # ❌ REMOVE THIS - NVM is now computed
    'Unit': 'unit_id',
    'Phases': 'phase',
    'Building': 'building'
}
```

**Should Be:**
```python
column_mapping = {
    'Move-out': 'move_out',
    'Move-in': 'move_in',
    # 'Nvm' removed - now computed by compute_all_unit_fields()
    'Unit': 'unit_id',
    'Phases': 'phase',
    'Building': 'building'
}
```

**Also Remove (Line 61):**
```python
'nvm': 'Nvm',  # ❌ Remove from reverse mapping
```

**Update Required Columns (Line 71):**
```python
# Old
required_cols = ["Nvm", "Unit", "Phases", "Building", "Move-out", "Move-in"]

# New
required_cols = ["Unit", "Phases", "Building", "Move-out", "Move-in"]
```

**Update Vacancy Calculation (Line 77-78):**
```python
# Old
nvm_normalized = units_df["Nvm"].fillna("").astype(str).str.strip().str.lower()
vacant_units = nvm_normalized.isin(["vacant", "smi"]).sum()

# New (use lowercase 'nvm' - it's a computed column)
from utils.constants import VACANT_STATUSES
nvm_normalized = units_df["nvm"].fillna("").astype(str).str.strip().str.lower()
vacant_units = nvm_normalized.isin([s.lower() for s in VACANT_STATUSES]).sum()
```

---

### 2. **Update Units Page**

**File:** `pages/2_🏢_Units.py`

**Same Changes as Dashboard:**

**Line 81-90 - Remove `'Nvm': 'nvm'` from column_mapping:**
```python
column_mapping = {
    'Move-out': 'move_out',
    'Move-in': 'move_in',
    # 'Nvm': 'nvm',  # ❌ REMOVE - now computed
    'Unit': 'unit_number',
    'Unit id': 'unit_id',
    'Phases': 'phase',
    'Building': 'building'
}
```

**Line 113 - Update vacancy calculation:**
```python
from utils.constants import VACANT_STATUSES
nvm_norm = units_df['nvm'].fillna('').astype(str).str.lower()
vacant_units = nvm_norm.isin([s.lower() for s in VACANT_STATUSES]).sum()
```

**Line 222, 228, 234 - Update NVM filtering:**
```python
# Notice tab
nvm_norm = units_df['nvm'].fillna('').astype(str).str.lower()
notice = units_df[nvm_norm == 'notice'].copy()

# Vacant tab
vacant = units_df[nvm_norm.isin(['vacant', 'smi'])].copy()
```

---

### 3. **Update phase_logic.py**

**File:** `src/core/phase_logic.py`

**Line 24 - Update docstring:**
```python
# Old
Expects columns: 'Phases','Building','Unit','Nvm','Move-out','Move-in','lifecycle_label'.

# New
Expects columns: 'Phases','Building','Unit','Move-out','Move-in','lifecycle_label'.
Note: 'nvm' is a computed column (lowercase).
```

**Line 39-40 - Use lowercase 'nvm':**
```python
# Old
nvm_norm = normalize_nvm_series(building_units['Nvm']) if 'Nvm' in building_units.columns else pd.Series(dtype=str)

# New
nvm_norm = normalize_nvm_series(building_units['nvm']) if 'nvm' in building_units.columns else pd.Series(dtype=str)
```

**Line 65, 139 - Use lowercase 'nvm':**
```python
# Change all instances of row.get('Nvm', '—') to:
row.get('nvm', '—')
```

---

### 4. **Update README.md**

**Section: Vacancy Logic (Line 97-102):**

```markdown
### Vacancy Logic

NVM status is **computed automatically** based on Move-Out and Move-In dates:

- **VACANT** = `Move-Out <= Today AND (Move-In blank OR invalid)`
- **SMI** = `Move-Out <= Today AND Move-In > Today`
- **NOTICE** = `Move-Out > Today AND Move-In blank`
- **NOTICE + SMI** = `Move-Out > Today AND Move-In > Today`
- **MOVE IN** = `Move-In <= Today`

For occupancy calculations:
- **Vacant Units** = Units with status `VACANT` or `SMI`
- **Occupied Units** = All other statuses
```

**Update Data Schema (Line 86-96):**

Remove `Nvm` from required columns table, add note that it's computed.

---

## 🎯 **Testing Checklist**

After making changes:

- [ ] Dashboard page loads without errors
- [ ] Units page loads without errors
- [ ] NVM status displays correctly in unit cards
- [ ] Vacancy counts are accurate
- [ ] All 6 NVM statuses can be displayed
- [ ] Emoji mapping is consistent across UI
- [ ] Phase overview shows correct NVM values
- [ ] Move activity sections work correctly

---

## 📊 **Emoji Reference**

Current centralized mapping in `utils/constants.py`:

```python
NVM_EMOJI_MAP = {
    'move in': '🟢',
    'smi': '🔴',
    'vacant': '🟢',
    'notice + smi': '📢🔴',
    'notice': '📢',
    'moving': '📦',  # Legacy - may not be generated
    '': '⚪'
}
```

---

## 🔄 **Migration Path**

### **Option A: Remove Nvm from Excel (Recommended)**
- NVM is fully computed
- Excel only needs Move-Out and Move-In dates
- Cleaner data model

### **Option B: Keep Nvm in Excel for Reference**
- Excel contains manual NVM values
- System computes and overwrites them
- Useful for data validation/comparison

**Current Implementation:** Option A (compute only)

---

## ✅ **Summary**

**Completed:**
- ✅ NVM calculation logic implemented
- ✅ Constants centralized
- ✅ UI components updated

**Remaining:**
- 🔧 Update Dashboard page column mappings
- 🔧 Update Units page column mappings
- 🔧 Update phase_logic.py references
- 🔧 Update README documentation
- ✅ Test all NVM status values display correctly

**Estimated Time:** 15-20 minutes

---

**End of Implementation Guide**
