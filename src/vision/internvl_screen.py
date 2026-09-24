# internvl_screen.py

import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.backend.base import get_backend


class InternVLScreenAnalyzer:

    def __init__(self, mode="snapdragon"):
        # mode: "snapdragon" or "cpu"
        self.backend = get_backend(mode)

        # aadhaar mein space chahiye warna 12 digit account number bhi match
        self.pii_rx = [
            (r"\b\d{4}\s\d{4}\s\d{4}\b", "AADHAAR"),
            (r"\b[A-Z]{5}\d{4}[A-Z]\b", "PAN"),
            (r"\b[6-9]\d{9}\b", "PHONE"),
            (r"\b\d{9,18}\b", "ACCOUNT_NUMBER"),
        ]
        self.money_words = ["salary", "compensation", "ctc", "payroll", "bonus"]
        self.ip_words = ["confidential", "proprietary", "internal only", "trade secret"]

    def analyze(self, text):
        # inference through backend (CPU or NPU)
        inf = self.backend.infer("vision", {"text": text})

        # ---- real entity detection (runs on real input) ----
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
        }