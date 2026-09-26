# test_security_deep.py


import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import shutil
import json
import datetime as dt

from src.vision.perception import TextPerception
from src.policy.behavior_tracker import BehaviorTracker
from src.policy.risk_scorer import RiskScorer
from src.policy.dlp_engine import DLPEngine
from src.policy.audit_chain import AuditChain
from src.reasoning.intent_classifier import RuleBasedIntentClassifier
from src.vision import easyocr_screen


# ---------- PII detection ----------

def t_pan_detected():
    a = TextPerception("cpu")
    r = a.analyze("PAN ABCDE1234F")
    assert "PAN" in r["entities"]

def t_phone_detected():
    a = TextPerception("cpu")
    r = a.analyze("Call 9876543210")
    assert "PHONE" in r["entities"]

def t_financial_detected():
    a = TextPerception("cpu")
    r = a.analyze("Employee salary breakdown")
    assert "EMPLOYEE_FINANCIAL_DATA" in r["entities"]

def t_benign_no_pii():
    a = TextPerception("cpu")
    r = a.analyze("Meeting at 3pm in room 4")
    assert not r["sensitive"]

def t_empty_text():
    a = TextPerception("cpu")
    r = a.analyze("")
    assert r["sensitive"] == False

def t_whitespace_text():
    a = TextPerception("cpu")
    r = a.analyze("   \n\t  ")
    assert r["sensitive"] == False

def t_unicode_text():
    a = TextPerception("cpu")
    r = a.analyze("यह एक सामान्य संदेश है")
    assert isinstance(r, dict)

def t_long_text():
    a = TextPerception("cpu")
    r = a.analyze("word " * 10000)
    assert isinstance(r, dict)


# ---------- Behavior ----------

def t_usb_exfil_critical():
    t = BehaviorTracker()
    t.record("OPEN", "Excel")
    t.record("COPY", "Excel")
    t.record("USB_INSERT", "USB")
    t.record("PASTE", "USB")
    assert t.assess_risk()["verdict"] == "CRITICAL_RISK"

def t_gmail_exfil_critical():
    t = BehaviorTracker()
    t.record("OPEN", "Excel")
    t.record("COPY", "Excel")
    t.record("OPEN", "Gmail")
    t.record("PASTE", "Gmail")
    assert t.assess_risk()["verdict"] == "CRITICAL_RISK"

def t_benign_normal():
    t = BehaviorTracker()
    t.record("OPEN", "Notepad")
    t.record("TYPE", "Notepad")
    assert t.assess_risk()["verdict"] == "NORMAL"

def t_duplicate_events():
    t = BehaviorTracker()
    for _ in range(100):
        t.record("COPY", "Excel")
    assert t.assess_risk() is not None

def t_event_ordering():
    t = BehaviorTracker()
    t.record("PASTE", "Gmail")
    t.record("COPY", "Excel")
    assert t.assess_risk() is not None


# ---------- Risk ----------

def t_risk_score_capped():
    s = RiskScorer()
    e = ["PAN", "PHONE", "AADHAAR", "ACCOUNT_NUMBER", "EMPLOYEE_FINANCIAL_DATA"]
    b = {"verdict": "CRITICAL_RISK", "destination": "EXTERNAL_DEVICE", "after_hours": True}
    r = s.calculate(e, b)
    assert 0 <= r["score"] <= 100

def t_risk_zero_benign():
    s = RiskScorer()
    r = s.calculate([], {"verdict": "NORMAL", "destination": "LOCAL", "after_hours": False})
    assert r["score"] < 30

def t_risk_multiple_pii():
    s = RiskScorer()
    r = s.calculate(["PAN", "PHONE", "AADHAAR"],
                    {"verdict": "NORMAL", "destination": "LOCAL", "after_hours": False})
    assert r["score"] >= 30

def t_risk_after_hours_boost():
    s = RiskScorer()
    r1 = s.calculate(["PAN"], {"verdict": "NORMAL", "destination": "LOCAL", "after_hours": False})
    r2 = s.calculate(["PAN"], {"verdict": "NORMAL", "destination": "LOCAL", "after_hours": True})
    assert r2["score"] >= r1["score"]


# ---------- DLP ----------

def t_dlp_blocks_pii_external():
    d = DLPEngine()
    intent = {"classification": "EXFILTRATION", "confidence": 0.97}
    b = {"verdict": "CRITICAL_RISK", "destination": "PERSONAL_EMAIL"}
    risk = {"score": 100, "level": "CRITICAL"}
    r = d.evaluate("PAN ABCDE1234F", intent, b, risk)
    assert r["triggered"]

def t_dlp_allows_benign():
    d = DLPEngine()
    intent = {"classification": "BENIGN", "confidence": 0.95}
    b = {"verdict": "NORMAL", "destination": "LOCAL"}
    risk = {"score": 0, "level": "NONE"}
    r = d.evaluate("meeting notes", intent, b, risk)
    assert not r["triggered"]

def t_dlp_usb_destination():
    d = DLPEngine()
    intent = {"classification": "EXFILTRATION", "confidence": 0.9}
    b = {"verdict": "CRITICAL_RISK", "destination": "EXTERNAL_DEVICE"}
    risk = {"score": 90, "level": "CRITICAL"}
    r = d.evaluate("salary 1000000", intent, b, risk)
    assert r["triggered"]

def t_dlp_cloud_destination():
    d = DLPEngine()
    intent = {"classification": "EXFILTRATION", "confidence": 0.9}
    b = {"verdict": "HIGH_RISK", "destination": "CLOUD_STORAGE"}
    risk = {"score": 80, "level": "HIGH"}
    r = d.evaluate("PAN ABCDE1234F", intent, b, risk)
    assert r["triggered"]

