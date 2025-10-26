# AGENT_README

## 1. Repository Overview
- Frameworks
  - Streamlit (UI and app engine)
  - Pandas (data manipulation)
  - OpenPyXL (Excel reading)
  - Requests (Google Sheets download)
  - streamlit-autorefresh (optional auto-refresh)
- Directory layout (top-level only)
  - `app.py` – Streamlit entrypoint; redirects to Home page
  - `pages/` – Streamlit pages (Home, Dashboard, Units)
  - `src/core/` – Data access and business logic (calculators, loaders, aggregations)
  - `src/ui/` – UI components (cards, expanders, sections, refresh controls)
  - `src/utils/` – Utilities (styling, logging, helpers)
  - `.streamlit/` – Streamlit config + secrets template
  - `tests/` – Smoke tests (import checks)
- App boot sequence
  1. `streamlit run app.py`
  2. `app.py` calls `st.switch_page("pages/0_🏠_Home.py")`
  3. Pages add `src` to `sys.path` (see Known Issues) and import core/ui/utils
  4. Pages call `utils.styling.inject_css()` to apply shared CSS
  5. Pages load data via `core.data_loader` → `core.datasource`
  6. Calculations via `core.data_logic.compute_all_unit_fields()` and aggregations via `core.phase_logic`
  7. UI components render sections/cards using data and metrics
- Data flow summary
  - Source: `core.datasource.get_excel_file()` loads Google Sheets (bytes → ExcelFile). `core.data_loader` can prefer a local Excel if a valid `file_path` is provided.
  - Processing: `core.data_logic.compute_all_unit_fields()` adds derived fields; `core.phase_logic` builds Phase and All-Units structures for UI.
  - Presentation: Pages use `src/ui/*` components to render KPI cards, expanders, and task lists.

## 2. Core Logic Map
- `core/data_logic.py`
  - Purpose: Per-unit calculators and derived field aggregation
  - Functions
    - `compute_days_vacant(row)` – days since move-out
    - `compute_days_to_be_ready(row)` – days until scheduled move-in
    - `compute_turn_level(row)` – classify readiness/turn status
    - `compute_unit_blocked(row)` – detect blocked unit via comments
    - `compute_lifecycle_label(row)` – Ready/In Turn/Not Ready
    - `compute_all_unit_fields(df)` – add all derived columns to DataFrame
  - Dependencies: pandas, datetime; logs via `core.logger`
  - Used by: Dashboard and Units pages; `core.phase_logic`
- `core/task_logic.py`
  - Purpose: Task filtering and hierarchy mapping for UI
  - Functions
    - `parse_unit_id(unit_id)` – parse Phase/Building/Unit from string
    - `get_tasks_for_date(tasks_df, target_date)` – filter tasks by date and add hierarchy fields
    - `get_yesterday_tasks(tasks_df)` – convenience wrapper
    - `group_tasks_by_hierarchy(tasks)` – Phase → Building → Unit mapping
  - Used by: Dashboard page (Walk of the Day), `ui/task_cards`
- `core/phase_logic.py`
  - Purpose: Build Phase Overview and All-Units lists for UI
  - Functions
    - `build_phase_overview(units_df, today)` – per-phase building stats, move events, and vacant unit snippets
    - `build_all_units(units_df)` – flat list of units with status and day counters
  - Dependencies: `utils.helpers`, pandas
  - Used by: Dashboard page
- `core/data_loader.py`
  - Purpose: Load `Unit` and `Task` sheets
  - Behavior: If `file_path` is provided and exists → local Excel; else → `core.datasource.get_excel_file()` (Google Sheets)
  - Functions: `load_units_sheet(file_path=None)`, `load_task_sheet(file_path=None)`
- `core/datasource.py`
  - Purpose: Google Sheets download + cache via Streamlit
  - Functions: `get_gdrive_url()`, `load_excel_bytes()`, `get_excel_file()`, `clear_data_cache()`, `get_last_updated()`, `get_data_source_info()`
- `core/logger.py`
  - Purpose: Backward-compatible re-export of `utils.logger.log_event`

## 3. UI Structure
- Pages
  - `pages/0_🏠_Home.py` – Navigation entry; injects CSS; links to Dashboard/Units
  - `pages/1_📊_Dashboard.py` – KPIs, Move Activity, Walk of the Day, Phase Overview, All Units; uses `core.phase_logic`
  - `pages/2_🏢_Units.py` – Per-unit lifecycle tabs and KPIs; uses `core.data_logic` and `ui.unit_viewmodels`
