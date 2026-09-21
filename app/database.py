import csv
import os
import sqlite3
from datetime import datetime, timedelta

import config


def get_conn():
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS tools (
      slot_id TEXT PRIMARY KEY, name TEXT NOT NULL, class_id INTEGER NOT NULL,
      status TEXT DEFAULT 'present', last_seen TEXT, borrowed_by TEXT
    );
    CREATE TABLE IF NOT EXISTS checkouts (
      id INTEGER PRIMARY KEY AUTOINCREMENT, slot_id TEXT NOT NULL,
      tool_name TEXT NOT NULL, user_name TEXT NOT NULL,
      checkout_at TEXT NOT NULL, return_at TEXT
    );
    CREATE TABLE IF NOT EXISTS detections (
      id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL,
      slot_id TEXT NOT NULL, status TEXT NOT NULL, confidence REAL
    );
    CREATE TABLE IF NOT EXISTS alerts (
      id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, atype TEXT NOT NULL,
      severity TEXT NOT NULL, slot_id TEXT, message TEXT NOT NULL,
      status TEXT DEFAULT 'open'
    );
    CREATE TABLE IF NOT EXISTS calibration (
      slot_id TEXT PRIMARY KEY, tool_name TEXT NOT NULL, due_date TEXT
    );
    """)
    now = datetime.now().isoformat(timespec="seconds")
    due = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    for tool in config.TOOLS:
        conn.execute("INSERT OR IGNORE INTO tools VALUES (?,?,?,?,?,?)",
                     (tool["slot_id"], tool["name"], tool["class_id"], "present", now, None))
        conn.execute("INSERT OR IGNORE INTO calibration VALUES (?,?,?)",
                     (tool["slot_id"], tool["name"], due))
    conn.commit()
    conn.close()


def get_all_tools():
    conn = get_conn(); rows = conn.execute("SELECT * FROM tools ORDER BY slot_id").fetchall(); conn.close()
    return [dict(row) for row in rows]


def update_tool_status(slot_id, status, borrowed_by=None):
    conn = get_conn()
    conn.execute("UPDATE tools SET status=?, last_seen=?, borrowed_by=? WHERE slot_id=?",
                 (status, datetime.now().isoformat(timespec="seconds"), borrowed_by, slot_id))
    conn.commit(); conn.close()


def status_summary():
    summary = {"present": 0, "missing": 0, "misplaced": 0, "borrowed": 0}
    for tool in get_all_tools(): summary[tool["status"]] = summary.get(tool["status"], 0) + 1
    summary["total"] = sum(summary.values())
    return summary


def borrowed_map():
    conn = get_conn(); rows = conn.execute("SELECT slot_id, borrowed_by FROM tools WHERE borrowed_by IS NOT NULL").fetchall(); conn.close()
    return {row["slot_id"]: row["borrowed_by"] for row in rows}


def checkout_tool(slot_id, user_name):
    conn = get_conn(); name = config.NAME_BY_SLOT.get(slot_id, slot_id)
    conn.execute("INSERT INTO checkouts(slot_id,tool_name,user_name,checkout_at) VALUES(?,?,?,?)",
                 (slot_id, name, user_name, datetime.now().isoformat(timespec="seconds")))
    conn.execute("UPDATE tools SET borrowed_by=?, status='borrowed' WHERE slot_id=?", (user_name, slot_id))
    conn.commit(); conn.close()


def return_tool(slot_id):
    conn = get_conn(); now = datetime.now().isoformat(timespec="seconds")
    conn.execute("UPDATE checkouts SET return_at=? WHERE slot_id=? AND return_at IS NULL", (now, slot_id))
    conn.execute("UPDATE tools SET borrowed_by=NULL, status='present' WHERE slot_id=?", (slot_id,))
    conn.commit(); conn.close()


def get_checkouts(limit=50):
    conn = get_conn(); rows = conn.execute("SELECT * FROM checkouts ORDER BY id DESC LIMIT ?", (limit,)).fetchall(); conn.close()
    return [dict(row) for row in rows]


def log_detection(slot_id, status, confidence):
    ts = datetime.now().isoformat(timespec="seconds")
    conn = get_conn(); conn.execute("INSERT INTO detections(ts,slot_id,status,confidence) VALUES(?,?,?,?)", (ts, slot_id, status, confidence)); conn.commit(); conn.close()
    os.makedirs(os.path.dirname(config.CSV_PATH), exist_ok=True)
    new_file = not os.path.exists(config.CSV_PATH)
    with open(config.CSV_PATH, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if new_file: writer.writerow(["timestamp", "slot_id", "status", "confidence"])
        writer.writerow([ts, slot_id, status, confidence])


def usage_stats():
    conn = get_conn(); rows = conn.execute("SELECT tool_name, COUNT(*) times FROM checkouts GROUP BY tool_name ORDER BY times DESC").fetchall(); conn.close()
    return [dict(row) for row in rows]


def add_alert(atype, severity, message, slot_id=None):
    conn = get_conn(); conn.execute("INSERT INTO alerts(ts,atype,severity,slot_id,message) VALUES(?,?,?,?,?)", (datetime.now().isoformat(timespec="seconds"), atype, severity, slot_id, message)); conn.commit(); conn.close()


def get_alerts(limit=50, only_open=False):
    conn = get_conn(); query = "SELECT * FROM alerts" + (" WHERE status='open'" if only_open else "") + " ORDER BY id DESC LIMIT ?"; rows = conn.execute(query, (limit,)).fetchall(); conn.close()
    return [dict(row) for row in rows]


def recent_alert_exists(atype, slot_id, seconds=300):
    conn = get_conn(); since = (datetime.now() - timedelta(seconds=seconds)).isoformat(timespec="seconds")
    row = conn.execute("SELECT 1 FROM alerts WHERE atype=? AND slot_id=? AND ts>=? LIMIT 1", (atype, slot_id, since)).fetchone(); conn.close()
    return row is not None


def calibration_due_soon():
    conn = get_conn(); rows = conn.execute("SELECT * FROM calibration ORDER BY due_date").fetchall(); conn.close(); result = []
    for row in rows:
        if not row["due_date"]: continue
        days = (datetime.strptime(row["due_date"], "%Y-%m-%d").date() - datetime.now().date()).days
        if days <= config.CALIBRATION_WARN_DAYS: result.append({**dict(row), "days_left": days})
    return result


def trend_presence(minutes=120):
    since = (datetime.now() - timedelta(minutes=minutes)).isoformat(timespec="seconds")
    conn = get_conn(); rows = conn.execute("SELECT status FROM detections WHERE ts>=?", (since,)).fetchall(); conn.close()
    if not rows: return []
    good = sum(row["status"] in ("present", "borrowed") for row in rows)
    return [{"ts": datetime.now().strftime("%H:%M"), "rate": good / len(rows)}]


def reset_system():
    conn = get_conn(); now = datetime.now().isoformat(timespec="seconds")
    conn.execute("UPDATE tools SET status='present', borrowed_by=NULL, last_seen=?", (now,))
    for table in ("checkouts", "alerts", "detections"): conn.execute(f"DELETE FROM {table}")
    conn.commit(); conn.close()
    if os.path.exists(config.CSV_PATH): os.remove(config.CSV_PATH)
