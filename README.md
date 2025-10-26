# 🍁 Thousand Oaks - DMRB Make-Ready Dashboard

> Real-time property operations dashboard for apartment make-ready tracking and occupancy management.

## 📊 Overview

The DMRB Dashboard provides operational visibility for the Thousand Oaks property, tracking 1,300 apartment units across 3 phases. Monitor vacancy metrics, unit lifecycles, and move activity in real-time.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Excel data file: `data/DRMB.xlsx`

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd DMRB

# Install dependencies
pip install streamlit pandas openpyxl

# Run the dashboard
streamlit run app.py
```

## 📁 Project Structure

```
dmrb/
├── data/
│   └── DRMB.xlsx                 # Source of truth (Excel workbook)
│
├── src/
│   ├── app.py                    # Main Streamlit entrypoint (redirects to pages)
│   │
│   ├── pages/
│   │   └── (Streamlit pages live in repo-level `pages/`)
│   │
│   ├── core/
│   │   ├── data_loader.py        # Excel I/O & DataFrame structuring
│   │   ├── data_logic.py         # Business rules & calculations
│   │   ├── phase_logic.py        # Phase/All-units aggregations
│   │   └── logger.py             # Logging utilities
│   │
│   ├── ui/
│   │   ├── hero_cards.py         # KPI visualization components
│   │   ├── expanders.py          # Phase→Building→Unit displays
│   │   └── dividers.py           # Visual separators
│   │
│   └── utils/
│       ├── constants.py          # Global configuration
│       ├── helpers.py            # Formatting & shared logic (NVM/date)
│       ├── timers.py             # Auto-refresh utilities
│       ├── logger.py             # Operational logging
│       └── styling.py            # CSS injection
│
├── pages/                        # Streamlit pages
│   ├── 0_🏠_Home.py
│   ├── 1_📊_Dashboard.py
│   └── 2_🏢_Units.py
│
└── (additional docs/scripts omitted)
```

## 🎯 Key Features

### Dashboard Page (`pages/1_📊_Dashboard.py`)
- **Top KPIs**: Total units, vacant units, occupied units, occupancy %
- **Phase Overview**: Hierarchical view (Phase → Building → Unit)
- **Vacancy Details**: Days vacant, move-in/out dates, days to rent
- **Move Activity**: Today's move-ins and move-outs per building
- **All Units View**: Sortable list by vacancy age

### Units Lifecycle Page (`pages/2_🏢_Units.py`)
- **Lifecycle Stages**: Notice → Vacant → In Turn → Ready
- **Turn Performance**: On Track, Lagging, Delayed, Critical, Exception
- **Stage Breakdown**: Tabbed views for each lifecycle stage
- **Blocked Units**: Flag units with holds or issues
- **Days Tracking**: Days vacant, days to ready

## 📊 Data Schema

### Required Excel Columns (Unit Sheet)

| Column    | Type      | Description                          |
|-----------|-----------|--------------------------------------|
| Unit      | String    | Unit identifier (e.g., "210")        |
| Phases    | Integer   | Phase number (1, 2, or 3)            |
| Building  | Integer   | Building number                      |
| Nvm       | String    | Vacancy status (vacant/smi/notice)   |
| Move-out  | DateTime  | Tenant move-out date                 |
| Move-in   | DateTime  | Scheduled move-in date               |

### Vacancy Logic

```python
VACANT = Nvm IN ["vacant", "smi"] (case-insensitive)
OCCUPIED = Everything else (including NaN, "MOVE IN", "NOTICE")
```

## 🎨 Styling

The dashboard uses a **monochrome black & gray theme** with CSS variables:

- `--gray-50`: #0b0b0b (Page background)
- `--gray-100`: #141414 (Phase cards)
- `--gray-200`: #1e1e1e (Building cards)
- `--gray-300`: #2a2a2a (Unit cards)
- `--gray-900`: #eaeaea (Primary text)

Custom styles in `src/utils/styles.css`.

## 🔧 Configuration

Edit `src/utils/constants.py` for global settings:

```python
EXCEL_FILE_PATH = "data/DRMB.xlsx"
REQUIRED_SHEETS = ["Unit", "Task"]
REFRESH_INTERVAL_MIN = 5
TOTAL_UNITS = 1300
```

## 📝 Business Rules

1. **Total Units**: Fixed at 1,300 (entire property)
2. **Occupancy %**: `(Occupied Units / Total Units) × 100`
3. **Days Vacant**: `Today - Move-out Date`
4. **Days to Rent**: `Move-in Date - Today`
5. **Turn Performance**:
   - On Track: ≤ 8 days
   - Lagging: 9-15 days
   - Delayed: 16-25 days
   - Critical: 26-30 days
   - Exception: > 30 days

## 🔄 Refresh Strategy

- **Manual Refresh**: Sidebar button clears cache and reloads data
- **Auto-Refresh**: Configurable via `REFRESH_INTERVAL_MIN` (not yet implemented)
- **Last Updated**: Timestamp shown in sidebar

## 🧪 Development

### Running Tests
```bash
# (Tests not yet implemented)
pytest tests/
```

### Code Quality
```bash
# Type checking
mypy src/

