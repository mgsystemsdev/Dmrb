"""
Global constants for the DMRB Dashboard.
These values define required sheets, refresh rates, and common references.
"""


# 🏢 Property Configuration
TOTAL_UNITS = 1300  # Total units in property

# 📊 Excel Configuration
REQUIRED_SHEETS = ["Unit", "Task"]

# ⏱️ Refresh Settings
REFRESH_INTERVAL_MIN = 5  # minutes (used later for scheduler.py)

# 🗂️ File Paths
EXCEL_FILE_PATH = "data/DRMB.xlsx"

# 🎨 Theme & Styling (for CSS alignment)
PRIMARY_COLOR = "#007BFF"
BACKGROUND_COLOR = "#F5F7FA"
TEXT_COLOR = "#222"

# 🧾 Metadata
APP_VERSION = "0.1.0"
APP_NAME = "DMRB Make-Ready Dashboard"

# 🏷️ NVM Status Values (computed from Move-Out/Move-In dates)
NVM_STATUS_MOVE_IN = "MOVE IN"
NVM_STATUS_SMI = "SMI"
NVM_STATUS_VACANT = "VACANT"
NVM_STATUS_NOTICE_SMI = "NOTICE + SMI"
NVM_STATUS_NOTICE = "NOTICE"
NVM_STATUS_BLANK = ""

# NVM Emoji Mapping (centralized)
# Convention: 🟢 Green = Vacant (available), 🔴 Red = Occupied
NVM_EMOJI_MAP = {
    'move in': '🔴',        # Red - occupied (tenant moved in)
    'smi': '🟢',            # Green - vacant with scheduled move-in
    'vacant': '🟢',         # Green - vacant, no move-in scheduled
    'notice + smi': '📢',   # Yellow - occupied, notice given, next tenant scheduled
    'notice': '📢',         # Yellow - occupied, notice given
    'moving': '📦',         # Box - in transition
    '': '⚪'                # White - unknown/blank
}

# Vacancy indicators (for occupancy calculations)
VACANT_STATUSES = ['vacant', 'smi']
