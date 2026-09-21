import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")
DB_PATH = os.path.join(DATA_DIR, "tool_monitor.db")
CSV_PATH = os.path.join(DATA_DIR, "detections.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "best.pt")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

TOOLS = [
    {"slot_id": f"{row}{col}", "name": name, "class_id": i}
    for i, (row, col, name) in enumerate([
        ("A", 1, "Wrench Set"), ("A", 2, "Screwdrivers"), ("A", 3, "Pliers"), ("A", 4, "Bolt Cutter"),
        ("B", 1, "Vise Grips"), ("B", 2, "Level"), ("B", 3, "Tape Measure"), ("B", 4, "Hammer"),
        ("C", 1, "Pipe Wrench"), ("C", 2, "Hex Keys"), ("C", 3, "Crimper"), ("C", 4, "Tool Box"),
    ])
]
BOARD_COLS = 4
NAME_BY_SLOT = {tool["slot_id"]: tool["name"] for tool in TOOLS}
CONF_THRESHOLD = 0.45
CALIBRATION_WARN_DAYS = 7
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_TARGET_ID = os.getenv("LINE_TARGET_ID", "")
LINE_ALERT_COOLDOWN_SEC = 60
APP_TITLE = "AI Equipment & Tool Monitoring"
REFRESH_SEC = 2
COLOR = {"present": "#2DD4BF", "missing": "#FB7185", "misplaced": "#FBBF24", "accent": "#38BDF8"}
