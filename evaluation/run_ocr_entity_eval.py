# run_ocr_entity_eval.py

import sys
import csv
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vision.easyocr_screen import EasyOCRScreenAnalyzer
from src.vision.perception import TextPerception


EVAL_DIR = Path("evaluation")
MANIFEST = EVAL_DIR / "dataset_manifest.csv"
OUT_PATH = EVAL_DIR / "ocr_entity_report.json"


def compute_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return round(precision, 4), round(recall, 4), round(f1, 4)


def load_manifest():
    if not MANIFEST.exists():
        print("Manifest not found: " + str(MANIFEST))
        return []
    rows = []
    with open(MANIFEST, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


ENTITY_TYPES = ["PAN", "PHONE", "EMPLOYEE_FINANCIAL_DATA", "CONFIDENTIAL_MARKING"]


def main():
    print("=" * 70)
    print("  SENTINEL DRISHTI - OCR -> ENTITY DETECTION RELIABILITY")
    print("=" * 70)
    print()

    rows = load_manifest()
    if not rows:
        print("No manifest rows.")
        return

    print("Test images: " + str(len(rows)))
    print()

    print("Loading OCR + entity detector...")
    ocr = EasyOCRScreenAnalyzer(mode="cpu")
    perception = TextPerception("cpu")
    print("Ready.")
    print()

    counters = {e: {"tp": 0, "fp": 0, "fn": 0} for e in ENTITY_TYPES}
    per_image = []
    ocr_success = 0
    ocr_fail = 0

    for i, row in enumerate(rows, start=1):
        img_path = Path(row["image_path"])
        image_id = row["image_id"]

        if not img_path.exists():
            print("  [" + image_id + "] SKIP (missing)")
            continue

        ocr_result = ocr.extract_text(str(img_path), use_cache=False)
        ocr_status = ocr_result["status"]
        ocr_conf = ocr_result["avg_confidence"]
        extracted = ocr_result["text"]

        if ocr_status in ("SUCCESS", "LOW_CONFIDENCE"):
            ocr_success += 1
        else:
            ocr_fail += 1

        perc = perception.analyze(extracted)
        detected = set(perc.get("entities", []))

        gt = set()
        if int(row["has_pan"]) == 1:
            gt.add("PAN")
        if int(row["has_phone"]) == 1:
            gt.add("PHONE")
        if int(row["has_financial"]) == 1:
            gt.add("EMPLOYEE_FINANCIAL_DATA")
        if int(row["has_confidential"]) == 1:
            gt.add("CONFIDENTIAL_MARKING")

        for e in ENTITY_TYPES:
            in_gt = e in gt
            in_det = e in detected
            if in_gt and in_det:
                counters[e]["tp"] += 1
            elif not in_gt and in_det:
                counters[e]["fp"] += 1
            elif in_gt and not in_det:
                counters[e]["fn"] += 1

        per_image.append({
            "image_id": image_id,
            "ocr_status": ocr_status,
            "ocr_confidence": ocr_conf,
            "ocr_text": extracted[:200],
            "gt": sorted(list(gt)),
            "detected": sorted(list(detected)),
            "missed": sorted(list(gt - detected)),
            "spurious": sorted(list(detected - gt)),
        })

        status_mark = "OK" if gt == detected else "MISMATCH"
        print("  [" + image_id + "] OCR=" + ocr_status +
              " conf=" + str(ocr_conf) +
              " gt=" + str(sorted(list(gt))) +
              " det=" + str(sorted(list(detected))) +
              " -> " + status_mark)

    total = ocr_success + ocr_fail

    print()
    print("=" * 70)
    print("  OCR PIPELINE HEALTH")
    print("=" * 70)
    print("  Images processed:  " + str(total))
    print("  OCR success:       " + str(ocr_success))
    print("  OCR failure:       " + str(ocr_fail))
    if total > 0:
        print("  OCR success rate:  " + str(round(100 * ocr_success / total, 1)) + "%")

    print()
    print("=" * 70)
    print("  ENTITY DETECTION METRICS (image -> OCR -> entity)")
    print("=" * 70)
    print()
    print("  Entity                      Precision  Recall   F1    TP  FP  FN")
    print("  " + "-" * 65)

    report_entities = {}
    for e in ENTITY_TYPES:
        c = counters[e]
        p, r, f = compute_metrics(c["tp"], c["fp"], c["fn"])
        report_entities[e] = {
            "precision": p, "recall": r, "f1": f,
            "tp": c["tp"], "fp": c["fp"], "fn": c["fn"],
        }
        print("  " + e.ljust(27) + " " +
              str(p).ljust(10) + " " + str(r).ljust(8) + " " + str(f).ljust(5) +
              " " + str(c["tp"]).ljust(3) + " " + str(c["fp"]).ljust(3) + " " + str(c["fn"]))

    # macro average
    total_tp = sum(counters[e]["tp"] for e in ENTITY_TYPES)
    total_fp = sum(counters[e]["fp"] for e in ENTITY_TYPES)
    total_fn = sum(counters[e]["fn"] for e in ENTITY_TYPES)
    macro_p, macro_r, macro_f = compute_metrics(total_tp, total_fp, total_fn)
    print()
    print("  MACRO AVG                   " +
          str(macro_p).ljust(10) + " " + str(macro_r).ljust(8) + " " + str(macro_f))

    print()
    print("  Total FP: " + str(total_fp))
    print("  Total FN: " + str(total_fn))

    # mismatches
    mismatches = [r for r in per_image if r["missed"] or r["spurious"]]
    if mismatches:
        print()
        print("=" * 70)
        print("  MISMATCHES")
        print("=" * 70)
        for r in mismatches:
            print("  " + r["image_id"] + ":")
            print("    OCR text: " + r["ocr_text"])
            if r["missed"]:
                print("    MISSED:   " + str(r["missed"]))
            if r["spurious"]:
                print("    SPURIOUS: " + str(r["spurious"]))
    else:
        print()
        print("  No mismatches. All entities matched ground truth.")

    report = {
        "total_images": total,
        "ocr_success": ocr_success,
        "ocr_failure": ocr_fail,
        "ocr_success_rate_pct": round(100 * ocr_success / total, 1) if total > 0 else 0,
        "entities": report_entities,
        "macro": {
            "precision": macro_p, "recall": macro_r, "f1": macro_f,
            "tp": total_tp, "fp": total_fp, "fn": total_fn,
        },
        "per_image": per_image,
    }
    OUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print()
    print("Report saved: " + str(OUT_PATH))
    print()


if __name__ == "__main__":
    main()