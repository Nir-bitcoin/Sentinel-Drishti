# risk score 0-100. 

class RiskScorer:

    def calculate(self, entities, behavior):
        pts = 0
        why = []

        # ---- content ----
        n_pii = 0
        fin = False
        conf = False

        for e in entities:
            if e in ["PAN", "PHONE", "AADHAAR", "ACCOUNT_NUMBER"]:
                n_pii += 1
            elif e == "EMPLOYEE_FINANCIAL_DATA":
                fin = True
            elif e == "CONFIDENTIAL_MARKING":
                conf = True

        if n_pii >= 2:
            pts += 30
            why.append("Multiple PII entities detected (+30)")
        elif n_pii == 1:
            pts += 15
            why.append("PII entity detected (+15)")

        if fin:
            pts += 20
            why.append("Employee financial data (+20)")

        if conf:
            pts += 10
            why.append("Confidential marking (+10)")

        # ---- behavior ----
        v = behavior.get("verdict", "NORMAL")

        if v == "CRITICAL_RISK":
            pts += 40
            why.append("Critical behavior pattern (+40)")
        elif v == "HIGH_RISK":
            pts += 30
            why.append("High risk behavior pattern (+30)")
        elif v == "MEDIUM_RISK":
            pts += 20
            why.append("Medium risk behavior pattern (+20)")
        elif v == "LOW_RISK":
            pts += 5
            why.append("Sensitive app opened (+5)")

        # ---- destination ----
        d = behavior.get("destination", "LOCAL")

        if d == "EXTERNAL_DEVICE":
            pts += 20
            why.append("Destination: external device (+20)")
        elif d == "PERSONAL_EMAIL":
            pts += 15
            why.append("Destination: personal email (+15)")
        elif d == "CLOUD_STORAGE":
            pts += 12
            why.append("Destination: cloud storage (+12)")
        elif d == "MESSAGING":
            pts += 12
            why.append("Destination: messaging app (+12)")
        elif d == "WORK_EMAIL":
            pts += 3
            why.append("Destination: work email (+3)")

        # ---- time ----
        if behavior.get("after_hours", False):
            pts += 10
            why.append("Outside business hours (+10)")

        raw = pts
        final = min(raw, 100)

        if raw > 100:
            why.append("Capped at 100 (raw was " + str(raw) + ")")

        return {
            "score": final,
            "raw_score": raw,
            "reasons": why,
            "level": self._lvl(final),
        }

    def _lvl(self, s):
        if s >= 80:
            return "CRITICAL"
        elif s >= 60:
            return "HIGH"
        elif s >= 30:
            return "MEDIUM"
        elif s > 0:
            return "LOW"
        return "NONE"