# data_flow.py

from datetime import datetime


# destination classification
DESTINATIONS = {
    "gmail": "PERSONAL_EMAIL",
    "yahoo mail": "PERSONAL_EMAIL",
    "outlook personal": "PERSONAL_EMAIL",
    "outlook": "WORK_EMAIL",
    "outlook exchange": "WORK_EMAIL",
    "teams": "WORK_EMAIL",
    "slack": "WORK_EMAIL",
    "google drive": "CLOUD_STORAGE",
    "dropbox": "CLOUD_STORAGE",
    "onedrive": "CLOUD_STORAGE",
    "whatsapp": "MESSAGING",
    "telegram": "MESSAGING",
    "signal": "MESSAGING",
    "usb drive": "EXTERNAL_DEVICE",
    "usb": "EXTERNAL_DEVICE",
    "external drive": "EXTERNAL_DEVICE",
    "excel": "LOCAL",
    "word": "LOCAL",
    "notepad": "LOCAL",
    "pdf": "LOCAL",
}

# destination risk tier
DEST_RISK = {
    "LOCAL": "NORMAL",
    "WORK_EMAIL": "LOW",
    "CLOUD_STORAGE": "HIGH",
    "MESSAGING": "HIGH",
    "PERSONAL_EMAIL": "CRITICAL",
    "EXTERNAL_DEVICE": "CRITICAL",
}

# transfer mechanisms
TRANSFER_MAP = {
    "COPY": "CLIPBOARD",
    "PASTE": "CLIPBOARD",
    "DRAG": "CLIPBOARD",
    "DROP": "CLIPBOARD",
    "USB_INSERT": "REMOVABLE_MEDIA",
    "UPLOAD": "NETWORK",
    "SAVE_AS": "FILESYSTEM",
}


def classify_app(app_name):
    if not app_name:
        return "LOCAL"
    key = app_name.lower().strip()
    for k, v in DESTINATIONS.items():
        if k in key:
            return v
    return "LOCAL"


class DataFlowNode:
    def __init__(self, app, data_class=None, ts=None):
        self.app = app
        self.data_class = data_class or []
        self.ts = ts or datetime.now().isoformat()

    def to_dict(self):
        return {
            "app": self.app,
            "data_class": self.data_class,
            "ts": self.ts,
        }


class DataFlowEdge:
    def __init__(self, source, transfer, destination, ts=None):
        self.source = source
        self.transfer = transfer
        self.destination = destination
        self.ts = ts or datetime.now().isoformat()

    def to_dict(self):
        return {
            "source": self.source,
            "transfer": self.transfer,
            "destination": self.destination,
            "ts": self.ts,
        }


