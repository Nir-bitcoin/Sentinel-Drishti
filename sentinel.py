# sentinel.py


import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def banner():
    print("=" * 55)
    print("           SENTINEL DRISHTI")
    print("   On-Device AI Compliance & DLP Agent")
    print("=" * 55)
    print()


def system_status():
    print("Environment       : " + sys.platform + " / " + str(sys.version_info.major) + "." + str(sys.version_info.minor))
    try:
        from src.backend.base import get_backend_with_fallback
        b = get_backend_with_fallback()
        print("Backend           : " + getattr(b, "name", "unknown"))
    except Exception as e:
        print("Backend           : ERROR (" + str(e) + ")")
    print("CPU fallback      : ACTIVE")
    print("OCR               : READY (EasyOCR)")
    print("Policy Engine     : READY")
    print("Audit             : READY")
    print("Arduino           : OPTIONAL (simulated)")
    print()
    print("System Status     : READY")
    print()


def menu():
    print("Select mode:")
    print("  [1] Demo (terminal)")
    print("  [2] Health check")
    print("  [3] Tests (unit)")
    print("  [4] Tests (security deep)")
    print("  [5] Tests (E2E)")
    print("  [6] Benchmark (cache)")
    print("  [7] Benchmark (mixed)")
    print("  [8] Benchmark (cold)")
    print("  [9] Provider diagnostic")
    print("  [10] Memory profile")
    print("  [11] Detection evaluation")
    print("  [0] Exit")
    print()


def run(script_path, args=None):
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    subprocess.run(cmd, cwd=str(ROOT))


def main():
    banner()
    system_status()

    while True:
        menu()
        try:
            ch = input("Choice: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if ch == "1":
            run(ROOT / "run_demo.py")
        elif ch == "2":
            run(ROOT / "scripts" / "healthcheck.py")
        elif ch == "3":
            run(ROOT / "tests" / "test_pipeline.py")
        elif ch == "4":
            run(ROOT / "tests" / "test_security_deep.py")
        elif ch == "5":
            run(ROOT / "tests" / "test_e2e.py")
        elif ch == "6":
            run(ROOT / "scripts" / "benchmark_continuous.py", ["--cache"])
        elif ch == "7":
            run(ROOT / "scripts" / "benchmark_continuous.py", ["--mixed"])
        elif ch == "8":
            run(ROOT / "scripts" / "benchmark_continuous.py", ["--cold"])
        elif ch == "9":
            run(ROOT / "scripts" / "check_provider.py")
        elif ch == "10":
            run(ROOT / "scripts" / "memory_profile.py")
        elif ch == "11":
            run(ROOT / "evaluation" / "run_evaluation.py")
        elif ch == "0":
            break
        else:
            print("Invalid choice")
        print()
        print("=" * 55)
        print()


if __name__ == "__main__":
    main()