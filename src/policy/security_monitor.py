# security_monitor.py

import time
from src.vision.change_detector import ChangeDetector
from src.policy.event_policy import EventPolicy
from src.policy.data_flow import DataFlowGraph
from src.policy.session_risk import SessionRisk


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

    Coverage gate:
        On L2 events, if OCR confidence is low OR no sensitive entities are
        detected, escalate to a full precise OCR pass before DLP decision.
        This prevents an optimized ROI pass from missing a PAN/phone.

    Data flow + session risk:
        Tracks data movement across apps and accumulates session-level risk
        to catch insider-threat patterns across multiple events.
    """

    def __init__(self, ocr_analyzer, dlp_engine, behavior_tracker, risk_scorer):
        self.ocr = ocr_analyzer
        self.dlp = dlp_engine
        self.tracker = behavior_tracker
        self.risk = risk_scorer

        self.detector = ChangeDetector()
        self.policy = EventPolicy()
        self.flow = DataFlowGraph()
        self.session_risk = SessionRisk()

        # stats
        self.frames = 0
        self.skipped = 0
        self.ocr_calls = 0
        self.cache_hits = 0
        self.l1_calls = 0
        self.l2_calls = 0
        self.coverage_gate_hits = 0

    def process_frame(self, image_path, actions):
        """
        Process a single frame with priority routing and coverage gate.
        """
        self.frames += 1
        t_event = time.time()

        # Stage 1: event policy decides level
        decision = self.policy.decide(actions)
        level = decision["level"]

        # Stage 2: change detection (informational, not blocking)
        changed = self.detector.has_changed(image_path)

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

        # L1/L2: run OCR
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

        # ---- SECURITY-CRITICAL COVERAGE GATE ----
        # On L2 events (critical: USB/upload/email), if OCR confidence is low
        # OR no sensitive entity is detected, escalate to a full precise OCR
        # pass before making the DLP decision.
        coverage_gate_triggered = False
        if level == 2 and (
            ocr_status == "LOW_CONFIDENCE"
            or ocr_confidence < 0.85
            or len(self._quick_entities(text)) == 0
        ):
            try:
                from src.vision.easyocr_screen import cache_clear as _cc
                _cc()
            except Exception:
                pass

            precise = self.ocr.extract_text(image_path, use_cache=False)

            if precise["avg_confidence"] > ocr_confidence:
                result = precise
                text = precise["text"]
                ocr_confidence = precise["avg_confidence"]
                ocr_status = precise["status"]
                coverage_gate_triggered = True
                self.coverage_gate_hits += 1

        # Stage 3: behavior tracking + data flow + session risk
        entities_quick = self._quick_entities(text)

        for a in actions:
            self.tracker.record(a["action"], a["app"])
            self.flow.record(a["action"], a["app"], entities=entities_quick)
            self.session_risk.record_event(
                a["action"], a["app"], entities=entities_quick
            )

        behavior = self.tracker.assess_risk()
        flow_result = self.flow.analyze()
        session_summary = self.session_risk.summary()

        # Stage 4: risk scoring (combine per-event + session risk)
        risk = self.risk.calculate(entities_quick, behavior)

        # blend session risk into event risk
        blended_score = max(risk["score"], session_summary["session_risk_score"])
        if blended_score > risk["score"]:
            risk = dict(risk)
            risk["event_score"] = risk["score"]
            risk["session_score"] = session_summary["session_risk_score"]
            risk["score"] = blended_score
            risk["level"] = (
                "LOW" if blended_score <= 29
                else ("MEDIUM" if blended_score <= 69 else "HIGH")
            )

        # Stage 5: DLP decision
        intent = {
            "classification": "EXFILTRATION" if behavior["verdict"] in ["CRITICAL_RISK", "HIGH_RISK"] else "BENIGN",
            "confidence": 0.9,
        }
        dlp_result = self.dlp.evaluate(text, intent, behavior, risk)

        # fail-safe: low confidence + risky behavior
        if ocr_status == "LOW_CONFIDENCE" and behavior["verdict"] in ["CRITICAL_RISK", "HIGH_RISK"]:
            dlp_result["triggered"] = True
            if dlp_result.get("action") == "ALLOW":
                dlp_result["action"] = "WARN_AND_ALERT"

        total_ms = round((time.time() - t_event) * 1000, 3)

        return {
            "level": level,
            "skipped": False,
            "changed": changed,
            "ocr_status": ocr_status,
            "ocr_confidence": ocr_confidence,
            "cache_hit": result["cache_hit"],
            "coverage_gate_triggered": coverage_gate_triggered,
            "action": dlp_result["action"],
            "triggered": dlp_result["triggered"],
            "requires_user_confirmation": dlp_result.get("requires_user_confirmation", False),
            "flow": flow_result,
            "session_risk": session_summary,
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
        if re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", text):
            entities.append("AADHAAR")
        if re.search(r"\b\d{9,18}\b", text):
            entities.append("ACCOUNT_NUMBER")
        if any(w in text.lower() for w in ["salary", "compensation", "ctc", "payroll", "bonus"]):
            entities.append("EMPLOYEE_FINANCIAL_DATA")
        if any(w in text.lower() for w in ["confidential", "proprietary", "internal only", "trade secret"]):
            entities.append("CONFIDENTIAL_MARKING")
        return entities

    def stats(self):
        return {
            "frames": self.frames,
            "skipped": self.skipped,
            "ocr_calls": self.ocr_calls,
            "cache_hits": self.cache_hits,
            "l1_calls": self.l1_calls,
            "l2_calls": self.l2_calls,
            "coverage_gate_hits": self.coverage_gate_hits,
            "policy": self.policy.stats(),
        }

    def reset_session(self):
        """Reset data flow graph and session risk."""
        self.flow.reset()
        self.session_risk.reset()