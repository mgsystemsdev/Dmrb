# 🔢 Unit Card Update Count - How Many Sections Need Updating?

**Question:** How many sections use the inconsistent unit card rendering?  
**Answer:** **1 PAGE** with **4 TAB SECTIONS** = **ONE LOCATION** to fix

---

## 📊 **Current State Summary**

### **✅ Dashboard Page** - Already Uses Correct Component
**File:** `pages/1_📊_Dashboard.py`  
**Function:** `render_unit_row()` (from `ui/expanders.py`)  
**Status:** ✅ **CORRECT** - Uses `.unit-card` CSS styling

**Locations (3):**
1. **Line 182** - Move-Outs Today+ tab
2. **Line 209** - Move-Ins Tomorrow tab  
3. **Line 299** - All Units section

**All use:** `render_unit_row(unit)` ✅

---

### **❌ Units Page** - Uses Wrong Component
**File:** `pages/2_🏢_Units.py`  
**Function:** `render_enhanced_unit_row()` (from `ui/unit_cards.py`)  
**Status:** ❌ **INCONSISTENT** - Uses `st.columns()` instead of `.unit-card`

**Location:** **ONE FUNCTION** that gets called by **4 TAB SECTIONS**

---

## 🎯 **The Single Location to Fix**

### **Function:** `render_units_by_hierarchy()` 
**Line:** 149 in `pages/2_🏢_Units.py`

```python
# Current (WRONG):
def render_units_by_hierarchy(units_subset, tasks_df, title_prefix=""):
    # ... phase and building loops ...
    for idx, (_, unit_row) in enumerate(building_units.iterrows()):
        render_enhanced_unit_row(build_enhanced_unit(unit_row, tasks_df))  # ❌ WRONG
        if idx < len(building_units) - 1:
            st.markdown('<div class="hairline"></div>', unsafe_allow_html=True)
```

**This ONE function is called by ALL 4 tabs:**

1. **Active Pipeline Tab** (Line 163)
   ```python
   def render_active_units_tab(context):
       # ...
       render_units_by_hierarchy(active, tasks_df, "in active pipeline")  # → Line 149
   ```

2. **Notice Tab** (Line 175 - inside NVM tab)
   ```python
   with nvm_tabs[0]:
       # ...
       render_units_by_hierarchy(notice, tasks_df, "on notice")  # → Line 149
   ```

3. **Vacant Tab** (Line 182 - inside NVM tab)
   ```python
   with nvm_tabs[1]:
       # ...
       render_units_by_hierarchy(vacant, tasks_df, "vacant")  # → Line 149
   ```

4. **Moving Tab** (Line 189 - inside NVM tab)
   ```python
   with nvm_tabs[2]:
       # ...
       render_units_by_hierarchy(moving, tasks_df, "moving in 72h")  # → Line 149
   ```

5. **Ready Tab** (Line 199 - inside Ready vs Not Ready)
   ```python
   with ready_tabs[0]:
       # ...
       render_units_by_hierarchy(ready, tasks_df, "ready")  # → Line 149
   ```

6. **Not Ready Tab** (Line 205 - inside Ready vs Not Ready)
   ```python
   with ready_tabs[1]:
       # ...
       render_units_by_hierarchy(not_ready, tasks_df, "not ready")  # → Line 149
   ```

7. **All Units Tab** (Line 210)
   ```python
   def render_all_units_tab(context):
       # ...
       render_units_by_hierarchy(all_units, tasks_df, "total")  # → Line 149
   ```

---

## ✅ **The Fix: Change ONE Line**

### **Current Code (Line 149):**
```python
render_enhanced_unit_row(build_enhanced_unit(unit_row, tasks_df))
```

### **New Code:**
```python
from ui.expanders import render_unit_row
unit_data = build_enhanced_unit(unit_row, tasks_df)
render_unit_row(unit_data)
```

**Result:** All 7 tab sections (across 4 main tabs) will automatically get consistent styling!

---

## 📋 **Affected Sections Breakdown**

### **Units Page Tabs:**

| Tab | Sub-Section | Calls render_units_by_hierarchy? | Gets Fixed? |
|-----|-------------|----------------------------------|-------------|
| **Active Pipeline** | Main content | ✅ Yes (Line 163) | ✅ Yes |
| **NVM** | Notice | ✅ Yes (Line 175) | ✅ Yes |
| **NVM** | Vacant | ✅ Yes (Line 182) | ✅ Yes |
| **NVM** | Moving | ✅ Yes (Line 189) | ✅ Yes |
| **Ready vs Not** | Ready | ✅ Yes (Line 199) | ✅ Yes |
| **Ready vs Not** | Not Ready | ✅ Yes (Line 205) | ✅ Yes |
| **All Units** | Main content | ✅ Yes (Line 210) | ✅ Yes |

**Total Sections:** 7  
**Lines to Change:** **1** ✅  
**Functions to Update:** **1** ✅

---

## 🔍 **Why Only One Location?**

All unit cards on the Units page are rendered through the **same helper function**:

```
render_active_units_tab()      ─┐
render_nvm_tab()                 │
  ├─ Notice tab                  │
  ├─ Vacant tab                  ├─→ ALL call render_units_by_hierarchy()
  └─ Moving tab                  │       └─→ Line 149: render_enhanced_unit_row()
render_ready_vs_not_tab()        │
  ├─ Ready tab                   │
  └─ Not Ready tab               │
render_all_units_tab()          ─┘
```

**Fix Line 149 → All 7 sections get fixed automatically!**

---

## 🎯 **Summary**

### **Question:** How many sections need updating?

### **Answer:**
- **Files to Edit:** 1 file (`pages/2_🏢_Units.py`)
- **Functions to Update:** 1 function (`render_units_by_hierarchy`)
- **Lines to Change:** 1 line (Line 149)
- **Sections That Get Fixed:** 7 tab sections
- **Import to Add:** 1 import statement

---

## 📝 **Step-by-Step Fix**

### **Step 1:** Update Import (Line 21)
```python
# OLD:
from ui.unit_cards import render_enhanced_unit_row, render_unit_kpi_cards

# NEW:
from ui.unit_cards import render_unit_kpi_cards
from ui.expanders import render_unit_row
```

### **Step 2:** Update render_units_by_hierarchy (Line 149)
```python
# OLD:
render_enhanced_unit_row(build_enhanced_unit(unit_row, tasks_df))

# NEW:
render_unit_row(build_enhanced_unit(unit_row, tasks_df))
```

### **Step 3:** (Optional) Deprecate old function
Comment or remove `render_enhanced_unit_row()` from `src/ui/unit_cards.py`

---

## ✅ **Expected Result**

After the fix, ALL unit cards across BOTH pages will have:

✅ Same dark gray background (`gray-300`)  
✅ Same subtle left border  
✅ Same rounded corners  
✅ Same hover effect (lift + lighten)  
✅ Same compact grid layout  
✅ Same typography  
✅ Same spacing  

**Visual Consistency: 100%**

---

## 🚀 **Efficiency Score**

- **Sections affected:** 7
- **Changes required:** 2 (1 import + 1 function call)
- **Files modified:** 1
- **Time to fix:** < 2 minutes
- **Impact:** Complete visual consistency across entire app

**Return on Investment:** 🔥 **EXTREMELY HIGH**

---

**End of Count Report**
