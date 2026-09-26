# intent_classifier.py
#
# Rule-based intent classification.
# Currently uses entity-based rules (not an LLM).
#
# Note: earlier this was called QwenIntentClassifier, but actual code
# is rule-based. Renamed for honesty.


import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.backend.base import get_backend


class RuleBasedIntentClassifier:
    """Classifies user intent based on detected entities."""

    def __init__(self, mode="snapdragon"):
        self.backend = get_backend(mode)

    def classify(self, text, entities):
        inf = self.backend.infer("reasoning", {"text": text, "entities": entities})

        if not text or not text.strip():
            return {
                "classification": "UNVERIFIED_DATA_TRANSFER",
                "confidence": 0.90,
                "latency_ms": inf["latency_ms"],
                "compute_unit": inf["compute_unit"],
                "timing_source": inf["timing_source"],
                "precision": inf.get("precision", "unknown"),
                "ram_peak_mb": inf.get("ram_peak_mb", "?"),
                "layers_on_npu": inf.get("layers_on_npu", "?"),
                "runtime": inf.get("runtime", "?"),
            }

        n_pii = 0
        n_fin = 0
        n_conf = 0

        for e in entities:
            if e in ["PAN", "PHONE", "AADHAAR", "ACCOUNT_NUMBER"]:
                n_pii += 1
            elif e == "EMPLOYEE_FINANCIAL_DATA":
                n_fin += 1
            elif e == "CONFIDENTIAL_MARKING":
                n_conf += 1

        if n_pii >= 2 and n_fin >= 1:
            label = "EXFILTRATION"
            conf = 0.97
        elif n_pii >= 1 and n_fin >= 1:
            label = "EXFILTRATION"
            conf = 0.94
        elif n_pii >= 1:
            label = "EXFILTRATION"
            conf = 0.87
        elif n_fin >= 1:
            label = "EXFILTRATION"
            conf = 0.85
        elif n_conf >= 1:
            label = "CONFIDENTIAL_DATA_ACCESS"
            conf = 0.82
        else:
            label = "BENIGN"
            conf = 0.95

        return {
            "classification": label,
            "confidence": conf,
            "latency_ms": inf["latency_ms"],
            "compute_unit": inf["compute_unit"],
            "timing_source": inf["timing_source"],
            "precision": inf.get("precision", "unknown"),
            "ram_peak_mb": inf.get("ram_peak_mb", "?"),
            "layers_on_npu": inf.get("layers_on_npu", "?"),
            "runtime": inf.get("runtime", "?"),
        }


# backwards compat alias
QwenIntentClassifier = RuleBasedIntentClassifier


if __name__ == "__main__":
    c = RuleBasedIntentClassifier("cpu")
    r = c.classify("PAN ABCDE1234F", ["PAN", "EMPLOYEE_FINANCIAL_DATA"])
    print("Intent:", r["classification"])
    print("Confidence:", r["confidence"])