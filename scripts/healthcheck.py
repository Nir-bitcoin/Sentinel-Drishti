# healthcheck.py
#
# Quick health check for Sentinel Drishti.


import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def check(name, fn):
    try:
        fn()
        print("  " + name.ljust(20) + " OK")
        return True
    except Exception as e:
        print("  " + name.ljust(20) + " FAIL: " + str(e))
        return False


def check_python():
    assert sys.version_info >= (3, 10)

def check_deps():
    import numpy
    import PIL

def check_ocr_module():
    from src.vision.easyocr_screen import EasyOCRScreenAnalyzer

def check_perception():
    from src.vision.perception import TextPerception
    a = TextPerception("cpu")
    assert a is not None

def check_dlp():
    from src.policy.dlp_engine import DLPEngine
    d = DLPEngine()
    assert d is not None

def check_audit():
    from src.policy.audit_chain import AuditChain
    import shutil
    c = AuditChain(log_dir="audit_logs_healthcheck")
    c.append({"action": "HEALTHCHECK"})
    valid, _ = c.verify_chain()
    assert valid == True
    shutil.rmtree("audit_logs_healthcheck", ignore_errors=True)

def check_provider():
    from src.backend.base import get_backend_with_fallback
    b = get_backend_with_fallback()
    assert b is not None


def main():
    print("=" * 50)
    print("  SENTINEL DRISHTI - Health Check")
    print("=" * 50)
    print()

    results = [
        check("Python", check_python),
        check("Dependencies", check_deps),
        check("OCR module", check_ocr_module),
        check("Perception", check_perception),
        check("DLP engine", check_dlp),
        check("Audit chain", check_audit),
        check("Provider", check_provider),
    ]

    print()
    passed = sum(1 for r in results if r)
    print("  Total: " + str(passed) + "/" + str(len(results)) + " passed")
    print()


if __name__ == "__main__":
    main()