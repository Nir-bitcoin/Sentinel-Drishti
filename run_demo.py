# demo script
# 4 scenarios
#
# chalao: python run_demo.py             (snapdragon - simulated)
#         python run_demo.py --cpu       (cpu baseline)
#
# N - 26 sept

import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.vision.screen_capture import ScreenCapture
from src.vision.internvl_screen import InternVLScreenAnalyzer
from src.reasoning.qwen_intent import QwenIntentClassifier
from src.policy.dlp_engine import DLPEngine
from src.policy.behavior_tracker import BehaviorTracker
from src.policy.risk_scorer import RiskScorer
from simulation.simulated_arduino import SimulatedArduino


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
    print("Stage 2 - Perception")
    v = vis.analyze(content)
    print("  Sensitive: " + str(v["sensitive"]))
    print("  Entities:  " + str(v["entities"]) + " [regex pattern detection]")
    if v["timing_source"] == "SIMULATED_NPU":
        print("  Time:      " + str(v["latency_ms"]) + " ms [AI Hub benchmark reference]")
    else:
        print("  Time:      " + str(v["latency_ms"]) + " ms [measured on " + v["compute_unit"] + "]")

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
    if i["timing_source"] == "SIMULATED_NPU":
        print("  Time:             " + str(i["latency_ms"]) + " ms [AI Hub benchmark reference]")
    else:
        print("  Time:             " + str(i["latency_ms"]) + " ms [measured on " + i["compute_unit"] + "]")

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

    tot = v["latency_ms"] + i["latency_ms"]
    print()
    if v["timing_source"] == "SIMULATED_NPU":
        print("  Total reference latency: " + str(round(tot, 1)) + " ms [AI Hub benchmark]")
    else:
        print("  Total measured latency: " + str(round(tot, 1)) + " ms")


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
        print("Reference latency: Qualcomm AI Hub benchmark")
        print("NPU hardware:      Validation pending")

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

    run_one(
        "PII exfiltration to Gmail",
        "Employee salary record: Name - Rajesh Kumar, PAN - ABCDE1234F, "
        "Phone - 9876543210, Bank Account - 123456789012",
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