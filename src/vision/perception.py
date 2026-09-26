# perception.py

import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.backend.base import get_backend


class TextPerception:
    """Detects sensitive entities in text using regex patterns."""

    def __init__(self, mode="snapdragon"):
        self.backend = get_backend(mode)

        # PII patterns
        self.pii_rx = [
            (r"\b\d{4}\s\d{4}\s\d{4}\b", "AADHAAR"),
            (r"\b[A-Z]{5}\d{4}[A-Z]\b", "PAN"),
            (r"\b[6-9]\d{9}\b", "PHONE"),
            (r"\b\d{11,18}\b", "ACCOUNT_NUMBER"),
        ]

        self.financial_words = [
            "salary", "compensation", "ctc", "payroll", "bonus"
        ]

        self.confidential_words = [
            "confidential", "proprietary", "internal only", "trade secret"
        ]

    def analyze(self, text):
        """Detect sensitive entities in text."""
        inf = self.backend.infer("vision", {"text": text})

        found = []
        lower = text.lower()

        for rx, name in self.pii_rx:
            if re.search(rx, text):
                found.append(name)

        for w in self.financial_words:
            if w in lower:
                found.append("EMPLOYEE_FINANCIAL_DATA")
                break

        for w in self.confidential_words:
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


# backwards compat alias - remove later
InternVLScreenAnalyzer = TextPerception


if __name__ == "__main__":
    a = TextPerception("cpu")
    r = a.analyze("Employee salary record PAN ABCDE1234F Phone 9876543210")
    print("Sensitive:", r["sensitive"])
    print("Entities:", r["entities"])