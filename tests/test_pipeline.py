# test_pipeline.py
# Basic tests for Sentinel Drishti pipeline.
# Run: python tests/test_pipeline.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vision.perception import TextPerception
from src.policy.behavior_tracker import BehaviorTracker
from src.policy.risk_scorer import RiskScorer
from src.policy.dlp_engine import DLPEngine
from src.policy.audit_chain import AuditChain
from src.reasoning.intent_classifier import RuleBasedIntentClassifier


def test_pii_pan():
    a = TextPerception("cpu")
    r = a.analyze("PAN - ABCDE1234F")
    assert "PAN" in r["entities"]

def test_pii_phone():
    a = TextPerception("cpu")
    r = a.analyze("Phone - 9876543210")
    assert "PHONE" in r["entities"]

def test_pii_financial():
    a = TextPerception("cpu")
    r = a.analyze("Employee salary record")
    assert "EMPLOYEE_FINANCIAL_DATA" in r["entities"]

def test_no_pii_benign():
    a = TextPerception("cpu")
    r = a.analyze("Team meeting at 3pm")
    assert r["sensitive"] == False

def test_behavior_usb_critical():
    t = BehaviorTracker()
    t.record("OPEN", "Excel")
    t.record("COPY", "Excel")
    t.record("INSERT", "USB Drive")
    t.record("PASTE", "USB Drive")
    r = t.assess_risk()
    assert r["verdict"] == "CRITICAL_RISK"

def test_behavior_gmail_critical():
    t = BehaviorTracker()
    t.record("OPEN", "Excel")
    t.record("COPY", "Excel")
    t.record("OPEN", "Gmail")
    t.record("PASTE", "Gmail")
    r = t.assess_risk()
    assert r["verdict"] == "CRITICAL_RISK"

def test_behavior_normal():
    t = BehaviorTracker()
    t.record("OPEN", "Notepad")
    t.record("TYPE", "Notepad")
    r = t.assess_risk()
    assert r["verdict"] == "NORMAL"

def test_risk_capped():
    s = RiskScorer()
    entities = ["PAN", "PHONE", "ACCOUNT_NUMBER", "EMPLOYEE_FINANCIAL_DATA"]
    behavior = {"verdict": "CRITICAL_RISK", "destination": "EXTERNAL_DEVICE", "after_hours": True}
    r = s.calculate(entities, behavior)
    assert r["score"] <= 100

def test_dlp_blocks_pii():
    d = DLPEngine()
    intent = {"classification": "EXFILTRATION", "confidence": 0.97}
    behavior = {"verdict": "CRITICAL_RISK", "destination": "PERSONAL_EMAIL"}
    risk = {"score": 100, "level": "CRITICAL"}
    r = d.evaluate("PAN ABCDE1234F", intent, behavior, risk)
    assert r["triggered"] == True

def test_dlp_allows_benign():
    d = DLPEngine()
    intent = {"classification": "BENIGN", "confidence": 0.95}
    behavior = {"verdict": "NORMAL", "destination": "LOCAL"}
    risk = {"score": 0, "level": "NONE"}
    r = d.evaluate("meeting notes", intent, behavior, risk)
    assert r["triggered"] == False

def test_intent_exfiltration():
    c = RuleBasedIntentClassifier("cpu")
    r = c.classify("PAN ABCDE1234F", ["PAN", "EMPLOYEE_FINANCIAL_DATA"])
    assert r["classification"] == "EXFILTRATION"

def test_intent_benign():
    c = RuleBasedIntentClassifier("cpu")
    r = c.classify("meeting notes", [])
    assert r["classification"] == "BENIGN"

def test_intent_ocr_fail():
    c = RuleBasedIntentClassifier("cpu")
    r = c.classify("", [])
    assert r["classification"] == "UNVERIFIED_DATA_TRANSFER"

def test_audit_chain_integrity():
    import shutil
    c = AuditChain(log_dir="audit_logs_test")
    c.append({"action": "TEST_A"})
    c.append({"action": "TEST_B"})
    c.append({"action": "TEST_C"})
    valid, msg = c.verify_chain()
    assert valid == True
    shutil.rmtree("audit_logs_test", ignore_errors=True)

def test_provider_diagnostic_runs():
    import subprocess
    result = subprocess.run(
        [sys.executable, "scripts/check_provider.py"],
        capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0
    assert "Selected provider" in result.stdout


if __name__ == "__main__":
    tests = [
        test_pii_pan, test_pii_phone, test_pii_financial, test_no_pii_benign,
        test_behavior_usb_critical, test_behavior_gmail_critical, test_behavior_normal,
        test_risk_capped, test_dlp_blocks_pii, test_dlp_allows_benign,
        test_intent_exfiltration, test_intent_benign, test_intent_ocr_fail,
        test_audit_chain_integrity,
        test_provider_diagnostic_runs,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS: " + t.__name__)
            passed += 1
        except AssertionError:
            print("FAIL: " + t.__name__)
            failed += 1
    print()
    print("Total: " + str(passed) + "/" + str(passed + failed) + " passing")