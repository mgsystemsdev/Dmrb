# 📦 Unit Card Container Analysis - Dashboard Phase Overview

**Focus:** All Units section in Dashboard → Individual unit card styling  
**Location:** `pages/1_📊_Dashboard.py` → "All Units" section  
**Component:** `render_unit_row()` from `src/ui/expanders.py`

---

## 🎯 **Current Unit Card Structure**

### **Dashboard Page - All Units Section**

```python
# Line 292-304 in pages/1_📊_Dashboard.py
render_section_container_start("All Units", "📋")

all_units = build_all_units(units_df)

with st.expander(f"📋 View All Units ({len(all_units)} total)", expanded=False):
    for idx, unit in enumerate(all_units):
        render_unit_row(unit)  # ← This is the unit card
        if idx < len(all_units) - 1:
            st.divider()

render_section_container_end()
```

**Visual Structure:**
```
┌─────────────────────────────────────────────────┐
│ 📋 All Units                                    │  ← Section container
│ ─────────────────────────────────────────────── │
│  ┌─ 📋 View All Units (X total) ──────────┐   │  ← Expander
│  │                                          │   │
│  │  ┌──────────────────────────────────┐  │   │  ← Unit card
│  │  │ 210  | Move Out | Days | Move In │  │   │
│  │  └──────────────────────────────────┘  │   │
│  │  ─────────────────────────────────────  │   │  ← Divider
│  │  ┌──────────────────────────────────┐  │   │  ← Unit card
│  │  │ 305  | Move Out | Days | Move In │  │   │
│  │  └──────────────────────────────────┘  │   │
│  │                                          │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## 🎨 **Unit Card Styling (from `src/ui/expanders.py`)**

### **HTML Structure**

```html
<div class='unit-card'>
  <div class='row-grid' style='grid-template-columns: 1.1fr 1fr 0.9fr 1fr 0.9fr 1fr;'>
    <div>
      <div class='meta-value'>210</div>  <!-- Unit number -->
    </div>
    <div style='text-align:center;'>
      <div class='meta-label'>Move Out</div>
      <div class='meta-value' style='font-weight:600;'>10/20/25</div>
    </div>
    <div style='text-align:center;'>
      <div class='meta-label'>Days Vac</div>
      <div class='meta-value'>6</div>
    </div>
    <div style='text-align:center;'>
      <div class='meta-label'>Move In</div>
      <div class='meta-value' style='font-weight:600;'>10/30/25</div>
    </div>
    <div style='text-align:center;'>
      <div class='meta-label'>Days Ready</div>
      <div class='meta-value'>4</div>
    </div>
    <div style='text-align:center;'>
      <div class='meta-label'>Nvm</div>
      <div class='meta-value'>🔴 SMI</div>
    </div>
  </div>
</div>
```

### **CSS Classes (from `src/utils/styles.css`)**

```css
.unit-card {
  background: var(--gray-300) !important;     /* #242424 - Dark gray */
  border-left: 1px solid var(--gray-500);     /* #444444 - Subtle left border */
  border-radius: var(--radius-md);            /* 0.5rem - Rounded corners */
  padding: var(--spacing-xs) var(--spacing-sm); /* 0.125rem 0.25rem */
  box-shadow: var(--shadow-sm);               /* Subtle shadow */
  transition: all 0.2s ease;                  /* Smooth hover */
}

