# test_offline.py


import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import socket


class NetworkBlocked(Exception):
    pass


def _blocked(*args, **kwargs):
    raise NetworkBlocked("Network access attempted")


def install_blocker():
    socket.socket = _blocked
    socket.create_connection = _blocked
    socket.getaddrinfo = _blocked


def uninstall_blocker():
    import importlib
    importlib.reload(socket)


def run_pipeline():
    from src.vision.perception import TextPerception
    from src.policy.behavior_tracker import BehaviorTracker
    from src.policy.risk_scorer import RiskScorer
    from src.policy.dlp_engine import DLPEngine
    from src.policy.audit_chain import AuditChain
    from src.policy.data_flow import DataFlowGraph
    from src.policy.session_risk import SessionRisk
    from src.security.masking import mask_all
    from src.reasoning.intent_classifier import RuleBasedIntentClassifier

    text = "Employee salary PAN ABCDE1234F phone 9876543210"

    perc = TextPerception("cpu").analyze(text)
    entities = perc["entities"]

    tracker = BehaviorTracker()
    tracker.record("OPEN", "Excel")
    tracker.record("COPY", "Excel")
    tracker.record("OPEN", "Gmail")
    tracker.record("PASTE", "Gmail")
    behavior = tracker.assess_risk()

    risk = RiskScorer().calculate(entities, behavior)
    intent = RuleBasedIntentClassifier("cpu").classify(text, entities)
    decision = DLPEngine().evaluate(text, intent, behavior, risk)

    flow = DataFlowGraph()
    flow.record("COPY", "Excel", entities=entities)
    flow.record("PASTE", "Gmail")
    flow_result = flow.analyze()

    session = SessionRisk()
    session.record_event("COPY", "Excel", entities=entities)
    session.record_event("PASTE", "Gmail")

    masked = mask_all(text)

    import shutil
    shutil.rmtree("audit_logs_offline_test", ignore_errors=True)
    chain = AuditChain(log_dir="audit_logs_offline_test")
    chain.append({"action": "OFFLINE_TEST"})
    valid, _ = chain.verify_chain()
    shutil.rmtree("audit_logs_offline_test", ignore_errors=True)

    return {
        "entities": entities,
        "behavior": behavior["verdict"],
        "risk": risk["score"],
        "intent": intent["classification"],
        "decision": decision["decision"],
        "flow_verdict": flow_result["verdict"],
        "session_risk": session.score(),
        "masked": masked,
        "audit_valid": valid,
    }


def main():
    print("=" * 60)
    print("  SENTINEL DRISHTI - OFFLINE VERIFICATION")
    print("=" * 60)
    print()
    print("  Blocking all network calls...")
    install_blocker()
    print("  Network block: ACTIVE")
    print()

    try:
        result = run_pipeline()
        status = "PASS"
    except NetworkBlocked as e:
        print("  FAIL: " + str(e))
        status = "FAIL"
        result = {}
    except Exception as e:
        print("  FAIL (unexpected): " + str(e))
        status = "FAIL"
        result = {}
    finally:
        uninstall_blocker()

    if status == "PASS":
        print("  Full pipeline ran with ZERO network calls.")
        print()
        print("  Results:")
        print("    Entities:      " + str(result["entities"]))
        print("    Behavior:      " + result["behavior"])
        print("    Risk:          " + str(result["risk"]) + "/100")
        print("    Intent:        " + result["intent"])
        print("    DLP decision:  " + result["decision"])
        print("    Data flow:     " + result["flow_verdict"])
        print("    Session risk:  " + str(result["session_risk"]) + "/100")
        print("    Masked:        " + result["masked"])
        print("    Audit chain:   " + ("VALID" if result["audit_valid"] else "INVALID"))
        print()

    print("=" * 60)
    print("  OFFLINE VERIFICATION: " + status)
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()