# Linting
flake8 src/
```

## 📚 Documentation

  (legacy docs omitted for brevity)

## 🛠️ Tech Stack

- **Streamlit**: Web framework
- **Pandas**: Data manipulation
- **OpenPyXL**: Excel file handling
- **Python 3.8+**: Core language

## 📄 License

Internal use only. © 2025 Thousand Oaks

## 👤 Author

**Miguel González Almonte**  
Property Manager | Thousand Oaks

---

**Version**: 0.1.0  
**Last Updated**: 2025-10-25

---

# 🧭 Streamlit Page Intent — **Dashboard**

## 🏷️ Page Identity

* **Page Name:** Dashboard
* **Module Path:** `src/pages/dashboard.py`
* **Primary Owner:** Miguel (Make-Ready Coordinator / Dev)
* **Last Updated:** 2025-10-24

---

## 🎯 Page Intent & Purpose

**One glance = operational truth.**
The Dashboard gives a real-time, **property-wide snapshot** of make-ready health: occupancy, vacancy, readiness, and today’s operational focus (move-outs, move-ins, and tasks requiring follow-up). It’s the **cockpit** for morning stand-ups and quick decisions, not deep investigation.

**Non-goal:** It’s not for editing, drilling into unit history, or vendor performance analysis (those live on other pages).

---

## 👤 Primary Users & Outcomes

| User                   | Outcome                                     | Why It Matters                              |
| ---------------------- | ------------------------------------------- | ------------------------------------------- |
| Make-Ready Coordinator | See what needs attention **today**          | Directs calls, vendor nudges, and walks     |
| Property Manager       | Understand overall **turn pipeline health** | Sets priorities, communicates to leadership |
| Maintenance Lead       | See **work at risk** and resource needs     | Shifts crews, unblocks bottlenecks fast     |

---

## 📊 Core Value Displayed

**Top KPI Row (global, simple, stable):**

* **Total Units**
* **Occupied Units**
* **Vacant Units**
* **Occupancy %**
* **Vacancy %**
* *(Optional)* **Avg Days Vacant**

**Middle “Data Section” (expanders with real context):**

* **Move-Outs (Today+)** → Phase → Building → Unit rows (inline, not tables)
  *Fields:* Unit ID • Move-Out Date • Status
* **Move-Ins (Tomorrow)** → same hierarchy
  *Fields:* Unit ID • Move-In Date • Status
* **Today’s Follow-Up Tasks** (the “24-hour walk window”: tasks completed **yesterday**, to be walked **today**), grouped by category
  *Fields:* Unit ID • Task • Vendor • Due Date • Status • Days Vacant

**Bottom “Hero KPI Footer Summary” (recap):**

* **Units Ready This Week**
* **Tasks Completed Yesterday**
* **Open Tasks (Today)**
* **Avg Turn Time (rolling)**

---

## 🧱 Layout & Interaction Model

**Canonical structure (fixed across app):**

1. **Property Header** (community name + timestamp)
2. **KPI Row** (adaptive to page, but stable format)
3. **Divider**
4. **Expanders / Data Section** (Phase → Building → Unit)
5. **Divider**
6. **Hero KPI Footer Summary** (totals/recap)

**Interactions (simple by design):**

* **Expanders only** (no filters in MVP)
* Rows are **inline cards** with dividers, not tables
* **Auto-refresh** every 5 minutes or on page reload
* No write actions, no notifications from here

---

## 🧠 Data Logic & Rules (Dashboard-specific)

* **Source of Truth:** `data/DMRB.xls` (Units + Tasks)
* **Follow-Up Tasks Window:** show tasks whose **due date == yesterday** (walk-today rule). Hide after **24h**.
* **Move-Outs (Today+):** include **today and future** move-outs.
* **Move-Ins (Tomorrow):** include **tomorrow only** (planning lens).
* **Sorting:** unit rows sorted by **Days Vacant (desc: oldest first)** where applicable.
* **No manual status toggles**—visibility is **time-based logic** only.

---

## 🔒 Safety & Guardrails (MVP)

* **Validator required** before render: Units sheet present; columns like `Unit ID, Phase, Building, Move Out, Move In, Days Vacant, Status, Type, Sqft`.
* **Constants** for sheet names/status enums to avoid silent mismatches.
* **Logger** writes load/logic issues to `logs/dmrb.log` (UI shows a soft warning, never crashes).
* **Defensive defaults:** if a KPI column is missing, render “N/A” for that metric instead of failing.

---

## ⚙️ Dependencies & Shared Modules

| Module                | Role                              |
| --------------------- | --------------------------------- |
| `core/data_loader.py` | Cached Excel read (`DMRB.xls`)    |
| `core/phase_logic.py` | Phase and list aggregations       |
| `core/data_logic.py`  | KPI math + task window filtering  |
| `ui/hero_cards.py`    | KPI card rendering                |
| `ui/expanders.py`     | Phase → Building → Unit layouts   |
| `utils/logger.py`     | Error/info logging                |
| `core/constants.py`   | Paths, statuses, refresh interval |

---

## 📦 Outputs (What the page “produces”)

* **Rendered UI state** (structured, scannable picture of today)
* **Aggregated KPI values** (reused by other pages if needed)
* **Implicit focus list** (follow-up tasks = coordinator’s morning action queue)

---

## ✅ Success Criteria (MVP)

* Page loads cleanly even if a sheet/column is missing (warning, not failure)
* A coordinator can **decide the day’s top 3 actions in < 30 seconds**
* All logic is **time-driven and automatic** (no manual updates needed)
* KPI row and footer always reflect the **same underlying data** as the expanders

---

## 🔭 Extensibility (Near-term)

* Optional **phase-level mini KPIs** shown **inside expander headers** (not in the global header)
* “At-risk” highlight (e.g., **Days Vacant > threshold** = subtle badge)
* CSV export of **Today’s Follow-Up Tasks** (“bring to morning huddle”)
* Later: small **sparkline** in footer hero cards (7-day trend)


## 🧩 Scalable Sections & Tabs (Sidebar-Driven)

Enable pages to scale by defining sidebar “sections”, where each section behaves like a subpage within the page and renders one or more rows of tabs.

- Sidebar Sections
  - Each page registers multiple sections (think: subpages).
  - The sidebar lists sections; selecting one updates the main content area.
  - Deep linkable via `?section=` query parameter and persisted in `st.session_state`.

- Per-Section Tab Rows
  - A section can contain one or more tab rows.
  - Each tab row is rendered with Streamlit `st.tabs`, and each tab maps to a renderer function.
  - Supports multiple rows to group related views (e.g., “Moves” row and “Follow-ups” row).

- Proposed API (ui/sections.py)
  - Data structures
    - `Tab(label: str, key: str, render: Callable[[Context], None])`
    - `TabRow(tabs: list[Tab], key: str)`
    - `Section(id: str, title: str, icon: str, rows: list[TabRow])`
  - Render helpers
    - `register_sections(page_id: str, sections: list[Section])`
    - `render_sections(page_id: str, context: dict)` — renders only the active section
  - State & routing
    - Store `active_section` and per-section active tab(s) in `st.session_state`
    - Read/write `st.query_params` for `section` and optional `tab` deep links

- Example Usage

```python
# src/pages/dashboard.py
from ui.sections import Section, TabRow, Tab, render_sections

