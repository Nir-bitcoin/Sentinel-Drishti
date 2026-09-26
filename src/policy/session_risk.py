# session_risk.py


from datetime import datetime


# action weights (added to session risk when action observed)
ACTION_WEIGHTS = {
    "OPEN": 0,
    "READ": 0,
    "TYPE": 0,
    "COPY": 20,
    "PASTE": 15,
    "DRAG": 15,
    "DROP": 15,
    "USB_INSERT": 45,
    "UPLOAD": 40,
    "EMAIL_OPEN": 15,
    "SAVE_AS": 20,
    "BROWSER_NAV": 10,
}

# entity weights (applied once when first detected in session)
ENTITY_WEIGHTS = {
    "PAN": 25,
    "PHONE": 15,
    "AADHAAR": 30,
    "ACCOUNT_NUMBER": 25,
    "EMPLOYEE_FINANCIAL_DATA": 20,
    "CONFIDENTIAL_MARKING": 10,
}

# destination weights (applied once when first seen)
DESTINATION_WEIGHTS = {
    "LOCAL": 0,
    "WORK_EMAIL": 5,
    "CLOUD_STORAGE": 30,
    "MESSAGING": 30,
    "PERSONAL_EMAIL": 40,
    "EXTERNAL_DEVICE": 45,
}


class SessionRisk:
    """
    Accumulates risk over the session.
    Tracks which entities and destinations have already been counted so
    the same signal is not double-counted.
    """

    def __init__(self, reset_minutes=30):
        self.session_start = datetime.now()
        self.reset_minutes = reset_minutes
        self._reset_state()

    def _reset_state(self):
        self.events = []
        self.seen_entities = set()
        self.seen_destinations = set()
        self.raw_score = 0

    def _maybe_reset(self):
        elapsed = (datetime.now() - self.session_start).total_seconds() / 60
        if elapsed > self.reset_minutes:
            self._reset_state()
            self.session_start = datetime.now()

    def record_event(self, action, app, entities=None, destination=None):
        """Record one event and accumulate risk."""
        self._maybe_reset()
        entities = entities or []

        delta = 0
        reasons = []

        # action weight
        w = ACTION_WEIGHTS.get(action, 0)
        if w > 0:
            self.raw_score += w
            delta += w
            reasons.append(action + " (+" + str(w) + ")")

        # entity weight (once per session per entity)
        for e in entities:
            if e not in self.seen_entities:
                ew = ENTITY_WEIGHTS.get(e, 0)
                if ew > 0:
                    self.raw_score += ew
                    delta += ew
                    reasons.append("entity " + e + " (+" + str(ew) + ")")
                self.seen_entities.add(e)

        # destination weight (once per session per destination)
        if destination and destination not in self.seen_destinations:
            dw = DESTINATION_WEIGHTS.get(destination, 0)
            if dw > 0:
                self.raw_score += dw
                delta += dw
                reasons.append("destination " + destination + " (+" + str(dw) + ")")
            self.seen_destinations.add(destination)

        self.events.append({
            "action": action,
            "app": app,
            "entities": entities,
            "destination": destination,
            "delta": delta,
            "raw_score_after": self.raw_score,
        })

        return delta

    def score(self):
        """Current session risk (capped at 100)."""
        return min(100, self.raw_score)

    def level(self):
        s = self.score()
        if s <= 29:
            return "LOW"
        if s <= 69:
            return "MEDIUM"
        return "HIGH"

    def summary(self):
        return {
            "session_risk_score": self.score(),
            "session_risk_level": self.level(),
            "raw_score": self.raw_score,
            "events_count": len(self.events),
            "entities_seen": sorted(list(self.seen_entities)),
            "destinations_seen": sorted(list(self.seen_destinations)),
            "events": self.events,
        }

    def reset(self):
        self._reset_state()
        self.session_start = datetime.now()


if __name__ == "__main__":
    print("=" * 55)
    print("  SESSION RISK TEST")
    print("=" * 55)
    print()

    sr = SessionRisk()
    sr.record_event("OPEN", "Excel")
    sr.record_event("COPY", "Excel", entities=["EMPLOYEE_FINANCIAL_DATA", "PAN"])
    sr.record_event("OPEN", "Gmail")
    sr.record_event("PASTE", "Gmail", destination="PERSONAL_EMAIL")

    print("Scenario: Excel -> Gmail")
    for e in sr.events:
        print("  " + e["action"].ljust(12) + " delta=+" +
              str(e["delta"]) + "  total=" + str(e["raw_score_after"]))
    print()
    print("  Final session risk: " + str(sr.score()) + "/100 (" + sr.level() + ")")
    print()