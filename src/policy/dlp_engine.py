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

try:
    from src.security.masking import summarize_entities, mask_all
    HAS_MASKING = True
except Exception:
    HAS_MASKING = False


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
        dest = behavior.get("destination", "LOCAL")
        risk_score = risk.get("score", 0)

        # ---------- Decision matrix ----------
        # LOW: no sensitive OR no risky behavior
        # WARN: sensitive + suspicious destination but not full exfiltration
        # BLOCK: sensitive + risky behavior + external destination

        critical_dests = ("PERSONAL_EMAIL", "EXTERNAL_DEVICE")
        warn_dests = ("CLOUD_STORAGE", "MESSAGING")

        if not sensitive or not risky:
            # ALLOW path
            if sensitive and risk_score >= 40:
                # sensitive data present and moderate risk -> WARN
                decision = "WARN_AND_ALERT"
                action = "WARN_AND_ALERT"
                triggered = True
            else:
                decision = "ALLOW"
                action = "ALLOW"
                triggered = False
        else:
            # risky + sensitive
            if dest in critical_dests:
                decision = "BLOCK_AND_ALERT"
                action = "BLOCK_AND_ALERT"
                triggered = True
            elif dest in warn_dests:
                decision = "WARN_AND_ALERT"
                action = "WARN_AND_ALERT"
                triggered = True
            else:
                # risky but local -> WARN
                decision = "WARN_AND_ALERT"
                action = "WARN_AND_ALERT"
                triggered = True

        # pick top severity hit
        order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        top = hits[0] if hits else {"severity": "NONE", "action": "ALLOW"}

        # explanation
        exp = self._why(hits, behavior, risk, action)

        # enforcement (only for BLOCK)
        enf = None
        if action == "BLOCK_AND_ALERT":
            enf = self._block(behavior)
        elif action == "WARN_AND_ALERT":
            enf = self._warn(behavior)

        res = {
            "triggered": triggered,
            "matches": hits,
            "severity": top["severity"],
            "action": action,
            "decision": decision,
            "intent_classification": intent.get("classification", "?"),
            "intent_confidence": intent.get("confidence", 0),
            "explanation": exp,
            "risk_score": risk_score,
            "risk_level": risk.get("level", "LOW"),
            "enforcement": enf,
            "requires_user_confirmation": action == "WARN_AND_ALERT",
        }

        self._log(res, text[:200])
        return res

    def _block(self, behavior):
        d = behavior.get("destination", "LOCAL")
        messages = {
            "PERSONAL_EMAIL": ("PASTE to personal email", "Data exfiltration PREVENTED"),
            "EXTERNAL_DEVICE": ("USB file transfer", "Removable device write PREVENTED"),
            "CLOUD_STORAGE": ("Cloud upload", "Upload PREVENTED"),
            "MESSAGING": ("Message send", "Message send PREVENTED"),
        }
        act, msg = messages.get(d, ("Unknown action", "Action PREVENTED"))
        return {
            "blocked_action": act,
            "status": "BLOCKED",
            "message": msg,
            "mode": "SIMULATED",
            "requires_user_confirmation": False,
        }

    def _warn(self, behavior):
        d = behavior.get("destination", "LOCAL")
        return {
            "warned_action": "Transfer to " + str(d),
            "status": "WARNED",
            "message": "Confirm to proceed (policy risk flag)",
            "mode": "USER_CONFIRMATION",
            "requires_user_confirmation": True,
            "options": ["Allow once", "Cancel transfer"],
        }

    def _why(self, hits, behavior, risk, action):
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

        if action == "BLOCK_AND_ALERT":
            lines.append("Evidence Level: HIGH")
            lines.append("Policy Decision: BLOCK_AND_ALERT")
        elif action == "WARN_AND_ALERT":
            lines.append("Evidence Level: MEDIUM")
            lines.append("Policy Decision: WARN_AND_ALERT")
        else:
            lines.append("Evidence Level: LOW")
            lines.append("Policy Decision: ALLOW")

        return lines

    def _log(self, res, snippet):
        snippet_hash = hashlib.sha256(snippet.encode()).hexdigest()[:16]

        # privacy-preserving: per-entity masked summary
        masked_entities = []
        if HAS_MASKING:
            try:
                entity_names = [m["rule_id"] for m in res["matches"]]
                friendly = []
                if "PII_001" in entity_names:
                    friendly.append("PAN")
                    friendly.append("PHONE")
                if "FIN_001" in entity_names:
                    friendly.append("EMPLOYEE_FINANCIAL_DATA")
                if "CONF_001" in entity_names:
                    friendly.append("CONFIDENTIAL_MARKING")
                masked_entities = summarize_entities(friendly, snippet)
            except Exception:
                masked_entities = []

        event = {
            "severity": res["severity"],
            "action": res["action"],
            "decision": res["decision"],
            "matches": [m["rule_id"] for m in res["matches"]],
            "risk_score": res["risk_score"],
            "content_hash": snippet_hash,
            "content_redacted": True,
            "masked_entities": masked_entities,
            "raw_content_stored": False,
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