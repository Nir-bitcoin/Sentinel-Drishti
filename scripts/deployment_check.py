# deployment_check.py


import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def check(name, fn):
    try:
        fn()
        return (name, "PASS", "")
    except Exception as e:
        return (name, "FAIL", str(e)[:80])


def c_setup_files():
    for f in ["setup.ps1", "run.ps1", "sentinel.py"]:
        assert Path(f).exists(), f + " missing"

def c_config():
    assert Path("config/policy.yaml").exists()

def c_docs():
    for f in ["README.md", "docs/architecture.md", "docs/benchmark.md",
              "docs/security.md", "docs/snapdragon_validation.md"]:
        assert Path(f).exists(), f + " missing"

def c_ocr():
    from src.vision.easyocr_screen import EasyOCRScreenAnalyzer
    assert EasyOCRScreenAnalyzer("cpu") is not None

def c_backend():
    from src.backend.base import get_backend_with_fallback
    assert get_backend_with_fallback() is not None

def c_dlp():
    from src.policy.dlp_engine import DLPEngine
    DLPEngine()

def c_audit():
    import shutil
    from src.policy.audit_chain import AuditChain
    shutil.rmtree("audit_logs_deploy", ignore_errors=True)
    c = AuditChain(log_dir="audit_logs_deploy")
    c.append({"action": "DEPLOY"})
    valid, _ = c.verify_chain()
    assert valid
    shutil.rmtree("audit_logs_deploy", ignore_errors=True)

def c_data_flow():
    from src.policy.data_flow import DataFlowGraph
    g = DataFlowGraph()
    g.record("COPY", "Excel", entities=["PAN"])
    assert g.analyze()["verdict"]

def c_session_risk():
    from src.policy.session_risk import SessionRisk
    s = SessionRisk()
    s.record_event("COPY", "Excel", entities=["PAN"])
    assert s.score() > 0

def c_masking():
    from src.security.masking import mask_all
    assert "****" in mask_all("PAN ABCDE1234F")

def c_scenarios():
    yamls = list(Path("demo_scenarios").glob("*.yaml"))
    assert len(yamls) >= 3

def c_arduino():
    from src.action.arduino import ArduinoAlert
    a = ArduinoAlert()
    a.green()
    a.red()
    assert a.status()["mode"] in ("HARDWARE", "SOFTWARE")

def c_graceful():
    from src.backend.base import get_backend_with_fallback
    b = get_backend_with_fallback()
    assert getattr(b, "name", None)


def main():
    print("=" * 55)
    print("  DEPLOYMENT VALIDATION")
    print("=" * 55)
    print()

    checks = [
        ("Setup files",        c_setup_files),
        ("Config",             c_config),
        ("Docs",               c_docs),
        ("OCR",                c_ocr),
        ("Backend routing",    c_backend),
        ("DLP engine",         c_dlp),
        ("Audit chain",        c_audit),
        ("Data flow",          c_data_flow),
        ("Session risk",       c_session_risk),
        ("Masking",            c_masking),
        ("Demo scenarios",     c_scenarios),
        ("Arduino fallback",   c_arduino),
        ("Graceful fallback",  c_graceful),
    ]

    passed = 0
    failed = 0
    for name, fn in checks:
        n, status, err = check(name, fn)
        if status == "PASS":
            print("  " + n.ljust(20) + " " + status)
            passed += 1
        else:
            print("  " + n.ljust(20) + " " + status + "  -- " + err)
            failed += 1

    print()
    print("=" * 55)
    if failed == 0:
        print("  Deployment status: READY")
    else:
        print("  Deployment status: DEGRADED (" + str(failed) + ")")
    print("  " + str(passed) + "/" + str(len(checks)) + " checks passed")
    print("=" * 55)
    print()


if __name__ == "__main__":
    main()