.unit-card:hover {
  background: var(--gray-400) !important;     /* #333333 - Lighter on hover */
  transform: translateY(-1px);                /* Slight lift effect */
}
```

**Grid Layout:**
```css
.row-grid {
  grid-template-columns: 1.1fr 1fr 0.9fr 1fr 0.9fr 1fr;
  /* Columns:
     1. Unit Number (1.1fr) - Slightly wider
     2. Move Out (1fr)
     3. Days Vac (0.9fr) - Slightly narrower
     4. Move In (1fr)
     5. Days Ready (0.9fr) - Slightly narrower
     6. Nvm (1fr)
  */
}
```

---

## 🔍 **Key Characteristics**

### **1. Container Hierarchy**

```
Section Container (gray-100, #121212)
  └─ Expander (gray-200, #1a1a1a)
       └─ Unit Card (gray-300, #242424)  ← THIS IS THE UNIT CARD
            └─ Content grid (6 columns)
```

### **2. Visual Properties**

| Property | Value | Purpose |
|----------|-------|---------|
| **Background** | `var(--gray-300)` (#242424) | Distinct from expander |
| **Border** | 1px left border, gray-500 | Subtle left accent |
| **Border Radius** | `var(--radius-md)` (0.5rem) | Rounded corners |
| **Padding** | 0.125rem 0.25rem | Compact spacing |
| **Shadow** | `var(--shadow-sm)` | Depth separation |
| **Hover Effect** | Background → gray-400, lift 1px | Interactive feedback |

### **3. Content Structure**

**6 Columns:**
1. **Unit Number** - Left-aligned, no label
2. **Move Out** - Centered, with label, bold value
3. **Days Vacant** - Centered, with label
4. **Move In** - Centered, with label, bold value
5. **Days Ready** - Centered, with label
6. **Nvm Status** - Centered, with emoji + text

**Typography:**
- Labels: `.meta-label` class (smaller, muted)
- Values: `.meta-value` class (larger, prominent)
- Important dates: `font-weight: 600`

---

## 📊 **Color Palette (Dark Theme)**

```
Background Hierarchy (darkest → lightest):
--gray-50:  #0a0a0a  ← Page background
--gray-100: #121212  ← Section container
--gray-200: #1a1a1a  ← Building/Phase expander
--gray-300: #242424  ← Unit card ★
--gray-400: #333333  ← Borders, hover state
--gray-500: #444444  ← Lines, dividers
--gray-900: #e0e0e0  ← Primary text
```

---

## ⚠️ **Problem: Units Page Unit Cards Different**

### **Dashboard Unit Card** (from `expanders.py`)
```python
render_unit_row(unit)  # Uses .unit-card class
```
- ✅ Background: `gray-300` (#242424)
- ✅ Compact grid layout (6 columns)
- ✅ Hover effect
- ✅ Subtle left border
- ✅ Clean, minimal design

### **Units Page Unit Card** (from `unit_cards.py`)
```python
render_enhanced_unit_row(unit)  # Uses st.columns()
```
- ❌ Uses Streamlit columns (not grid)
- ❌ No `.unit-card` styling
- ❌ No hover effect
- ❌ Different layout approach
- ❌ Inconsistent appearance

---

## 🎯 **Recommendation**

### **Problem**
The Units page uses `render_enhanced_unit_row()` which has a **completely different structure** than the Dashboard's `render_unit_row()`.

### **Solution Options**

#### **Option A: Use Dashboard's render_unit_row() Everywhere** ✅ RECOMMENDED
- Replace `render_enhanced_unit_row()` with `render_unit_row()`
- **Benefit:** Instant consistency
- **Downside:** Units page loses any enhanced features

#### **Option B: Enhance render_unit_row() for Both**
- Add any missing fields from Units page to Dashboard version
- Use the enhanced version everywhere
- **Benefit:** Best of both worlds
- **Downside:** More work

#### **Option C: Apply .unit-card CSS to Units Page**
- Keep separate functions
- Apply same CSS classes to Units version
- **Benefit:** Flexibility
- **Downside:** Code duplication

---

## 📝 **Detailed Comparison**

### **Dashboard: render_unit_row()**
**File:** `src/ui/expanders.py`

```python
def render_unit_row(unit: dict) -> None:
    st.markdown(f"""
<div class='unit-card'>
  <div class='row-grid' style='grid-template-columns: 1.1fr 1fr 0.9fr 1fr 0.9fr 1fr;'>
    <!-- 6 columns of data -->
  </div>
</div>
""", unsafe_allow_html=True)
```

**Columns:**
1. Unit Number
2. Move Out
3. Days Vacant
4. Move In
5. Days Ready
6. Nvm

### **Units Page: render_enhanced_unit_row()**
**File:** `src/ui/unit_cards.py`

```python
def render_enhanced_unit_row(unit: dict) -> None:
    col1, col2, col3, col4, col5, col6 = st.columns([1.5, 1, 0.8, 1, 0.8, 1])
    
    with col1:
        st.markdown(f"<small><strong>{unit.get('unit_id', 'N/A')}</strong></small>", ...)
    # ... Streamlit columns approach ...
```

**Columns:**
1. Unit ID (full path like "P-5 / Bld-1 / U-210")
2. Move Out
3. Days Vacant
4. Move In
5. Days Ready
6. Nvm

**Issues:**
- ❌ No `.unit-card` class
- ❌ No grid layout
- ❌ No hover effect
- ❌ Inconsistent sizing
- ❌ Different visual weight

---

## ✅ **Recommended Fix**

### **Step 1: Update render_unit_row() to handle both cases**

```python
# src/ui/expanders.py
def render_unit_row(unit: dict, show_full_id: bool = False) -> None:
    """
    Render a single, compact unit row with Nvm at the end.
    
    Args:
        unit: Dictionary with unit data
        show_full_id: If True, show full unit_id path (for Units page)
    """
    # Use unit_id if available and requested, else unit_num
    unit_label = unit.get('unit_id', unit.get('unit_num', '—')) if show_full_id else unit.get('unit_num', '—')
    
    # ... rest of render logic ...
```

### **Step 2: Replace Units page function**

```python
# In pages/2_🏢_Units.py
# OLD:
render_enhanced_unit_row(build_enhanced_unit(unit_row, tasks_df))

# NEW:
from ui.expanders import render_unit_row
render_unit_row(build_enhanced_unit(unit_row, tasks_df), show_full_id=True)
```

### **Step 3: Remove duplicate function**

Delete or deprecate `render_enhanced_unit_row()` from `unit_cards.py`

---

## 🎨 **Expected Visual Result**

All unit cards across **Dashboard** and **Units** pages will have:

✅ Same dark gray background (`gray-300`)  
✅ Same subtle left border  
✅ Same rounded corners  
✅ Same hover effect (lift + lighten)  
✅ Same compact grid layout  
✅ Same typography  
✅ Same spacing  

**Result:** Professional, consistent, polished UI

---

**End of Analysis**
