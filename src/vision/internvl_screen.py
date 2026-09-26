# internvl_screen.py


import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.backend.base import get_backend


class InternVLScreenAnalyzer:

    def __init__(self, mode="snapdragon"):
        self.backend = get_backend(mode)

        # PII patterns - strictly typed
        # ACCOUNT_NUMBER: 11+ digits (phone is 10, exclude)
        self.pii_rx = [
            (r"\b\d{4}\s\d{4}\s\d{4}\b", "AADHAAR"),
            (r"\b[A-Z]{5}\d{4}[A-Z]\b", "PAN"),
            (r"\b[6-9]\d{9}\b", "PHONE"),                    # Indian mobile: 10 digits starting 6-9
            (r"\b\d{11,18}\b", "ACCOUNT_NUMBER"),            # bank account: 11-18 digits
        ]

        self.money_words = ["salary", "compensation", "ctc", "payroll", "bonus"]
        self.ip_words = ["confidential", "proprietary", "internal only", "trade secret"]

    def analyze(self, text):
        inf = self.backend.infer("vision", {"text": text})

        found = []
        lower = text.lower()

        for rx, name in self.pii_rx:
            if re.search(rx, text):
                found.append(name)

        for w in self.money_words:
            if w in lower:
                found.append("EMPLOYEE_FINANCIAL_DATA")
                break

        for w in self.ip_words:
            if w in lower:
                found.append("CONFIDENTIAL_MARKING")
                break

        found = list(set(found))

        return {
            "sensitive": len(found) > 0,
            "entities": sorted(found),
            "latency_ms": inf["latency_ms"],
            "compute_unit": inf["compute_unit"],
            "timing_source": inf["timing_source"],
            "precision": inf.get("precision", "unknown"),
            "ram_peak_mb": inf.get("ram_peak_mb", "?"),
            "layers_on_npu": inf.get("layers_on_npu", "?"),
            "runtime": inf.get("runtime", "?"),
        }