# behavior_tracker.py

from datetime import datetime


PERSONAL_EMAIL = ["gmail", "yahoo", "outlook.com", "hotmail"]
WORK_EMAIL = ["exchange", "company", "corp"]
MESSAGING = ["whatsapp", "telegram", "slack", "teams", "signal", "discord"]
CLOUD_STORAGE = ["drive", "dropbox", "onedrive", "box", "mega"]
EXTERNAL_DEVICE = ["usb", "external", "removable", "pendrive"]


class BehaviorTracker:

    def __init__(self, user_id="default"):
        self.user_id = user_id
        self.events = []

    def record(self, action, app, detail=""):
        ev = {
            "time": datetime.now().isoformat(),
            "action": action,
            "app": app,
            "detail": detail,
        }
        self.events.append(ev)
        return ev

    def get_recent(self, n=10):
        return self.events[-n:]

    def classify_destination(self, app_name):
        a = app_name.lower()

        if any(x in a for x in EXTERNAL_DEVICE):
            return "EXTERNAL_DEVICE"
        if any(x in a for x in PERSONAL_EMAIL):
            return "PERSONAL_EMAIL"
        if any(x in a for x in WORK_EMAIL):
            return "WORK_EMAIL"
        if any(x in a for x in MESSAGING):
            return "MESSAGING"
        if any(x in a for x in CLOUD_STORAGE):
            return "CLOUD_STORAGE"
        return "LOCAL"

    def assess_risk(self):
        recent = self.get_recent(10)

        opened_sensitive = False
        copied = False
        paste_dest = None
        usb_seen = False
        after_hrs = False

        for e in recent:
            app = e["app"].lower()
            action = e["action"]

            if action == "OPEN":
                if any(x in app for x in ["excel", "hr", "sheet", "salary"]):
                    opened_sensitive = True

            if action == "COPY":
                copied = True

            if action == "PASTE":
                paste_dest = self.classify_destination(e["app"])

            if "usb" in app or "external" in app:
                usb_seen = True

            try:
                h = datetime.fromisoformat(e["time"]).hour
                if h < 9 or h > 19:
                    after_hrs = True
            except Exception:
                pass

        # USB copy = worst
        if copied and usb_seen:
            return {
                "verdict": "CRITICAL_RISK",
                "reason": "Sensitive data copied to USB device",
                "destination": "EXTERNAL_DEVICE",
                "chain": ["sensitive_source", "copy", "usb"],
                "after_hours": after_hrs,
            }

        # personal email = CRITICAL (not HIGH)
        if copied and paste_dest == "PERSONAL_EMAIL":
            return {
                "verdict": "CRITICAL_RISK",
                "reason": "Sensitive data pasted to personal email",
                "destination": "PERSONAL_EMAIL",
                "chain": ["sensitive_source", "copy", "personal_email", "paste"],
                "after_hours": after_hrs,
            }

        if copied and paste_dest == "CLOUD_STORAGE":
            return {
                "verdict": "HIGH_RISK",
                "reason": "Sensitive data uploaded to cloud storage",
                "destination": "CLOUD_STORAGE",
                "chain": ["sensitive_source", "copy", "cloud", "paste"],
                "after_hours": after_hrs,
            }

        if copied and paste_dest == "MESSAGING":
            return {
                "verdict": "HIGH_RISK",
                "reason": "Sensitive data sent via messaging app",
                "destination": "MESSAGING",
                "chain": ["sensitive_source", "copy", "messaging", "paste"],
                "after_hours": after_hrs,
            }

        if copied and paste_dest == "WORK_EMAIL":
            return {
                "verdict": "LOW_RISK",
                "reason": "Data pasted into work email (audit only)",
                "destination": "WORK_EMAIL",
                "chain": ["sensitive_source", "copy", "work_email"],
                "after_hours": after_hrs,
            }

        if opened_sensitive:
            return {
                "verdict": "LOW_RISK",
                "reason": "Sensitive app opened, no exfiltration action yet",
                "destination": "LOCAL",
                "chain": ["sensitive_source"],
                "after_hours": after_hrs,
            }

        return {
            "verdict": "NORMAL",
            "reason": "No suspicious pattern detected",
            "destination": "LOCAL",
            "chain": [],
            "after_hours": after_hrs,
        }

    def reset(self):
        self.events = []