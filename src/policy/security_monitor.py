# security_monitor.py
#
# Event-driven security monitor.
# Priority: critical event > change detection.


import time
from src.vision.change_detector import ChangeDetector
from src.policy.event_policy import EventPolicy


class SecurityMonitor:
    """
    Event-driven endpoint security monitor.

    Levels:
        L0: skip OCR (no security event)
        L1: fast OCR (suspicious event)
        L2: precise OCR (critical event)

    Priority:
        1. L2 event -> ALWAYS run OCR (overrides change detection)
        2. L1 event -> run OCR if screen changed OR cache available
        3. No event -> skip OCR
    """

    def __init__(self, ocr_analyzer, dlp_engine, behavior_tracker, risk_scorer):
        self.ocr = ocr_analyzer
        self.dlp = dlp_engine
        self.tracker = behavior_tracker
        self.risk = risk_scorer

        self.detector = ChangeDetector()
        self.policy = EventPolicy()

        # stats
        self.frames = 0
        self.skipped = 0
        self.ocr_calls = 0
        self.cache_hits = 0
        self.l1_calls = 0
        self.l2_calls = 0

    def process_frame(self, image_path, actions):
        """
        Process a single frame with priority routing.
        """
        self.frames += 1
        t_event = time.time()

        # Stage 1: event policy decides level
        decision = self.policy.decide(actions)
        level = decision["level"]

        # Stage 2: change detection (informational, not blocking)
        changed = self.detector.has_changed(image_path)

        # PRIORITY ROUTING
        # L0: no security event -> skip OCR
        if level == 0:
            self.skipped += 1
            return {
                "level": 0,
                "skipped": True,
                "reason": "no security event",
                "changed": changed,
                "security_response_ms": round((time.time() - t_event) * 1000, 3),
            }

        # L1/L2: run OCR (regardless of change detection)
        if level == 1:
            self.l1_calls += 1
        else:
            self.l2_calls += 1

        result = self.ocr.extract_text(image_path, use_cache=True)

        if result["cache_hit"]:
            self.cache_hits += 1
        else:
            self.ocr_calls += 1

        text = result["text"]
        ocr_confidence = result["avg_confidence"]
        ocr_status = result["status"]

        # Stage 3: behavior tracking
        for a in actions:
            self.tracker.record(a["action"], a["app"])
        behavior = self.tracker.assess_risk()

        # Stage 4: risk scoring
        entities = self._quick_entities(text)
        risk = self.risk.calculate(entities, behavior)

        # Stage 5: DLP decision
        intent = {
            "classification": "EXFILTRATION" if behavior["verdict"] in ["CRITICAL_RISK", "HIGH_RISK"] else "BENIGN",
            "confidence": 0.9,
        }
        dlp_result = self.dlp.evaluate(text, intent, behavior, risk)

        # fail-safe
        if ocr_status == "LOW_CONFIDENCE" and behavior["verdict"] in ["CRITICAL_RISK", "HIGH_RISK"]:
            dlp_result["triggered"] = True
            dlp_result["action"] = "WARN_AND_ALERT"

        total_ms = round((time.time() - t_event) * 1000, 3)

        return {
            "level": level,
            "skipped": False,
            "changed": changed,
            "ocr_status": ocr_status,
            "ocr_confidence": ocr_confidence,
            "cache_hit": result["cache_hit"],
            "action": dlp_result["action"],
            "triggered": dlp_result["triggered"],
            "security_response_ms": total_ms,
        }

    def _quick_entities(self, text):
        """Cheap entity extraction from OCR text."""
        import re
        entities = []
        if re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", text):
            entities.append("PAN")
        if re.search(r"\b[6-9]\d{9}\b", text):
            entities.append("PHONE")
        if re.search(r"\b\d{9,18}\b", text):
            entities.append("ACCOUNT_NUMBER")
        if any(w in text.lower() for w in ["salary", "compensation", "ctc"]):
            entities.append("EMPLOYEE_FINANCIAL_DATA")
        return entities

    def stats(self):
        return {
            "frames": self.frames,
            "skipped": self.skipped,
            "ocr_calls": self.ocr_calls,
            "cache_hits": self.cache_hits,
            "l1_calls": self.l1_calls,
            "l2_calls": self.l2_calls,
            "policy": self.policy.stats(),
        }