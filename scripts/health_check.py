# health_check.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def check(name, fn):
    try:
        fn()
        return (name, "PASS", "")
    except Exception as e:
        return (name, "FAIL", str(e)[:60])


def check_python():
    assert sys.version_info >= (3, 10)

def check_deps():
    import numpy
    import PIL

def check_ocr():
    from src.vision.easyocr_screen import EasyOCRScreenAnalyzer
    assert EasyOCRScreenAnalyzer("cpu") is not None

def check_perception():
    from src.vision.perception import TextPerception
    assert TextPerception("cpu") is not None

def check_risk():
    from src.policy.risk_scorer import RiskScorer
    r = RiskScorer()
    out = r.calculate([], {"verdict": "NORMAL", "destination": "LOCAL", "after_hours": False})
    assert "score" in out

def check_dlp():
    from src.policy.dlp_engine import DLPEngine
    assert DLPEngine() is not None

def check_audit():
    import shutil
    from src.policy.audit_chain import AuditChain
    shutil.rmtree("audit_logs_healthcheck", ignore_errors=True)
    c = AuditChain(log_dir="audit_logs_healthcheck")
    c.append({"action": "HEALTHCHECK"})
    valid, _ = c.verify_chain()
    assert valid
    shutil.rmtree("audit_logs_healthcheck", ignore_errors=True)

def check_cache():
    from src.vision import easyocr_screen
    s = easyocr_screen.cache_stats()
    assert "hits" in s

def check_cpu_backend():
    from src.backend.base import get_backend_with_fallback
    assert get_backend_with_fallback() is not None

def check_data_flow():
    from src.policy.data_flow import DataFlowGraph
    g = DataFlowGraph()
    g.record("COPY", "Excel", entities=["PAN"])
    assert "verdict" in g.analyze()

def check_session_risk():
    from src.policy.session_risk import SessionRisk
    s = SessionRisk()
    s.record_event("COPY", "Excel", entities=["PAN"])
    assert s.score() > 0

def check_masking():
    from src.security.masking import mask_all
    assert "****" in mask_all("PAN ABCDE1234F")


def main():
    print("=" * 55)
    print("  SENTINEL DRISHTI - SYSTEM HEALTH")
    print("=" * 55)
    print()

    checks = [
        ("Python",          check_python),
        ("Dependencies",    check_deps),
        ("OCR",             check_ocr),
        ("Perception",      check_perception),
        ("Risk Engine",     check_risk),
        ("DLP Engine",      check_dlp),
        ("Audit Engine",    check_audit),
        ("Cache",           check_cache),
        ("CPU Backend",     check_cpu_backend),
        ("Data Flow",       check_data_flow),
        ("Session Risk",    check_session_risk),
        ("Masking",         check_masking),
    ]

    passed = 0
    failed = 0
    for name, fn in checks:
        n, status, err = check(name, fn)
        if status == "PASS":
            print("  " + n.ljust(18) + " " + status)
            passed += 1
        else:
            print("  " + n.ljust(18) + " " + status + "  <-- " + err)
            failed += 1

    print("  " + "QNN Backend".ljust(18) + " FALLBACK (no hardware)")
    print("  " + "Arduino".ljust(18) + " OPTIONAL (simulated)")
    print()
    print("=" * 55)
    if failed == 0:
        print("  Overall Status: READY")
    else:
        print("  Overall Status: DEGRADED (" + str(failed) + " failed)")
    print("  Passed: " + str(passed) + "/" + str(len(checks)))
    print("=" * 55)
    print()


if __name__ == "__main__":
    main()