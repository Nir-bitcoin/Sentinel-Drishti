# event_policy.py
#

TRIGGER_ACTIONS = [
    "COPY", "PASTE", "DRAG", "DROP",
    "SAVE_AS", "UPLOAD", "USB_INSERT",
    "EMAIL_OPEN", "BROWSER_NAV",
]

CRITICAL_ACTIONS = ["UPLOAD", "USB_INSERT"]
SUSPICIOUS_ACTIONS = ["COPY", "PASTE", "EMAIL_OPEN", "SAVE_AS"]


class EventPolicy:

    def __init__(self):
        self.level0_count = 0
        self.level1_count = 0
        self.level2_count = 0

    def decide(self, recent_actions):
        if not recent_actions:
            self.level0_count += 1
            return {"level": 0, "reason": "no recent activity", "trigger": None}

        triggers = []
        for a in recent_actions:
            if a.get("action") in TRIGGER_ACTIONS:
                triggers.append(a["action"])

        if not triggers:
            self.level0_count += 1
            return {"level": 0, "reason": "no OCR-triggering action", "trigger": None}

        has_critical = any(t in CRITICAL_ACTIONS for t in triggers)
        has_suspicious = any(t in SUSPICIOUS_ACTIONS for t in triggers)

        if has_critical:
            self.level2_count += 1
            return {"level": 2, "reason": "critical transfer event", "trigger": triggers}
        elif has_suspicious:
            self.level1_count += 1
            return {"level": 1, "reason": "suspicious transfer event", "trigger": triggers}
        else:
            self.level1_count += 1
            return {"level": 1, "reason": "activity triggered OCR", "trigger": triggers}

    def stats(self):
        return {
            "level0": self.level0_count,
            "level1": self.level1_count,
            "level2": self.level2_count,
        }


if __name__ == "__main__":
    p = EventPolicy()

    print("No activity:", p.decide([]))
    print()
    print("Normal typing:", p.decide([
        {"action": "OPEN", "app": "Notepad"},
        {"action": "TYPE", "app": "Notepad"},
    ]))
    print()
    print("Suspicious:", p.decide([
        {"action": "COPY", "app": "Excel"},
        {"action": "OPEN", "app": "Gmail"},
        {"action": "PASTE", "app": "Gmail"},
    ]))
    print()
    print("Critical:", p.decide([
        {"action": "COPY", "app": "Excel"},
        {"action": "USB_INSERT", "app": "USB Drive"},
    ]))
    print()
    print("Stats:", p.stats())