# dlp_engine.py

import re
import hashlib
import json
from datetime import datetime
from pathlib import Path

try:
    from src.policy.audit_chain import AuditChain
    HAS_CHAIN = True
except Exception:
    HAS_CHAIN = False


class DLPEngine:

    def __init__(self):
        self.rules = [
            {
                "id": "PII_001",
                "desc": "Personal identifiable information",
                "regex": [
                    r"\b\d{4}\s\d{4}\s\d{4}\b",
                    r"\b[A-Z]{5}\d{4}[A-Z]\b",
                    r"\b[6-9]\d{9}\b",
                ],
                "severity": "HIGH",
                "action": "BLOCK_AND_ALERT"
            },
            {
                "id": "FIN_001",
                "desc": "Employee financial data",
                "regex": [
                    r"\b(?:salary|compensation|ctc|payroll|bonus)\b",
                    r"\b\d{9,18}\b",
                ],
                "severity": "HIGH",
                "action": "BLOCK_AND_ALERT"
            },
            {
                "id": "CONF_001",
                "desc": "Confidential markings",
                "regex": [
                    r"\b(?:confidential|proprietary|internal\s+only|trade\s+secret)\b"
                ],
                "severity": "MEDIUM",
                "action": "ALERT_ONLY"
            }
        ]

        self.log_dir = Path("audit_logs")
        if not self.log_dir.exists():
            self.log_dir.mkdir()

        if HAS_CHAIN:
            self.chain = AuditChain(str(self.log_dir))
        else:
            self.chain = None

    def evaluate(self, text, intent, behavior, risk):
        hits = []
        for rule in self.rules:
            for rx in rule["regex"]:
                if re.search(rx, text, re.IGNORECASE):
                    hits.append({
                        "rule_id": rule["id"],
                        "description": rule["desc"],
                        "severity": rule["severity"],
                        "action": rule["action"]
                    })
                    break

        risky = behavior.get("verdict") in ["CRITICAL_RISK", "HIGH_RISK"]
        sensitive = len(hits) > 0

        if not (risky and sensitive):
            exp = self._why(hits, behavior, risk, False)
            return {
                "triggered": False,
                "matches": hits,
                "severity": "NONE",
                "action": "ALLOW",
                "explanation": exp,
                "risk_score": risk["score"],
                "risk_level": risk["level"],
                "enforcement": None,
            }

        order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        top = hits[0]
        for m in hits:
            if order.get(m["severity"], 0) > order.get(top["severity"], 0):
                top = m

        exp = self._why(hits, behavior, risk, True)
        enf = self._block(behavior)

        res = {
            "triggered": True,
            "matches": hits,
            "severity": top["severity"],
            "action": top["action"],
            "intent_classification": intent.get("classification", "?"),
            "intent_confidence": intent.get("confidence", 0),
            "explanation": exp,
            "risk_score": risk["score"],
            "risk_level": risk["level"],
            "enforcement": enf,
        }

        self._log(res, text[:200])
        return res

    def _block(self, behavior):
        d = behavior.get("destination", "LOCAL")

        if d == "PERSONAL_EMAIL":
            return {
                "blocked_action": "PASTE to personal email",
                "status": "BLOCKED",
                "message": "Data exfiltration PREVENTED",
                "mode": "SIMULATED",
            }
        elif d == "EXTERNAL_DEVICE":
            return {
                "blocked_action": "USB file transfer",
                "status": "BLOCKED",
                "message": "Removable device write PREVENTED",
                "mode": "SIMULATED",
            }
        elif d == "CLOUD_STORAGE":
            return {
                "blocked_action": "Cloud upload",
                "status": "BLOCKED",
                "message": "Upload PREVENTED",
                "mode": "SIMULATED",
            }
        elif d == "MESSAGING":
            return {
                "blocked_action": "Message send",
                "status": "BLOCKED",
                "message": "Message send PREVENTED",
                "mode": "SIMULATED",
            }
        else:
            return {
                "blocked_action": "Unknown action",
                "status": "BLOCKED",
                "message": "Action PREVENTED",
                "mode": "SIMULATED",
            }

    def _why(self, hits, behavior, risk, blocked):
        lines = []

        if len(hits) > 0:
            ids = [h["rule_id"] for h in hits]
            lines.append("Rules matched: " + ", ".join(ids))
        else:
            lines.append("No policy rules matched")

        lines.append("Behavior verdict: " + behavior.get("verdict", "?"))

        d = behavior.get("destination", "LOCAL")
        if d != "LOCAL":
            lines.append("Destination: " + d)

        if behavior.get("after_hours"):
            lines.append("Access outside business hours")

        lines.append("Risk score: " + str(risk["score"]) + "/100 (" + risk["level"] + ")")

        if blocked:
            lines.append("Decision: BLOCK + ALERT")
        else:
            if not behavior.get("verdict") in ["CRITICAL_RISK", "HIGH_RISK"]:
                lines.append("Decision: ALLOW (behavior not risky)")
            else:
                lines.append("Decision: ALLOW (no rule matched)")

        return lines

    def _log(self, res, snippet):
        event = {
            "severity": res["severity"],
            "action": res["action"],
            "matches": [m["rule_id"] for m in res["matches"]],
            "risk_score": res["risk_score"],
            "snippet": snippet,
        }

        if self.chain is not None:
            self.chain.append(event)
        else:
            entry = {"ts": datetime.now().isoformat()}
            entry.update(event)
            s = json.dumps(entry, sort_keys=True)
            entry["hash"] = hashlib.sha256(s.encode()).hexdigest()[:16]
            fname = "dlp_" + datetime.now().strftime("%Y%m%d") + ".jsonl"
            with open(self.log_dir / fname, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")