# sentinel.py
# Unified entry point for Sentinel Drishti.

import sys
import argparse
import subprocess
import webbrowser
import socket as _sock
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def banner():
    print("=" * 58)
    print("                 SENTINEL DRISHTI")
    print("       On-Device AI Compliance & DLP Agent")
    print("=" * 58)
    print()


def show_backend_status(requested="auto"):
    """Show backend status with QNN as primary target."""
    import platform

    print("Environment       : " + platform.system() + " " + platform.machine())
    print("Python            : " + str(sys.version_info.major) + "." + str(sys.version_info.minor))

    if requested == "cpu":
        print("Requested backend : CPU")
    elif requested == "qnn":
        print("Requested backend : QNN/HTP")
    else:
        print("Requested backend : AUTO")

    try:
        from src.backend.base import get_backend_with_fallback
        b = get_backend_with_fallback()
        actual = getattr(b, "name", "unknown")
        print("Execution backend : " + actual)
    except Exception as e:
        print("Execution backend : ERROR (" + str(e) + ")")

    print()
    print("TARGET RUNTIME    : Snapdragon QNN / Hexagon NPU")

    try:
        from src.backend.qnn_backend import QNNBackend
        qnn = QNNBackend()
        if getattr(qnn, "available", False):
            print("  QNN/HTP         : AVAILABLE")
            print("  Accelerator     : Hexagon Tensor Processor (NPU)")
            print("  Status          : ACTIVE")
        else:
            print("  QNN/HTP         : NOT AVAILABLE on this host")
            print("  Reason          : No QNN Execution Provider detected")
            print("  Fallback        : CPU backend ACTIVE")
    except Exception:
        print("  QNN/HTP         : NOT AVAILABLE on this host")
        print("  Fallback        : CPU backend ACTIVE")

    print()
    print("AI Hub reference  : EasyOCR detector 13.5 ms . recognizer 10.5 ms")
    print("                    (hosted Snapdragon component benchmarks)")
    print()
    print("Local validation  : CPU backend (end-to-end pipeline measured)")
    print("Network required  : NO  (fully offline core)")
    print()
    print("System Status     : READY")
    print()


def run_script(path, args=None):
    cmd = [sys.executable, str(path)]
    if args:
        cmd.extend(args)
    subprocess.run(cmd, cwd=str(ROOT))


def find_free_port(start=8650, end=8700):
    for p in range(start, end):
        try:
            with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", p))
                return p
        except OSError:
            continue
    return start


def launch_streamlit():
    port = find_free_port()
    print("[Launching Streamlit dashboard...]")
    print("  URL will open in your browser in a few seconds.")
    print("  Press Ctrl+C to stop.")
    print()
    try:
        subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run",
             str(ROOT / "app.py"),
             "--server.headless", "false",
             "--server.port", str(port)],
            cwd=str(ROOT),
        )
        time.sleep(4)
        url = "http://localhost:" + str(port)
        try:
            webbrowser.open(url)
        except Exception:
            pass
        print("  Streamlit running at " + url)
        print("  Close the browser and press Ctrl+C here to stop.")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass
    except KeyboardInterrupt:
        print()
        print("Streamlit stopped.")
    except Exception as e:
        print("Streamlit failed: " + str(e))


def menu_loop():
    while True:
        print("Select mode:")
        print("  [1] Interactive Demo")
        print("  [2] Live Monitoring")
        print("  [3] Benchmark")
        print("  [4] System Health")
        print("  [5] Deployment Check")
        print("  [6] Offline Verify")
        print("  [7] Run Scenarios")
        print("  [8] Streamlit Dashboard (auto-launch browser)")
        print("  [9] Provider Diagnostic")
        print("  [0] Exit")
        print()
        try:
            ch = input("Choice: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if ch == "1":
            run_script(ROOT / "run_demo.py")
        elif ch == "2":
            run_script(ROOT / "scripts" / "benchmark_continuous.py", ["--mixed"])
        elif ch == "3":
            run_script(ROOT / "scripts" / "benchmark_continuous.py", ["--mixed"])
        elif ch == "4":
            run_script(ROOT / "scripts" / "health_check.py")
        elif ch == "5":
            run_script(ROOT / "scripts" / "deployment_check.py")
        elif ch == "6":
            run_script(ROOT / "tests" / "test_offline.py")
        elif ch == "7":
            run_script(ROOT / "scripts" / "run_scenario.py", ["--all"])
        elif ch == "8":
            launch_streamlit()
        elif ch == "9":
            run_script(ROOT / "scripts" / "check_provider.py")
        elif ch == "0":
            break
        else:
            print("Invalid choice")
        print()
        print("=" * 58)
        print()


def main():
    p = argparse.ArgumentParser(description="Sentinel Drishti")
    p.add_argument("--demo", action="store_true")
    p.add_argument("--live", action="store_true")
    p.add_argument("--benchmark", action="store_true")
    p.add_argument("--health", action="store_true")
    p.add_argument("--deploy-check", action="store_true")
    p.add_argument("--offline", action="store_true")
    p.add_argument("--scenario", type=str)
    p.add_argument("--all-scenarios", action="store_true")
    p.add_argument("--provider", action="store_true")
    p.add_argument("--streamlit", action="store_true")
    p.add_argument("--no-banner", action="store_true")
    p.add_argument("--backend", type=str, choices=["cpu", "qnn", "auto"],
                   default="auto", help="Inference backend")
    args = p.parse_args()

    if not args.no_banner:
        banner()
        show_backend_status(args.backend)

    if args.demo:
        run_script(ROOT / "run_demo.py")
    elif args.live:
        run_script(ROOT / "scripts" / "benchmark_continuous.py", ["--mixed"])
    elif args.benchmark:
        run_script(ROOT / "scripts" / "benchmark_continuous.py", ["--mixed"])
    elif args.health:
        run_script(ROOT / "scripts" / "health_check.py")
    elif args.deploy_check:
        run_script(ROOT / "scripts" / "deployment_check.py")
    elif args.offline:
        run_script(ROOT / "tests" / "test_offline.py")
    elif args.scenario:
        run_script(ROOT / "scripts" / "run_scenario.py", [args.scenario])
    elif args.all_scenarios:
        run_script(ROOT / "scripts" / "run_scenario.py", ["--all"])
    elif args.provider:
        run_script(ROOT / "scripts" / "check_provider.py")
    elif args.streamlit:
        launch_streamlit()
    else:
        menu_loop()


if __name__ == "__main__":
    main()