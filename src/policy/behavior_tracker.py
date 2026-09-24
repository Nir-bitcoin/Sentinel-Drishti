# behavior_tracker.py

from datetime import datetime


# destination keyword lists
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
        # store one event
        event = {
            "time": datetime.now().isoformat(),
            "action": action,
            "app": app,
            "detail": detail,
        }
        self.events.append(event)
        return event

    def get_recent(self, count=10):
        return self.events[-count:]

    def classify_destination(self, app_name):
        # figure out destination category
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
        # look at last few events and decide verdict
        recent = self.get_recent(10)

        opened_sensitive = False
        copied_data = False
        paste_dest = None
        usb_detected = False
        after_hours = False

        for e in recent:
            app = e["app"].lower()
            action = e["action"]

            # was a sensitive file opened?
            if action == "OPEN":
                if any(x in app for x in ["excel", "hr", "sheet", "salary"]):
                    opened_sensitive = True

            # copy action
            if action == "COPY":
                copied_data = True

            # where did it get pasted?
            if action == "PASTE":
                paste_dest = self.classify_destination(e["app"])

            # USB check
            if "usb" in app or "external" in app:
                usb_detected = True

            # time check (before 9am or after 7pm = after hours)
            try:
                h = datetime.fromisoformat(e["time"]).hour
                if h < 9 or h > 19:
                    after_hours = True
            except Exception:
                pass

        # ---- verdict logic ----

        # USB copy = worst case
        if copied_data and usb_detected:
            return {
                "verdict": "CRITICAL_RISK",
                "reason": "Sensitive data copied to USB device",
                "destination": "EXTERNAL_DEVICE",
                "chain": ["sensitive_source", "copy", "usb"],
                "after_hours": after_hours,
            }

        # copy to personal email
        if copied_data and paste_dest == "PERSONAL_EMAIL":
            return {
                "verdict": "CRITICAL_RISK" if after_hours else "HIGH_RISK",
                "reason": "Sensitive data pasted to personal email",
                "destination": "PERSONAL_EMAIL",
                "chain": ["sensitive_source", "copy", "personal_email", "paste"],
                "after_hours": after_hours,
            }

        # copy to cloud
        if copied_data and paste_dest == "CLOUD_STORAGE":
            return {
                "verdict": "HIGH_RISK",
                "reason": "Sensitive data uploaded to cloud storage",
                "destination": "CLOUD_STORAGE",
                "chain": ["sensitive_source", "copy", "cloud", "paste"],
                "after_hours": after_hours,
            }

        # copy to messaging
        if copied_data and paste_dest == "MESSAGING":
            return {
                "verdict": "HIGH_RISK",
                "reason": "Sensitive data sent via messaging app",
                "destination": "MESSAGING",
                "chain": ["sensitive_source", "copy", "messaging", "paste"],
                "after_hours": after_hours,
            }

        # pasted to work email - allowed
        if copied_data and paste_dest == "WORK_EMAIL":
            return {
                "verdict": "LOW_RISK",
                "reason": "Data pasted into work email (audit only)",
                "destination": "WORK_EMAIL",
                "chain": ["sensitive_source", "copy", "work_email"],
                "after_hours": after_hours,
            }

        # only opened sensitive app
        if opened_sensitive:
            return {
                "verdict": "LOW_RISK",
                "reason": "Sensitive app opened, no exfiltration action yet",
                "destination": "LOCAL",
                "chain": ["sensitive_source"],
                "after_hours": after_hours,
            }

        return {
            "verdict": "NORMAL",
            "reason": "No suspicious pattern detected",
            "destination": "LOCAL",
            "chain": [],
            "after_hours": after_hours,
        }

    def reset(self):
        self.events = []