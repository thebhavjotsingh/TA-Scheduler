"""
Configuration constants for the TA Scheduler application.
"""
import os
import sys

# --- File names and outputs ---
MAX_FILE = "Max Availability.csv"
RESP_FILE = "Responses.csv"
REQ_FILE = "Requirements.csv"
SLOT_OUTPUT_CSV = "slot_summary.csv"
TA_OUTPUT_CSV = "ta_summary.csv"

# --- Scheduling constraints ---
MAX_DAILY_HOURS = 4  # Maximum hours a TA can be assigned in a single day
MAX_LABS_PER_TA = 3  # Maximum number of labs a TA can be assigned to

# --- GUI constants ---
def get_icon_path():
    """Get the correct icon path whether running as script or PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running as script
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_path, 'icon.ico')

ICON_PATH = get_icon_path()
DEFAULT_APP_NAME = "TA Scheduler"