sections = [
    Section(
        id="kpis",
        title="KPIs",
        icon="📊",
        rows=[
            TabRow([
                Tab("Overview", "kpi_overview", render_kpi_overview),
                Tab("Trends", "kpi_trends", render_kpi_trends),
            ], key="kpi_row_1")
        ],
    ),
    Section(
        id="moves",
        title="Moves",
        icon="🚚",
        rows=[
            TabRow([
                Tab("Move-Outs", "move_outs", render_move_outs),
                Tab("Move-Ins", "move_ins", render_move_ins),
            ], key="moves_row_1"),
            TabRow([
                Tab("Follow-Ups", "followups", render_followups),
            ], key="moves_row_2"),
        ],
    ),
]

context = {"units_df": units_df, "now": datetime.now()}
render_sections(page_id="dashboard", context=context)
```

- Implementation Notes
  - Only render the active section for performance; memoize heavy computations.
  - Load data once per page load; pass a `context` dict to tab renderers.
  - Keep sidebar navigation in `ui.sidebar` and integrate section selection there.
  - Follow consistent keys to avoid Streamlit widget conflicts (`page.section.row.tab`).


---


## 🧭 **DMRB Units Page — Intent & Overview**

The **Units Page** is the **lifecycle command view** of the DMRB system.
If the **Dashboard** shows *the health of the property*, the **Units Page** shows *the story of every apartment*.

This page lets the Make Ready Coordinator track every unit’s journey — from notice to vacancy, through vendor work, and into readiness — in one continuous, structured interface.

It’s not about monitoring numbers. It’s about *understanding flow*: where each unit is today, what’s coming tomorrow, and what’s blocking readiness.

---

## 🧩 **Purpose & Intent**

The Units page exists to:

* Provide **full lifecycle visibility** per unit, including current and upcoming tasks.
* Replace the need to manually cross-check sheets by consolidating *task schedule + metadata*.
* Keep the same hierarchical flow as Dashboard (Phase → Building → Unit), but extend visibility deeper into each unit’s details.

It’s built for **daily coordination** — the operational layer between “what’s happening” (Dashboard) and “what’s next” (NVM).

---

## 👤 **Primary User**

**Role:** Make Ready Coordinator
**Focus:** Unit-level operations, daily task alignment, vendor follow-up
**Frequency:** Continuous (morning + throughout workday)

This is your cockpit when you want to **drill down from property KPIs into exact operational states.**

---

## 📊 **Core Value Displayed**

| Metric / Visualization                             | Purpose / Story                                         | Data Source / Logic Layer      |
| -------------------------------------------------- | ------------------------------------------------------- | ------------------------------ |
| Unit ID + Metadata (move-out/in dates, type, sqft) | Identify every unit’s lifecycle context                 | DMRB.xls → task & unit sheets  |
| Current Task                                       | Show what’s happening in each unit right now            | task_schedule sheet            |
| Next Task                                          | Preview what’s scheduled tomorrow                       | task_schedule sheet            |
| Status                                             | Show whether the unit is ready, in progress, or waiting | computed via data_logic        |
| Days Vacant                                        | Sort units by aging                                     | derived from move-out vs today |
| Days to Rent / Due Date                            | Show readiness goal                                     | DMRB.xls field                 |

Each unit row becomes a **snapshot of readiness** — not a table, but a structured readout block with dividers.

---

## 🧱 **Page Structure**

```
[ Header ]
───────────────────────────────
Property Name (Thousand Oaks)
Last Updated: hh:mm:ss

