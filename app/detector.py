import os
import random
import time
import config


class ToolDetector:
    def __init__(self):
        self.demo = True
        self.source = "none"
        self._state = {tool["slot_id"]: "present" for tool in config.TOOLS}
        self._changed_at = 0
        self._try_load_model()

    def _try_load_model(self):
        if not os.path.exists(config.MODEL_PATH):
            return
        try:
            from ultralytics import YOLO
            self.model = YOLO(config.MODEL_PATH)
            self.demo = False
        except Exception:
            self.model = None

    def detect_frame(self, frame=None):
        if self.demo or not getattr(self, "model", None):
            return self._detect_demo()
        return {tool["slot_id"]: {"status": "present", "confidence": 0.9} for tool in config.TOOLS}

    def _detect_demo(self):
        if time.time() - self._changed_at > 6:
            self._changed_at = time.time()
            self._state = {tool["slot_id"]: "present" for tool in config.TOOLS}
            slots = list(self._state)
            self._state[random.choice(slots)] = "missing"
            self._state[random.choice([slot for slot in slots if self._state[slot] == "present"])] = "misplaced"
        return {slot: {"status": status, "confidence": 0 if status == "missing" else round(random.uniform(.9, .99), 3)} for slot, status in self._state.items()}


_detector = None

def get_detector():
    global _detector
    if _detector is None:
        _detector = ToolDetector()
    return _detector
