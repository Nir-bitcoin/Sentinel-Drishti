# run_demo.py
#
# 4 scenarios. Real EasyOCR for image input.
# Adaptive OCR - fast pass + retry if needed.


import sys
import argparse
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.vision.screen_capture import ScreenCapture
from src.vision.internvl_screen import InternVLScreenAnalyzer
from src.vision.easyocr_screen import EasyOCRScreenAnalyzer
from src.reasoning.qwen_intent import QwenIntentClassifier
from src.reasoning.translator import AlertTranslator
from src.policy.dlp_engine import DLPEngine
from src.policy.behavior_tracker import BehaviorTracker
from src.policy.risk_scorer import RiskScorer
from simulation.simulated_arduino import SimulatedArduino


# AI Hub pe actual EasyOCR jobs
DET_MS = 39.5
DET_JOB = "jpxlmx3jp"
REC_MS = 19.3
REC_JOB = "jprl9wnvp"


def run_one(title, content, app, actions, mode):
    print()
    print("Scenario: " + title)
    print()

    cap = ScreenCapture()
    vis = InternVLScreenAnalyzer(mode)
    rea = QwenIntentClassifier(mode)
    trk = BehaviorTracker()
    scr = RiskScorer()
    dlp = DLPEngine()
    ard = SimulatedArduino()

    print("Stage 1 - Screen capture")
    c = cap.capture_text(content, app)
    print("  Source: " + c["source"])
    print("  App:  " + c["app"])
    prev = content[:60]
    if len(content) > 60:
        prev += "..."
    print("  Text: " + prev)

    print()
    print("Stage 2 - Perception (regex on text)")
    v = vis.analyze(content)
    print("  Sensitive: " + str(v["sensitive"]))
    print("  Entities:  " + str(v["entities"]))

    print()
    print("Stage 3 - Behavior tracking")
    for a in actions:
        trk.record(a["action"], a["app"])
        print("  " + a["action"] + " -> " + a["app"])
    b = trk.assess_risk()
    print("  Verdict:     " + b["verdict"])
    print("  Destination: " + b.get("destination", "LOCAL"))
    print("  Reason:      " + b["reason"])

    print()
    print("Stage 4 - Risk scoring")
    r = scr.calculate(v["entities"], b)
    if r["raw_score"] > 100:
        print("  Raw score:   " + str(r["raw_score"]))
        print("  Final score: " + str(r["score"]) + " / 100 (" + r["level"] + ", capped)")
    else:
        print("  SCORE: " + str(r["score"]) + " / 100 (" + r["level"] + ")")
    for x in r["reasons"]:
        print("    - " + x)

    print()
    print("Stage 5 - Reasoning (rule engine)")
    i = rea.classify(content, v["entities"])
    print("  Intent:           " + i["classification"])
    print("  Rule match score: " + str(i["confidence"]) + " [rule-engine]")

    print()
    print("Stage 6 - DLP decision")
    d = dlp.evaluate(content, i, b, r)
    print("  Triggered: " + str(d["triggered"]))
    print("  Action:    " + d["action"])
    print()
    print("  Explanation:")
    for line in d["explanation"]:
        print("    - " + line)

    enf_status = None
    if d.get("enforcement"):
        e = d["enforcement"]
        enf_status = e.get("mode", "SIMULATED")
        print()
        print("  ENFORCEMENT (DEMO/SIMULATED):")
        print("    - " + e["blocked_action"] + ": BLOCK ACTION TRIGGERED")
        print("    - Enforcement status: " + enf_status)
        print("    - Note: actual interception not performed on this laptop")

        trans = AlertTranslator()
        msg = d["action"] + " - " + e["blocked_action"]
        print()
        print("  LOCALIZED ALERTS (sample):")
        print("    EN: " + msg)
        print("    HI: " + trans.translate(msg, "hi")["text"])
        print("    (full 5-language list in docs/i18n_examples.md)")

    print()
    print("Stage 7 - Arduino UNO Q")
    if d["triggered"]:
        ard.trigger_alert(d["severity"])
    else:
        ard.reset()

    print()
    print("  Decision summary:")
    print("    Risk:        " + str(r["score"]) + "/100")
    print("    Action:      " + d["action"])
    if enf_status:
        print("    Enforcement: " + enf_status)


