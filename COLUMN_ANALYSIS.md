# 📊 DMRB Column & NVM Status Analysis

**Generated:** 2025-10-26  
**Purpose:** Document all columns used in DMRB and NVM status values

---

## 📋 **Excel Columns Used**

### **Unit Sheet - Required Columns**

| Column Name | Internal Name | Type | Purpose | Used In |
|-------------|---------------|------|---------|---------|
| `Unit` | `unit_number` | String | Unit identifier (e.g., "210") | Dashboard, Units pages |
| `Unit id` | `unit_id` | String | Full path (e.g., "P-5 / Bld-1 / U-210") | Units page |
| `Phases` | `phase` | Integer | Phase number (1, 2, 3) | All pages |
| `Building` | `building` | Integer | Building number | All pages |
| **`Nvm`** | `nvm` | String | **Vacancy status** | **All pages** |
| `Move-out` | `move_out` | DateTime | Tenant move-out date | All pages |
| `Move-in` | `move_in` | DateTime | Scheduled move-in date | All pages |
| `Status` | `status` | String | Work status (optional) | Units page (lifecycle logic) |

### **Task Sheet - Date Columns**

| Task Type | Date Column | Purpose |
|-----------|-------------|---------|
| Inspections | `Inspection Date` | Track inspection completion |
| Bids | `Bids Date` | Track bid completion |
| Paint | `Paint Date` | Track painting completion |
| Make Ready | `MR date` | Track MR completion |
| Housekeeping | `HK Date` | Track HK completion |
| Flooring/Carpet | `F/C Date` | Track flooring completion |
| Other Task | `Other Task Date` | Track misc task 1 |
| Other Task 2 | `O/T Date` | Track misc task 2 |
| Final Walk | `Final walk Date` | Track final walk |

---

## 🔧 **Derived Columns** (Added by `compute_all_unit_fields`)

These columns are **computed at runtime** and added to the DataFrame:

| Column Name | Type | Calculation | Purpose |
|-------------|------|-------------|---------|
| `days_vacant` | int | `today - move_out` | Vacancy age |
| `days_to_be_ready` | int | `move_in - today` | Days until move-in |
| `turn_level` | str | Based on `days_vacant` | Performance classification |
| `unit_blocked` | bool | Based on `comments` field | Flag for holds/issues |
| `lifecycle_label` | str | Mapped from `status` | Ready / In Turn / Not Ready |

---

## 🏷️ **NVM Status Values** (Vacancy States)

### **Current NVM Constants**

The `Nvm` column accepts the following values (case-insensitive):

| NVM Value | Emoji | Meaning | Vacancy Status | Used In Logic |
|-----------|-------|---------|----------------|---------------|
| **`vacant`** | 🟢 (expanders) / 🔴 (unit_cards) | Unit is vacant | ✅ VACANT | Occupancy calc |
| **`smi`** | 🔴 | Scheduled Move-In | ✅ VACANT | Occupancy calc |
| **`notice`** | 📢 | Tenant gave notice | ❌ OCCUPIED | NVM tracking |
| **`moving`** | 📦 | Tenant is moving | ❌ OCCUPIED | NVM tracking |
| **`notice + smi`** | 📢 + 🔴 | **NEW VALUE** | ❌ OCCUPIED | Special case |

### **Vacancy Logic**

```python
# From utils/helpers.py
def is_vacant(nvm_value: object) -> bool:
    """Return True if NVM value indicates vacancy (vacant or smi)."""
    n = normalize_nvm(nvm_value)
    return n in ("vacant", "smi")
```

**Vacancy = `vacant` OR `smi` (case-insensitive)**

Everything else is considered **OCCUPIED**.

---

## 🆕 **NEW NVM Value Detected**

### **`notice + smi`**