def t_dlp_empty_text():
    d = DLPEngine()
    intent = {"classification": "UNVERIFIED_DATA_TRANSFER", "confidence": 0.5}
    b = {"verdict": "CRITICAL_RISK", "destination": "PERSONAL_EMAIL"}
    risk = {"score": 65, "level": "HIGH"}
    r = d.evaluate("", intent, b, risk)
    assert isinstance(r, dict)


# ---------- Intent ----------

def t_intent_exfil():
    c = RuleBasedIntentClassifier("cpu")
    r = c.classify("PAN ABCDE1234F", ["PAN"])
    assert r["classification"] in ["EXFILTRATION", "CONFIDENTIAL_DATA_ACCESS"]

def t_intent_benign():
    c = RuleBasedIntentClassifier("cpu")
    r = c.classify("meeting notes", [])
    assert r["classification"] == "BENIGN"

def t_intent_empty():
    c = RuleBasedIntentClassifier("cpu")
    r = c.classify("", [])
    assert r["classification"] == "UNVERIFIED_DATA_TRANSFER"


# ---------- Audit chain ----------

def t_audit_integrity():
    shutil.rmtree("audit_logs_t1", ignore_errors=True)
    c = AuditChain(log_dir="audit_logs_t1")
    for i in range(5):
        c.append({"action": "E" + str(i)})
    valid, _ = c.verify_chain()
    assert valid
    shutil.rmtree("audit_logs_t1", ignore_errors=True)

def t_audit_content_redacted():
    shutil.rmtree("audit_logs_t2", ignore_errors=True)
    c = AuditChain(log_dir="audit_logs_t2")
    c.append({"action": "TEST", "content_redacted": True})
    valid, _ = c.verify_chain()
    assert valid
    shutil.rmtree("audit_logs_t2", ignore_errors=True)

def t_audit_tamper_detected():
    shutil.rmtree("audit_logs_t3", ignore_errors=True)
    c = AuditChain(log_dir="audit_logs_t3")
    c.append({"action": "A"})
    c.append({"action": "B"})
    c.append({"action": "C"})

    today = dt.datetime.now().strftime("%Y%m%d")
    fpath = Path("audit_logs_t3") / ("chain_" + today + ".jsonl")

    tamper_worked = False
    if fpath.exists():
        lines = fpath.read_text(encoding="utf-8").strip().split("\n")
        if len(lines) >= 2:
            entry = json.loads(lines[1])
            entry["event"]["action"] = "TAMPERED"
            lines[1] = json.dumps(entry)
            fpath.write_text("\n".join(lines) + "\n", encoding="utf-8")
            tamper_worked = True

    if tamper_worked:
        c2 = AuditChain(log_dir="audit_logs_t3")
        valid, msg = c2.verify_chain()
        assert valid == False, "Tamper not detected: " + str(msg)

    shutil.rmtree("audit_logs_t3", ignore_errors=True)


# ---------- Cache ----------

def t_cache_stats_exist():
    s = easyocr_screen.cache_stats()
    assert "hits" in s and "misses" in s and "hit_rate_pct" in s

def t_cache_clear():
    easyocr_screen.cache_clear()
    s = easyocr_screen.cache_stats()
    assert s["hits"] == 0 and s["misses"] == 0

def t_cache_put_get():
    easyocr_screen.cache_clear()
    easyocr_screen.cache_put("testkey", {"text": "hello", "avg_confidence": 0.9})
    got = easyocr_screen.cache_get("testkey")
    assert got is not None and got["text"] == "hello"

def t_cache_eviction():
    easyocr_screen.cache_clear()
    for i in range(150):
        easyocr_screen.cache_put("key_" + str(i), {"text": str(i)})
    s = easyocr_screen.cache_stats()
    assert s["size"] <= 100


# ---------- Provider ----------

def t_provider_returns_backend():
    from src.backend.base import get_backend_with_fallback
    b = get_backend_with_fallback()
    assert b is not None


if __name__ == "__main__":
    tests = [
        t_pan_detected, t_phone_detected, t_financial_detected,
        t_benign_no_pii, t_empty_text, t_whitespace_text,
        t_unicode_text, t_long_text,
        t_usb_exfil_critical, t_gmail_exfil_critical, t_benign_normal,
        t_duplicate_events, t_event_ordering,
        t_risk_score_capped, t_risk_zero_benign, t_risk_multiple_pii,
        t_risk_after_hours_boost,
        t_dlp_blocks_pii_external, t_dlp_allows_benign,
        t_dlp_usb_destination, t_dlp_cloud_destination, t_dlp_empty_text,
        t_intent_exfil, t_intent_benign, t_intent_empty,
        t_audit_integrity, t_audit_content_redacted, t_audit_tamper_detected,
        t_cache_stats_exist, t_cache_clear, t_cache_put_get, t_cache_eviction,
        t_provider_returns_backend,
    ]

    passed = 0
    failed = 0
    failed_names = []
    for t in tests:
        try:
            t()
            print("PASS: " + t.__name__)
            passed += 1
        except Exception as e:
            print("FAIL: " + t.__name__ + " -> " + str(e))
            failed += 1
            failed_names.append(t.__name__)

    print()
    print("=" * 50)
    print("Total: " + str(passed) + "/" + str(passed + failed) + " passing")
    if failed_names:
        print("Failed: " + ", ".join(failed_names))
    print("=" * 50)