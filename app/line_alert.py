import os
import time
import requests

import config

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
_last_sent = {}


def _can_send(key):
    now = time.time()
    previous = _last_sent.get(key)
    if previous is not None and now - previous < config.LINE_ALERT_COOLDOWN_SEC:
        return False
    _last_sent[key] = now
    return True


def send_line(message, dedup_key=None):
    if dedup_key and not _can_send(dedup_key):
        return {"ok": False, "reason": "cooldown"}

    token = config.LINE_CHANNEL_ACCESS_TOKEN
    target = config.LINE_TARGET_ID
    if not token or not target:
        print(f"[LINE SAFE MODE]\n{message}")
        return {"ok": True, "mode": "safe"}

    try:
        response = requests.post(
            LINE_PUSH_URL,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
            json={"to": target, "messages": [{"type": "text", "text": message}]},
            timeout=10,
        )
        if response.status_code == 200:
            return {"ok": True, "mode": "live"}
        return {"ok": False, "status": response.status_code, "body": response.text}
    except requests.RequestException as exc:
        return {"ok": False, "error": str(exc)}


def alert_missing(tool_name, slot_id):
    return send_line(f"🚨 Tool Missing Alert\nTool: {tool_name}\nSlot: {slot_id}", f"missing:{slot_id}")


def alert_misplaced(tool_name, expected_slot, current_slot="?"):
    return send_line(f"⚠️ Tool Misplaced\nTool: {tool_name}\nExpected: {expected_slot} → Current: {current_slot}", f"misplaced:{expected_slot}")


def alert_calibration(tool_name, slot_id, days_left):
    return send_line(f"🔧 Calibration Reminder\nTool: {tool_name} ({slot_id})\nเหลืออีก {days_left} วัน", f"calib:{slot_id}")


def alert_checkout(tool_name, slot_id, user):
    return send_line(f"📦 Tool Check-out\nTool: {tool_name}\nSlot: {slot_id}\nBorrower: {user}", f"co:{slot_id}:{int(time.time())}")


def alert_checkin(tool_name, slot_id, user=None):
    return send_line(f"✅ Tool Return\nTool: {tool_name}\nSlot: {slot_id}", f"ci:{slot_id}:{int(time.time())}")