**Location:** [src/ui/expanders.py:25](file:///Users/miguelgonzalez/Documents/ActiveProjects/DMRB/src/ui/expanders.py#L25)

```python
nvm_emoji_map = {
    'vacant': '🟢',
    'smi': '🔴',
    'notice': '📢',
    'moving': '📦',
    'notice + smi': '📢 + 🔴'  # NEW
}
```

**Status:** ⚠️ **Only defined in `expanders.py`**, not in `unit_cards.py`

**Recommendation:** Add to `unit_cards.py` for consistency.

---

## ⚠️ **Inconsistencies Detected**

### 1. **NVM Emoji Mismatch**

Different emoji mappings exist in two files:

**[src/ui/expanders.py](file:///Users/miguelgonzalez/Documents/ActiveProjects/DMRB/src/ui/expanders.py#L20-L26):**
```python
nvm_emoji_map = {
    'vacant': '🟢',        # GREEN dot
    'smi': '🔴',
    'notice': '📢',
    'moving': '📦',
    'notice + smi': '📢 + 🔴'
}
```

**[src/ui/unit_cards.py](file:///Users/miguelgonzalez/Documents/ActiveProjects/DMRB/src/ui/unit_cards.py#L37-L42):**
```python
nvm_emoji_map = {
    'vacant': '🔴',        # RED dot (different!)
    'smi': '🔴',
    'notice': '📢',
    'moving': '📦'
    # 'notice + smi' MISSING
}
```

**Impact:** Visual inconsistency across UI components.

### 2. **Missing `notice + smi` in unit_cards.py**

The new combined status is only defined in `expanders.py`.

---

## 🎯 **Column Mapping Flow**

### **Dashboard Page**

```python
column_mapping = {
    'Move-out': 'move_out',
    'Move-in': 'move_in',
    'Nvm': 'nvm',
    'Unit': 'unit_id',
    'Phases': 'phase',
    'Building': 'building'
}

# Rename to snake_case
units_df = units_df.rename(columns=column_mapping)

# Compute derived fields
units_df = compute_all_unit_fields(units_df)

# Rename back for compatibility
units_df = units_df.rename(columns={
    'move_out': 'Move-out',
    'move_in': 'Move-in',
    'nvm': 'Nvm',
    'unit_id': 'Unit',
    'phase': 'Phases',
    'building': 'Building'
})
```

### **Units Page**

```python
column_mapping = {
    'Move-out': 'move_out',
    'Move-in': 'move_in',
    'Nvm': 'nvm',
    'Unit': 'unit_number',
    'Unit id': 'unit_id',    # Different from Dashboard!
    'Phases': 'phase',
    'Building': 'building'
}
```

---

## 📝 **Recommended Actions**

### **1. Standardize NVM Emoji Mapping**

Create a centralized constant in `utils/constants.py`:

```python
# NVM Status Emoji Mapping
NVM_EMOJI_MAP = {
    'vacant': '🟢',
    'smi': '🔴',
    'notice': '📢',
    'moving': '📦',
    'notice + smi': '📢 + 🔴'
}

# Vacancy indicators (for occupancy calculations)
VACANT_STATUSES = ['vacant', 'smi']
```

### **2. Update Both UI Components**

Import and use the centralized mapping in both:
- `src/ui/expanders.py`
- `src/ui/unit_cards.py`

### **3. Document NVM States**

Add to `CONFIGURATION.md`:

```markdown
## NVM Status Values

| Status | Emoji | Vacancy | Description |
|--------|-------|---------|-------------|
| vacant | 🟢 | Yes | Unit is empty |
| smi | 🔴 | Yes | Scheduled Move-In |
| notice | 📢 | No | Tenant notice period |
| moving | 📦 | No | Tenant moving out |
| notice + smi | 📢🔴 | No | Notice + scheduled |
```

---

## 🔍 **Summary**

### **Total Columns Used**

- **8 Excel columns** (Unit sheet)
- **9 task date columns** (Task sheet)
- **5 derived columns** (computed at runtime)

### **NVM States**

- **5 defined values** (`vacant`, `smi`, `notice`, `moving`, `notice + smi`)
- **2 vacancy indicators** (`vacant`, `smi`)
- **1 new value** (`notice + smi` - inconsistently implemented)

### **Issues**

- ⚠️ Emoji inconsistency between `expanders.py` and `unit_cards.py`
- ⚠️ `notice + smi` missing from `unit_cards.py`
- ⚠️ No centralized NVM constants definition

---

**End of Analysis**
