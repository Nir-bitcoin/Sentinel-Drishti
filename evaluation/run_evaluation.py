# run_evaluation.py
# Entity detection evaluation: Precision / Recall / F1.

import sys
import csv
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vision.perception import TextPerception


def compute_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return round(precision, 4), round(recall, 4), round(f1, 4)


def main():
    csv_path = Path("evaluation/ground_truth.csv")
    if not csv_path.exists():
        print("ground_truth.csv not found")
        return

    perception = TextPerception("cpu")

    entities = ["PAN", "PHONE", "EMPLOYEE_FINANCIAL_DATA"]
    counters = {e: {"tp": 0, "fp": 0, "fn": 0} for e in entities}

    total = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            text = row["text"]
            result = perception.analyze(text)
            detected = result.get("entities", [])

            gt_pan = int(row["has_pan"]) == 1
            det_pan = "PAN" in detected
            if gt_pan and det_pan:
                counters["PAN"]["tp"] += 1
            elif not gt_pan and det_pan:
                counters["PAN"]["fp"] += 1
            elif gt_pan and not det_pan:
                counters["PAN"]["fn"] += 1

            gt_ph = int(row["has_phone"]) == 1
            det_ph = "PHONE" in detected
            if gt_ph and det_ph:
                counters["PHONE"]["tp"] += 1
            elif not gt_ph and det_ph:
                counters["PHONE"]["fp"] += 1
            elif gt_ph and not det_ph:
                counters["PHONE"]["fn"] += 1

            gt_fi = int(row["has_financial"]) == 1
            det_fi = "EMPLOYEE_FINANCIAL_DATA" in detected
            if gt_fi and det_fi:
                counters["EMPLOYEE_FINANCIAL_DATA"]["tp"] += 1
            elif not gt_fi and det_fi:
                counters["EMPLOYEE_FINANCIAL_DATA"]["fp"] += 1
            elif gt_fi and not det_fi:
                counters["EMPLOYEE_FINANCIAL_DATA"]["fn"] += 1

    print("=" * 55)
    print("  ENTITY DETECTION EVALUATION")
    print("=" * 55)
    print("  Samples: " + str(total))
    print()
    print("  Entity                     Precision  Recall   F1")
    print("  " + "-" * 51)
    for e in entities:
        c = counters[e]
        p, r, f = compute_metrics(c["tp"], c["fp"], c["fn"])
        print("  " + e.ljust(26) + " " +
              str(p).ljust(10) + " " + str(r).ljust(8) + " " + str(f))
    print()
    print("  Confusion matrix per entity:")
    for e in entities:
        c = counters[e]
        print("    " + e + ": TP=" + str(c["tp"]) +
              " FP=" + str(c["fp"]) + " FN=" + str(c["fn"]))
    print()


if __name__ == "__main__":
    main()