class DataFlowGraph:
    """
    Tracks data movement within a session.

    Usage:
        flow = DataFlowGraph()
        flow.record("OPEN", "Excel", entities=["EMPLOYEE_FINANCIAL_DATA"])
        flow.record("COPY", "Excel")
        flow.record("OPEN", "Gmail")
        flow.record("PASTE", "Gmail")
        result = flow.analyze()
    """

    def __init__(self, session_reset_minutes=30):
        self.nodes = []
        self.edges = []
        self.current_source = None
        self.clipboard_data_class = []
        self.clipboard_source_app = None
        self.session_start = datetime.now()
        self.session_reset_minutes = session_reset_minutes

    def _maybe_reset(self):
        elapsed = (datetime.now() - self.session_start).total_seconds() / 60
        if elapsed > self.session_reset_minutes:
            self.reset()

    def reset(self):
        self.nodes = []
        self.edges = []
        self.current_source = None
        self.clipboard_data_class = []
        self.clipboard_source_app = None
        self.session_start = datetime.now()

    def record(self, action, app, entities=None):
        """Record one event into the flow graph."""
        self._maybe_reset()
        entities = entities or []

        dest_class = classify_app(app)

        if action == "OPEN":
            self.nodes.append(DataFlowNode(app, entities))
            if dest_class == "LOCAL":
                self.current_source = app

        elif action == "COPY":
            # capture data going into clipboard
            self.clipboard_data_class = list(entities)
            self.clipboard_source_app = app
            self.edges.append(DataFlowEdge(
                source=app,
                transfer="CLIPBOARD_WRITE",
                destination="CLIPBOARD",
            ))

        elif action == "PASTE":
            self.edges.append(DataFlowEdge(
                source=self.clipboard_source_app or app,
                transfer="CLIPBOARD_READ",
                destination=app,
            ))

        elif action == "USB_INSERT":
            self.edges.append(DataFlowEdge(
                source="DEVICE",
                transfer="REMOVABLE_MEDIA",
                destination=app,
            ))

        elif action == "UPLOAD":
            self.edges.append(DataFlowEdge(
                source=app,
                transfer="NETWORK",
                destination=dest_class,
            ))

    def analyze(self):
        """Analyze the flow graph for exfiltration patterns."""
        if not self.edges:
            return {
                "flow_detected": False,
                "source": None,
                "data_class": [],
                "transfer": None,
                "destination": None,
                "destination_tier": "NORMAL",
                "verdict": "NO_FLOW",
            }

        # find the last meaningful edge (non-clipboard destination)
        meaningful = [e for e in self.edges if e.destination not in ("CLIPBOARD", "DEVICE")]

        if not meaningful:
            return {
                "flow_detected": False,
                "source": self.clipboard_source_app,
                "data_class": self.clipboard_data_class,
                "transfer": None,
                "destination": None,
                "destination_tier": "NORMAL",
                "verdict": "CLIPBOARD_ONLY",
            }

        last_edge = meaningful[-1]
        dest_class = classify_app(last_edge.destination)
        dest_tier = DEST_RISK.get(dest_class, "NORMAL")

        # overall verdict
        if dest_tier == "CRITICAL":
            verdict = "EXFILTRATION"
        elif dest_tier == "HIGH":
            verdict = "SUSPICIOUS_TRANSFER"
        else:
            verdict = "INTERNAL"

        return {
            "flow_detected": True,
            "source": self.clipboard_source_app or last_edge.source,
            "data_class": self.clipboard_data_class,
            "transfer": last_edge.transfer,
            "destination": last_edge.destination,
            "destination_class": dest_class,
            "destination_tier": dest_tier,
            "verdict": verdict,
            "edges": [e.to_dict() for e in self.edges],
            "nodes": [n.to_dict() for n in self.nodes],
        }

    def render(self):
        """Human-readable flow rendering for demo."""
        r = self.analyze()
        if not r["flow_detected"]:
            return "  (no data flow detected)"

        lines = []
        lines.append("  Source:      " + str(r["source"]))
        if r["data_class"]:
            lines.append("  Data class:  " + ", ".join(r["data_class"]))
        else:
            lines.append("  Data class:  (unknown)")
        if r["transfer"]:
            lines.append("  Transfer:    " + r["transfer"])
        lines.append("  Destination: " + str(r["destination"]) +
                     " [" + r.get("destination_class", "?") + "]")
        lines.append("  Verdict:     " + r["verdict"])
        return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 55)
    print("  DATA FLOW GRAPH TEST")
    print("=" * 55)
    print()

    # test 1: exfiltration
    flow = DataFlowGraph()
    flow.record("OPEN", "Excel", entities=["EMPLOYEE_FINANCIAL_DATA"])
    flow.record("COPY", "Excel", entities=["EMPLOYEE_FINANCIAL_DATA", "PAN"])
    flow.record("OPEN", "Gmail")
    flow.record("PASTE", "Gmail")
    print("Test 1: Excel -> Gmail")
    print(flow.render())
    print()

    # test 2: USB exfiltration
    flow2 = DataFlowGraph()
    flow2.record("OPEN", "Excel", entities=["EMPLOYEE_FINANCIAL_DATA"])
    flow2.record("COPY", "Excel", entities=["PAN"])
    flow2.record("USB_INSERT", "USB Drive")
    flow2.record("PASTE", "USB Drive")
    print("Test 2: Excel -> USB")
    print(flow2.render())
    print()

    # test 3: benign
    flow3 = DataFlowGraph()
    flow3.record("OPEN", "Notepad")
    flow3.record("TYPE", "Notepad")
    print("Test 3: Notepad typing")
    print(flow3.render())
    print()