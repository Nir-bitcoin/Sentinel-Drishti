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

def test_ocr_status_success():
    from src.vision.easyocr_screen import EasyOCRScreenAnalyzer
    a = EasyOCRScreenAnalyzer("cpu")
    assert a is not None

def test_ocr_low_confidence_failsafe():
    d = DLPEngine()
    intent = {"classification": "UNVERIFIED_DATA_TRANSFER", "confidence": 0.5}
    behavior = {"verdict": "CRITICAL_RISK", "destination": "PERSONAL_EMAIL"}
    risk = {"score": 65, "level": "HIGH"}
    r = d.evaluate("", intent, behavior, risk)
    assert r["action"] in ["BLOCK_AND_ALERT", "WARN_AND_ALERT", "ALLOW"]

def test_pii_read_local_allows():
    d = DLPEngine()
    intent = {"classification": "CONFIDENTIAL_DATA_ACCESS", "confidence": 0.82}
    behavior = {"verdict": "NORMAL", "destination": "LOCAL"}
    risk = {"score": 20, "level": "LOW"}
    r = d.evaluate("CONFIDENTIAL internal only", intent, behavior, risk)
    assert r["triggered"] == False

def test_audit_content_not_stored():
    import shutil
    from src.policy.audit_chain import AuditChain
    import json
    import datetime as dt

    shutil.rmtree("audit_logs_sec_test", ignore_errors=True)
    c = AuditChain(log_dir="audit_logs_sec_test")
    c.append({"action": "TEST", "content_redacted": True})

    today = dt.datetime.now().strftime("%Y%m%d")
    fpath = "audit_logs_sec_test/chain_" + today + ".jsonl"
    with open(fpath) as f:
        line = f.readline()
    entry = json.loads(line)
    assert entry["event"].get("content_redacted") == True
    shutil.rmtree("audit_logs_sec_test", ignore_errors=True)

def test_risk_multiple_pii_high():
    s = RiskScorer()
    entities = ["PAN", "PHONE", "AADHAAR"]
    behavior = {"verdict": "NORMAL", "destination": "LOCAL", "after_hours": False}
    r = s.calculate(entities, behavior)
    assert r["score"] >= 30

def test_risk_financial_data_adds_score():
    s = RiskScorer()
    entities = ["EMPLOYEE_FINANCIAL_DATA"]
    behavior = {"verdict": "NORMAL", "destination": "LOCAL", "after_hours": False}
    r = s.calculate(entities, behavior)
    assert r["score"] >= 20

def test_behavior_cloud_high_risk():
    t = BehaviorTracker()
    t.record("OPEN", "Excel")
    t.record("COPY", "Excel")
    t.record("OPEN", "Google Drive")
    t.record("PASTE", "Google Drive")
    r = t.assess_risk()
    assert r["verdict"] in ["HIGH_RISK", "CRITICAL_RISK"]

def test_behavior_messaging_high_risk():
    t = BehaviorTracker()
    t.record("OPEN", "Excel")
    t.record("COPY", "Excel")
    t.record("OPEN", "WhatsApp")
    t.record("PASTE", "WhatsApp")
    r = t.assess_risk()
    assert r["verdict"] in ["HIGH_RISK", "CRITICAL_RISK"]

def test_behavior_work_email_low_risk():
    t = BehaviorTracker()
    t.record("OPEN", "Excel")
    t.record("COPY", "Excel")
    t.record("OPEN", "Outlook Exchange")
    t.record("PASTE", "Outlook Exchange")
    r = t.assess_risk()
    assert r["verdict"] == "LOW_RISK"

def test_intent_unverified_transfer():
    c = RuleBasedIntentClassifier("cpu")
    r = c.classify("", [])
    assert r["classification"] == "UNVERIFIED_DATA_TRANSFER"


if __name__ == "__main__":
    tests = [
        test_pii_pan, test_pii_phone, test_pii_financial, test_no_pii_benign,
        test_behavior_usb_critical, test_behavior_gmail_critical, test_behavior_normal,
        test_risk_capped, test_dlp_blocks_pii, test_dlp_allows_benign,
        test_intent_exfiltration, test_intent_benign, test_intent_ocr_fail,
        test_audit_chain_integrity,
        test_provider_diagnostic_runs,
        test_ocr_status_success,
        test_ocr_low_confidence_failsafe,
        test_pii_read_local_allows,
        test_audit_content_not_stored,
        test_risk_multiple_pii_high,
        test_risk_financial_data_adds_score,
        test_behavior_cloud_high_risk,
        test_behavior_messaging_high_risk,
        test_behavior_work_email_low_risk,
        test_intent_unverified_transfer,
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