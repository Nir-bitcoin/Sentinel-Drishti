# policy_loader.py


import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


_DEFAULT = {
    "risk_weights": {
        "pii_detected": 40, "financial_data": 35, "confidential_marking": 20,
        "copy_event": 20, "paste_event": 15, "usb_insert": 45,
        "personal_email": 40, "cloud_storage": 35, "messaging_app": 35,
        "external_device": 45, "outside_hours": 10, "after_hours_access": 10,
    },
    "thresholds": {"allow_max": 29, "warn_max": 69, "block_min": 70},
    "severity_actions": {
        "HIGH": "BLOCK_AND_ALERT", "MEDIUM": "WARN_AND_ALERT", "LOW": "ALERT_ONLY",
    },
    "destinations": {
        "LOCAL": "NORMAL", "PERSONAL_EMAIL": "CRITICAL",
        "EXTERNAL_DEVICE": "CRITICAL", "CLOUD_STORAGE": "HIGH",
        "MESSAGING": "HIGH", "WORK_EMAIL": "LOW",
    },
}


class Policy:
    def __init__(self, path="config/policy.yaml"):
        self.path = path
        self.data = {k: (dict(v) if isinstance(v, dict) else v) for k, v in _DEFAULT.items()}
        self._load()

    def _load(self):
        if not HAS_YAML:
            return
        p = Path(self.path)
        if not p.exists():
            return
        try:
            with open(p, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f)
            if loaded:
                for k, v in loaded.items():
                    if isinstance(v, dict):
                        self.data.setdefault(k, {}).update(v)
                    else:
                        self.data[k] = v
        except Exception:
            pass

    def weight(self, key, default=0):
        return self.data["risk_weights"].get(key, default)

    def threshold(self, key, default=0):
        return self.data["thresholds"].get(key, default)

    def action_for_severity(self, sev):
        return self.data["severity_actions"].get(sev, "ALERT_ONLY")

    def dest_risk(self, dest):
        return self.data["destinations"].get(dest, "NORMAL")

    def classify_risk(self, score):
        if score <= self.threshold("allow_max", 29):
            return "LOW"
        if score <= self.threshold("warn_max", 69):
            return "MEDIUM"
        return "HIGH"


if __name__ == "__main__":
    p = Policy()
    print("Policy loaded from: " + p.path)
    print("  pii_detected weight: " + str(p.weight("pii_detected")))
    print("  usb_insert weight:  " + str(p.weight("usb_insert")))
    print("  block threshold:    " + str(p.threshold("block_min")))
    print("  score 45 -> " + p.classify_risk(45))
    print("  score 85 -> " + p.classify_risk(85))