- Components
  - `ui/refresh_controls.py` – Unified sidebar refresh and source banner
  - `ui/task_cards.py` – Hierarchical task rendering (Phase → Building → Unit)
  - `ui/expanders.py` – Phase/Building/Unit expanders; expects unit dicts
  - `ui/hero_cards.py` – KPI card renderers
  - `ui/toggle_controls.py` – Expand/collapse and view options
  - `ui/sections.py` – Generic section/tab framework
  - `ui/unit_cards.py` – Unit row with metrics; compact layout
  - `ui/unit_viewmodels.py` – Build view models for unit card consumption
  - `ui/dividers.py` – Simple headings and dividers
- Page dependencies
  - Dashboard → `core.data_loader`, `core.data_logic`, `core.phase_logic`, `ui.refresh_controls`, `ui.*`
  - Units → `core.data_loader`, `core.data_logic`, `ui.refresh_controls`, `ui.unit_viewmodels`, `ui.*`
  - Home → `utils.styling`

## 4. Data Source Pipeline
- Default: Google Sheets via `core.datasource`
- Optional: Local Excel if a valid path is provided to `core.data_loader` functions
- Modules: `core/data_loader.py`, `core/datasource.py`
- Key functions
  - `core.datasource.get_excel_file()` → `pd.ExcelFile`
  - `core.data_loader.load_units_sheet(file_path=None)` → `pd.DataFrame`
  - `core.data_loader.load_task_sheet(file_path=None)` → `pd.DataFrame`

## 5. Styling and Theming
- CSS injection: `utils/styling.inject_css()` (reads `src/utils/styles.css`)
- Theme: `.streamlit/config.toml` (dark)
- Requirement: Call `inject_css()` on pages using CSS variables

## 6. Known Deprecated or Legacy Modules
- `utils/timers.py` – Deprecated; replaced by `ui/refresh_controls.py` (module warns on import)
- Manual `sys.path.insert` calls – keep a single centralized insert at startup; avoid per-module path hacks

## 7. Naming & Consistency Rules
- Metrics: Use `days_to_be_ready` (not `days_to_rent`)
- Calculator function names: `compute_*`, `parse_*`, `group_*`
- No inline re-computation of core metrics in pages; use `core.data_logic` and `core.phase_logic`
- Use snake_case for Python; lower-case filenames

## 8. Repo Dependencies
- `streamlit` – UI runtime and caching
- `pandas` – data manipulation
- `openpyxl` – Excel parsing
- `requests` – download Google Sheets export
- `streamlit-autorefresh` – optional auto-refresh in UI

## 9. Linting and Type Rules
- Linter: Ruff configured in `pyproject.toml` (unused imports, isort, pyflakes)
- Type checks: mypy config present in `pyproject.toml` (lenient for imports)
- Basic smoke test: `tests/test_imports.py` imports core/ui/utils modules

## 10. Operational Constraints
- External network required for Google Sheets mode
- Calculators return pure values/DataFrames (no side effects beyond logging)
- Pages should not mutate DataFrames from `core.data_logic` in place

## 11. Current Known Issues
- Per-page `sys.path.insert` remains in `pages/*`; recommended to centralize in `app.py`
- Some page-level inline CSS blocks remain; consider moving into `src/utils/styles.css`
- Deprecated `utils/timers.py` kept for compatibility; do not import in new code

## 12. Update Policy
- Regenerate AGENT_README.md after structural changes (new modules, moved logic, or new pages)
- Treat this file as authoritative for module dependencies and data flow

```json
{
  "entrypoint": "app.py",
  "core_modules": [
    "core/data_logic.py",
    "core/task_logic.py",
    "core/phase_logic.py",
    "core/data_loader.py",
    "core/datasource.py",
    "core/logger.py"
  ],
  "ui_pages": [
    "pages/0_🏠_Home.py",
    "pages/1_📊_Dashboard.py",
    "pages/2_🏢_Units.py"
  ],
  "ui_components": [
    "ui/refresh_controls.py",
    "ui/task_cards.py",
    "ui/expanders.py",
    "ui/hero_cards.py",
    "ui/toggle_controls.py",
    "ui/sections.py",
    "ui/unit_cards.py",
    "ui/unit_viewmodels.py",
    "ui/dividers.py"
  ],
  "utils_modules": [
    "utils/helpers.py",
    "utils/styling.py",
    "utils/logger.py"
  ],
  "deprecated_modules": [
    "utils/timers.py"
  ],
  "data_source": "Google Sheets (fallback to local Excel when file_path exists)",
  "pending_features": [
    "Centralize sys.path configuration in app.py",
    "Move inline page CSS into shared stylesheet",
    "Add CI to run Ruff/Mypy/tests"
  ]
}
```