def run_image_scenario(title, image_path, app, actions, mode):
    print()
    print("Scenario: " + title)
    print()

    if not Path(image_path).exists():
        print("  [Image not found: " + image_path + "]")
        print("  [Skipping scenario]")
        return

    ocr = EasyOCRScreenAnalyzer(mode)
    rea = QwenIntentClassifier(mode)
    trk = BehaviorTracker()
    scr = RiskScorer()
    dlp = DLPEngine()
    ard = SimulatedArduino()

    print("Stage 1 - Input")
    print("  Image: " + image_path)
    print("  App:   " + app)

    print()
    print("Stage 2 - OCR (EasyOCR)")
    o = ocr.extract_text(image_path)

    txt_preview = o["text"][:70]
    if len(o["text"]) > 70:
        txt_preview += "..."

    print("  Extracted text: " + txt_preview)
    print("  OCR status:     " + o["status"])
    print("  Method:         " + o["method"])
    print("  Detections:     " + str(o["num_detections"]))
    print("  Avg confidence: " + str(o["avg_confidence"]))
    print("  Min confidence: " + str(o["min_confidence"]))
    print("  Init time:      " + str(o["init_ms"]) + " ms [one-time model load]")
    print("  Image:          " + o["image_size"] + " (width=" + str(o["used_width"]) + ")")
    print("  Passes used:    " + str(o["passes_used"]))
    print("  Fast pass conf: " + str(o["fast_pass_conf"]) + " (" + o["fast_pass_status"] + ")")
    print("  Inference time: " + str(o["inference_ms"]) + " ms [CPU]")
    if o["load_error"]:
        print("  Load error:     " + o["load_error"])
    print()
    print("  Snapdragon X Elite reference (component benchmarks):")
    print("    Detector:      ~" + str(DET_MS) + " ms  [job " + DET_JOB + "]")
    print("    Recognizer:    ~" + str(REC_MS) + " ms  [job " + REC_JOB + "]")
    print("    Compute:       NPU (Hexagon HTP)")
    print("    Status:        Hosted-device benchmark")
    print("    Note:          separate component benchmarks, not end-to-end")
    print("    Verify:        https://aihub.qualcomm.com/jobs/" + REC_JOB)

    content = o["text"]
    ocr_status = o["status"]
    ocr_usable = (ocr_status == "SUCCESS")

    if ocr_status == "LOW_CONFIDENCE":
        print()
        print("  WARNING: OCR confidence LOW (" + str(o["avg_confidence"]) + ")")
        print("  Content visibility: DEGRADED")

    print()
    print("Stage 3 - Perception (regex on OCR text)")
    vis = InternVLScreenAnalyzer(mode)
    v = vis.analyze(content)
    print("  Sensitive: " + str(v["sensitive"]))
    print("  Entities:  " + str(v["entities"]))

    if not ocr_usable:
        print("  WARNING: OCR text not reliable. Content visibility UNKNOWN.")

    print()
    print("Stage 4 - Behavior tracking")
    for a in actions:
        trk.record(a["action"], a["app"])
        print("  " + a["action"] + " -> " + a["app"])
    b = trk.assess_risk()
    print("  Verdict:     " + b["verdict"])
    print("  Destination: " + b.get("destination", "LOCAL"))
    print("  Reason:      " + b["reason"])

    print()
    print("Stage 5 - Risk scoring")
    r = scr.calculate(v["entities"], b)
    if r["raw_score"] > 100:
        print("  Raw score:   " + str(r["raw_score"]))
        print("  Final score: " + str(r["score"]) + " / 100 (" + r["level"] + ", capped)")
    else:
        print("  SCORE: " + str(r["score"]) + " / 100 (" + r["level"] + ")")
    for x in r["reasons"]:
        print("    - " + x)

    print()
    print("Stage 6 - Reasoning (rule engine)")
    i = rea.classify(content, v["entities"])
    print("  Intent:           " + i["classification"])
    print("  Rule match score: " + str(i["confidence"]) + " [rule-engine]")

    print()
    print("Stage 7 - DLP decision")

    # fail-safe: agar OCR low-confidence hai aur behavior risky
    if (not ocr_usable) and b["verdict"] in ["CRITICAL_RISK", "HIGH_RISK"]:
        d = {
            "triggered": True,
            "action": "WARN_AND_ALERT",
            "severity": "HIGH",
            "explanation": [
                "OCR status: " + ocr_status,
                "OCR confidence: " + str(o["avg_confidence"]),
                "Content visibility: DEGRADED",
                "Behavior verdict: " + b["verdict"],
                "Risk: HIGH (unverified content)",
                "Decision: WARN + ALERT (fail-safe)",
                "Reason: Sensitive content could not be reliably classified",
            ],
            "enforcement": {
                "blocked_action": "PASTE (unverified content)",
                "mode": "SIMULATED",
            },
        }
    else:
        d = dlp.evaluate(content, i, b, r)

    print("  Triggered: " + str(d["triggered"]))
    print("  Action:    " + d["action"])
    print()
    print("  Explanation:")
    for line in d["explanation"]:
        print("    - " + line)

    enf_status = None
    if d.get("enforcement"):
        e = d["enforcement"]
        enf_status = e.get("mode", "SIMULATED")
        print()
        print("  ENFORCEMENT (DEMO/SIMULATED):")
        print("    - " + e["blocked_action"] + ": BLOCK ACTION TRIGGERED")
        print("    - Enforcement status: " + enf_status)

        trans = AlertTranslator()
        msg = d["action"] + " - " + e["blocked_action"]
        print()
        print("  LOCALIZED ALERTS (sample):")
        print("    EN: " + msg)
        print("    HI: " + trans.translate(msg, "hi")["text"])
        print("    (full 5-language list in docs/i18n_examples.md)")

    print()
    print("Stage 8 - Arduino UNO Q")
    if d["triggered"]:
        ard.trigger_alert(d["severity"])
    else:
        ard.reset()

    print()
    print("  Decision summary:")
    print("    Risk:        " + str(r["score"]) + "/100")
    print("    Action:      " + d["action"])
    if enf_status:
        print("    Enforcement: " + enf_status)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cpu", action="store_true", help="CPU backend use karo")
    args = p.parse_args()

    mode = "cpu" if args.cpu else "snapdragon"

    print()
    print("SENTINEL DRISHTI - demo run")
    print("Snapdragon AI Lab Challenge 2026")
    print()

    if mode == "cpu":
        print("Backend:           CPU")
        print("Execution:         Local / real")
        print("Timing:            Measured")
    else:
        print("Backend:           Snapdragon-targeted")
        print("Host:              Local CPU laptop")
        print("Target values:     Qualcomm AI Hub component benchmarks")
        print("NPU hardware:      Validation pending")

    print()
    print("Warming up EasyOCR model (one-time)...")
    warmup = EasyOCRScreenAnalyzer(mode)
    print("Warmup done. Ready for scenarios.")

    run_one(
        "Normal work (no risk)",
        "Team meeting scheduled for 3pm to discuss Q4 roadmap",
        "Notepad",
        [
            {"action": "OPEN", "app": "Notepad"},
            {"action": "TYPE", "app": "Notepad"},
            {"action": "SAVE", "app": "Notepad"},
        ],
        mode
    )

    run_image_scenario(
        "Image-based PII detection (EasyOCR)",
        "docs/screenshots/hr_screenshot.png",
        "Excel (HR_salaries.xlsx)",
        [
            {"action": "OPEN", "app": "Excel"},
            {"action": "COPY", "app": "Excel"},
            {"action": "OPEN", "app": "Gmail"},
            {"action": "PASTE", "app": "Gmail"},
        ],
        mode
    )

    run_one(
        "Confidential document (read only)",
        "CONFIDENTIAL: Internal only - Q4 pricing strategy draft",
        "Word (pricing_draft.docx)",
        [
            {"action": "OPEN", "app": "Word"},
            {"action": "READ", "app": "Word"},
        ],
        mode
    )

    run_one(
        "Sensitive data copied to USB",
        "Employee salary record: PAN - ABCDE1234F, Phone - 9876543210",
        "Excel (HR_salaries.xlsx)",
        [
            {"action": "OPEN", "app": "Excel"},
            {"action": "COPY", "app": "Excel"},
            {"action": "INSERT", "app": "USB Drive"},
            {"action": "PASTE", "app": "USB Drive"},
        ],
        mode
    )

    print()
    print("Done. Logs in audit_logs/")
    print()


if __name__ == "__main__":
    main()