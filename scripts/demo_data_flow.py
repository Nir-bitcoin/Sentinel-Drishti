# demo_data_flow.py
# Demo showing data flow graph + session risk + WARN decision.

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.policy.data_flow import DataFlowGraph
from src.policy.session_risk import SessionRisk
from src.policy.dlp_engine import DLPEngine
from src.policy.behavior_tracker import BehaviorTracker
from src.policy.risk_scorer import RiskScorer
from src.reasoning.intent_classifier import RuleBasedIntentClassifier


def run_scenario(name, actions, entities, text):
    print("=" * 60)
    print("  " + name)
    print("=" * 60)

    flow = DataFlowGraph()
    session = SessionRisk()
    tracker = BehaviorTracker()
    scorer = RiskScorer()
    dlp = DLPEngine()
    intent_clf = RuleBasedIntentClassifier("cpu")

    for a in actions:
        flow.record(a["action"], a["app"], entities=entities if a["action"] == "COPY" else [])
        session.record_event(a["action"], a["app"], entities=entities if a["action"] == "COPY" else [])
        tracker.record(a["action"], a["app"])

    behavior = tracker.assess_risk()
    risk = scorer.calculate(entities, behavior)
    intent = intent_clf.classify(text, entities)

    print()
    print("DATA FLOW ANALYSIS")
    print("-" * 60)
    print(flow.render())
    print()

    print("SESSION RISK")
    print("-" * 60)
    print("  Score: " + str(session.score()) + "/100 (" + session.level() + ")")
    print()
    for e in session.events:
        print("    " + e["action"].ljust(12) + " +" + str(e["delta"]).ljust(4) +
              "  total=" + str(e["raw_score_after"]))
    print()

    print("BEHAVIOR + RISK")
    print("-" * 60)
    print("  Verdict:     " + behavior["verdict"])
    print("  Destination: " + behavior.get("destination", "?"))
    print("  Risk:        " + str(risk["score"]) + "/100 (" + risk["level"] + ")")
    print()

    decision = dlp.evaluate(text, intent, behavior, risk)
    print("DLP DECISION")
    print("-" * 60)
    print("  Decision:   " + decision["decision"])
    print("  Triggered:  " + str(decision["triggered"]))
    print("  Requires confirmation: " + str(decision.get("requires_user_confirmation", False)))
    print()
    for line in decision["explanation"]:
        print("    - " + line)
    print()


def main():
    print()
    print("#" * 60)
    print("#  SENTINEL DRISHTI - DATA FLOW + SESSION RISK DEMO")
    print("#" * 60)
    print()

    # scenario 1: exfiltration
    run_scenario(
        "Scenario 1: Excel -> Gmail (EXFILTRATION)",
        [
            {"action": "OPEN", "app": "Excel"},
            {"action": "COPY", "app": "Excel"},
            {"action": "OPEN", "app": "Gmail"},
            {"action": "PASTE", "app": "Gmail"},
        ],
        entities=["EMPLOYEE_FINANCIAL_DATA", "PAN", "PHONE"],
        text="Employee salary record PAN ABCDE1234F phone 9876543210",
    )

    # scenario 2: USB
    run_scenario(
        "Scenario 2: Excel -> USB (EXFILTRATION)",
        [
            {"action": "OPEN", "app": "Excel"},
            {"action": "COPY", "app": "Excel"},
            {"action": "USB_INSERT", "app": "USB Drive"},
            {"action": "PASTE", "app": "USB Drive"},
        ],
        entities=["PAN"],
        text="PAN ABCDE1234F",
    )

    # scenario 3: cloud -> WARN
    run_scenario(
        "Scenario 3: Excel -> Google Drive (WARN)",
        [
            {"action": "OPEN", "app": "Excel"},
            {"action": "COPY", "app": "Excel"},
            {"action": "OPEN", "app": "Google Drive"},
            {"action": "PASTE", "app": "Google Drive"},
        ],
        entities=["PAN"],
        text="PAN ABCDE1234F",
    )

    # scenario 4: benign
    run_scenario(
        "Scenario 4: Notepad typing (ALLOW)",
        [
            {"action": "OPEN", "app": "Notepad"},
            {"action": "TYPE", "app": "Notepad"},
        ],
        entities=[],
        text="team meeting at 3pm",
    )


if __name__ == "__main__":
    main()