[ KPI Row ]
───────────────────────────────
Total Units | Occupied | Vacant | Avg Turn Time | Units in Turn

[ Divider ]
───────────────────────────────

[ Tabs ]
───────────────────────────────
Active Units  |  NVM (Notice→Vacant→Move Schedule→Moving)  |  Ready vs Not Ready  |  Archived

[ Expanders ]
───────────────────────────────
• Active Units:
   Phase 1 → Building A/B → Units
   Each Unit = single line card: ID, move-out, vacant days, current/next task, status.
   
• NVM:
   Notice | Vacant | Moving Schedule | Moving (72hr window)
   Same hierarchy, units auto-expire from container once past logic threshold.

• Ready vs Not Ready:
   Phase → Building → Unit
   KPI cards summarizing counts per status.

[ Divider ]
───────────────────────────────

[ Hero KPI Footer ]
───────────────────────────────
Units Ready | Not Ready | Avg Days Vacant | Turns in Progress
```

---

## ⚙️ **Behavior & Logic**

| Behavior                              | Logic                 | Description                      |
| ------------------------------------- | --------------------- | -------------------------------- |
| Auto-refresh                          | every 5 min           | Pulls updated workbook data      |
| Unit sorting                          | Days vacant ascending | Shows oldest first               |
| Conditional visibility                | 24h/72h time windows  | Removes expired data             |
| No manual toggles                     | Tabs define data view | Keeps UX predictable             |
| Same header + KPI schema as Dashboard | Visual continuity     | Reinforces “command center” feel |

---

## 🔗 **Dependencies**

| Module           | Role                                   | Notes                     |
| ---------------- | -------------------------------------- | ------------------------- |
| `data_loader.py` | Reads unit + task sheets               | Caches with st.cache_data |
| `data_logic.py`  | Computes lifecycle and readiness logic | Defines state filters     |
| `phase_logic.py` | Aggregations for pages                 | Reduces duplication       |
| `hero_cards.py`  | Renders KPI rows                       | Shared UI                 |
| `expanders.py`   | Handles nested hierarchy rendering     | Shared with Dashboard     |
| `logger.py`      | Logs refresh and errors                | For auditability          |

---

## 📦 **Output / Deliverable**

| Output Type           | Description                                | Where It’s Used    |
| --------------------- | ------------------------------------------ | ------------------ |
| Streamlit page        | Live lifecycle tracker                     | `/pages/units.py`  |
| Hero cards            | KPI summary at top & bottom                | Shared across app  |
| Dynamic expanders     | Hierarchical visibility per phase/building | Streamlit UI layer |
| DataFrames (internal) | Pre-filtered for logic                     | Cached in memory   |

---

## 🧭 **Summary Snapshot**

| Aspect       | Summary                                           |
| ------------ | ------------------------------------------------- |
| Intent       | Deep visibility into unit lifecycle and readiness |
| Primary User | Make Ready Coordinator                            |
| Core Action  | View and track per-unit progress                  |
| Key Insight  | What’s being worked, what’s next, and what’s late |
| Output Type  | Streamlit reactive page                           |

---

Excel (DMRB.xls)
     ↓
[ Validator ] → Warns & filters structure
     ↓
[ Loader ] → Caches clean data
     ↓
[ Logic ] → Uses constants safely
     ↓
[ Logger ] → Captures issues quietly
     ↓
[ Hero Cards ] → Renders KPI rows
     ↓
[ Expanders ] → Handles nested hierarchy rendering
     ↓
[ Units Page ] → Live lifecycle tracker

---


[ 🏷 Property Header ]
─────────────────────────────
[ 📊 KPI ROW ]
    → High-level property + page-specific metrics
─────────────────────────────
[ TABS ]
    → Each tab = lifecycle segment (e.g., Active Units | NVM | Ready vs Not Ready)
─────────────────────────────
[ DATA SECTION ]
    → Within each tab:
        ▪ Top: contextual mini-KPIs (hero cards per phase/building)
        ▪ Middle: expanders (Phase → Building → Unit)
        ▪ Inside Unit Row: inline metadata fields
─────────────────────────────
[ 📈 Hero KPI Footer Summary ]
    → Aggregated metrics (e.g., total active tasks, avg. days vacant)
___
