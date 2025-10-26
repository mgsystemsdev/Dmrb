# 🎨 Container Styling Analysis - DMRB Dashboard

**Issue:** Inconsistent container sizes and styling across Dashboard and Units pages  
**Goal:** Create uniform, professional container appearance everywhere

---

## 🔍 **Current State Analysis**

### **Dashboard Page Containers**

| Container | Style | Issues |
|-----------|-------|--------|
| **KPI Section** | `background: var(--gray-100); border: 2px solid var(--gray-400); border-radius: var(--radius-lg); padding: var(--spacing-xl); margin-bottom: 2rem; box-shadow: var(--shadow-xl);` | ✅ Good (reference style) |
| **Walk of the Day** | Same as KPI | ✅ Consistent |
| **Phase Overview** | Same as KPI | ✅ Consistent |
| **All Units** | Same as KPI | ✅ Consistent |

**Dashboard Verdict:** ✅ **CONSISTENT** - All major sections use same container style

---

### **Units Page Containers**

| Container | Style | Issues |
|-----------|-------|--------|
| **KPI Row** | **NO CONTAINER** (just st.columns) | ❌ Missing wrapper |
| **Units Overview Tabs** | **INLINE in render_units_by_hierarchy()** | ⚠️ Inconsistent location |
| **Phase Sections** | Uses `.phase-section` class from CSS | ⚠️ Different approach |

**Units Page Issues:**
1. ❌ KPI section has no visual container
2. ⚠️ Tabs section styling defined inside helper function (not at page level)
3. ⚠️ Uses CSS class instead of inline styles (inconsistent with Dashboard)

---

### **Units Page - render_units_by_hierarchy() Function**

**Current Location:** Lines 142-196 in `pages/2_🏢_Units.py`

**Current Implementation:**
```python
def render_units_by_hierarchy(units_subset, tasks_df, title_prefix=""):
    # Wrap in styled container matching dashboard
    st.markdown("""
<div class="phase-section" style="background: var(--gray-100); border: 2px solid var(--gray-400); border-radius: var(--radius-lg); padding: var(--spacing-xl); margin-bottom: 2rem; box-shadow: var(--shadow-xl);">
""", unsafe_allow_html=True)
    # ... content ...
    st.markdown('</div>', unsafe_allow_html=True)
```

**Issues:**
- ❌ Container styling is INSIDE the helper function
- ❌ Each tab call creates a new container (tabs should share ONE container)
- ❌ CSS class `.phase-section` conflicts with inline styles

---

## 🎯 **Standard Container Style** (from Dashboard)

```python
SECTION_CONTAINER_STYLE = """
<div style="background: var(--gray-100); border: 2px solid var(--gray-400); border-radius: var(--radius-lg); padding: var(--spacing-xl); margin-bottom: 2rem; box-shadow: var(--shadow-xl);">
"""

SECTION_HEADER_STYLE = """
<h3 style="color: var(--gray-900); margin-top: 0; margin-bottom: 1.25rem; font-size: 1.5rem;">
"""
```

---

## ✅ **Required Changes**

### **1. Create Centralized Container Utility**

**File:** `src/utils/styling.py`

Add:
```python
def render_section_container_start(title: str, icon: str = "") -> None:
    """Render the start of a standard section container."""
    st.markdown(f"""
<div style="background: var(--gray-100); border: 2px solid var(--gray-400); border-radius: var(--radius-lg); padding: var(--spacing-xl); margin-bottom: 2rem; box-shadow: var(--shadow-xl);">
    <h3 style="color: var(--gray-900); margin-top: 0; margin-bottom: 1.25rem; font-size: 1.5rem;">{icon} {title}</h3>
""", unsafe_allow_html=True)

def render_section_container_end() -> None:
    """Render the end of a standard section container."""
    st.markdown('</div>', unsafe_allow_html=True)
```

---

### **2. Update Units Page Structure**

**Current Flow:**
```
KPIs (no container)
↓
Tabs
  ├─ Active Units (calls render_units_by_hierarchy → creates container)
  ├─ NVM (creates 3 sub-containers in tabs)
  ├─ Ready vs Not Ready (creates 2 sub-containers)
  └─ All Units (creates container)
```

**Desired Flow:**
```
KPIs (wrapped in container)
↓
[CONTAINER START: "Units Overview"]
  Tabs
    ├─ Active Units (NO wrapper, just content)
    ├─ NVM (NO wrapper, just nested tabs)
    ├─ Ready vs Not Ready (NO wrapper, nested tabs)
    └─ All Units (NO wrapper, just content)
[CONTAINER END]
```

---

### **3. Fix render_units_by_hierarchy()**

**Remove container logic from function:**
```python
def render_units_by_hierarchy(units_subset, tasks_df, title_prefix=""):
    """Render units grouped by Phase > Building. NO container wrapper."""
    if len(units_subset) == 0:
        st.info("No units to display")
        return

    # Just render content, no wrapping div
    st.caption(f"**{len(units_subset)} units** {title_prefix}")
    st.divider()

    # ... rest of logic ...
```

---

### **4. Wrap Sections at Page Level**

**Units Page - KPI Section:**
```python
from utils.styling import render_section_container_start, render_section_container_end

# Wrap KPIs
render_section_container_start("Key Performance Indicators", "📊")
render_unit_kpi_cards(kpi_metrics)
render_section_container_end()
```

**Units Page - Tabs Section:**
```python
render_section_container_start("Units Overview", "🏠")
# Tabs go here (no individual wrappers inside tabs)
render_section(units_section, context)
render_section_container_end()
```

---

## 📊 **Before vs After**

### **Before (Inconsistent)**
```
Dashboard:
  [Container: KPIs]
  [Container: Move Activity]
  [Container: Walk of Day]
  [Container: Phase Overview]
  [Container: All Units]

Units:
  KPIs (no container)
  Tabs
    ├─ [Container] Active
    ├─ [Container] Notice
    ├─ [Container] Vacant
    ...
```

### **After (Consistent)**
```
Dashboard:
  [Container: KPIs]
  [Container: Move Activity]
  [Container: Walk of Day]
  [Container: Phase Overview]
  [Container: All Units]

Units:
  [Container: KPIs]
  [Container: Units Overview]
    ├─ Tabs (inside container)
    │   ├─ Active (no wrapper)
    │   ├─ NVM tabs (no wrapper)
    │   └─ All (no wrapper)
  [Container: Performance Summary]
```

---

## 🎨 **Visual Hierarchy**

```
Page Title (centered, large)
    ↓
[═══════════════════════════════════]
│ 📊 Section Title                  │
│ ─────────────────────────────────  │
│ Content (KPIs, tabs, or data)     │
│                                    │
[═══════════════════════════════════]
    ↓
[═══════════════════════════════════]
│ 🏠 Section Title                  │
│ ─────────────────────────────────  │
│ Content                            │
[═══════════════════════════════════]
```

---

## ✅ **Implementation Checklist**

- [ ] Add container helpers to `utils/styling.py`
- [ ] Remove `.phase-section` CSS class from Units page
- [ ] Wrap KPI section in container on Units page
- [ ] Remove container logic from `render_units_by_hierarchy()`
- [ ] Wrap tabs section in single container on Units page
- [ ] Add container to Footer KPIs on Units page
- [ ] Verify all containers match Dashboard style
- [ ] Test visual consistency across both pages

---

**End of Analysis**
