# benchmark_continuous.py

import sys
import time
import argparse
import shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vision.easyocr_screen import EasyOCRScreenAnalyzer
from src.policy.security_monitor import SecurityMonitor
from src.policy.dlp_engine import DLPEngine
from src.policy.behavior_tracker import BehaviorTracker
from src.policy.risk_scorer import RiskScorer


TEST_IMAGE = "docs/screenshots/hr_screenshot.png"
TOTAL_FRAMES = 100


def get_actions(frame):
    # 1-70: no security event -> L0
    if 1 <= frame <= 70:
        return []

    # 71-85: suspicious event -> L1
    if 71 <= frame <= 85:
        return [
            {"action": "OPEN", "app": "Excel"},
            {"action": "COPY", "app": "Excel"},
            {"action": "OPEN", "app": "Gmail"},
            {"action": "PASTE", "app": "Gmail"},
        ]

    # 86-100: critical event -> L2
    return [
        {"action": "OPEN", "app": "Excel"},
        {"action": "COPY", "app": "Excel"},
        {"action": "USB_INSERT", "app": "USB Drive"},
    ]


def percentile(values, p):
    if not values:
        return 0
    s = sorted(values)
    idx = int(len(s) * p / 100)
    if idx >= len(s):
        idx = len(s) - 1
    return s[idx]


def run_benchmark(mode, force_cache_clear=False):
    """mode: 'cold' | 'mixed' | 'cache'"""

    print("=" * 60)
    print("  SENTINEL DRISHTI - Continuous Benchmark [" + mode.upper() + "]")
    print("=" * 60)
    print()

    img = Path(TEST_IMAGE)
    if not img.exists():
        print("Test image not found: " + TEST_IMAGE)
        return

    # clear cache for cold mode
    if force_cache_clear:
        try:
            from src.vision import easyocr_screen
            easyocr_screen.cache_clear()
        except Exception:
            pass

    ocr = EasyOCRScreenAnalyzer(mode="cpu")
    dlp = DLPEngine()
    tracker = BehaviorTracker()
    risk = RiskScorer()

    monitor = SecurityMonitor(ocr, dlp, tracker, risk)

    # warmup - load model (this creates 1 cache entry)
    print("Warmup...")
    ocr.extract_text(TEST_IMAGE, use_cache=False)
    if mode == "cold" or force_cache_clear:
        try:
            from src.vision import easyocr_screen
            easyocr_screen.cache_clear()
        except Exception:
            pass
    print("Ready.")
    print()

    control_times = []
    l1_times = []
    l2_times = []
    security_times = []

    for frame in range(1, TOTAL_FRAMES + 1):
        actions = get_actions(frame)

        # cold mode: clear cache before each L1/L2 frame
        if mode == "cold" and actions:
            try:
                from src.vision import easyocr_screen
                easyocr_screen.cache_clear()
            except Exception:
                pass

        # cache mode: only run L1/L2 frames (skip L0)
        if mode == "cache" and not actions:
            continue

        t0 = time.time()
        result = monitor.process_frame(TEST_IMAGE, actions)
        elapsed = (time.time() - t0) * 1000

        if result["skipped"]:
            control_times.append(result["security_response_ms"])
        else:
            if result["level"] == 1:
                l1_times.append(elapsed)
            elif result["level"] == 2:
                l2_times.append(elapsed)
            security_times.append(result["security_response_ms"])

    stats = monitor.stats()
    policy = stats["policy"]

    print("-" * 60)
    print("Event Distribution")
    print("-" * 60)
    print("  Total frames:          " + str(stats["frames"]))
    print("  L0 (skip):             " + str(policy["level0"]))
    print("  L1 (fast OCR):         " + str(policy["level1"]))
    print("  L2 (precise OCR):      " + str(policy["level2"]))

    print()
    print("OCR Routing")
    print("-" * 60)
    print("  OCR skipped:           " + str(stats["skipped"]))
    print("  OCR calls (cold):      " + str(stats["ocr_calls"]))
    print("  Cache hits:            " + str(stats["cache_hits"]))
    print("  L1 calls:              " + str(stats["l1_calls"]))
    print("  L2 calls:              " + str(stats["l2_calls"]))

    print()
    print("Control Plane (L0 skip)")
    print("-" * 60)
    if control_times:
        print("  P50:  " + str(round(percentile(control_times, 50), 3)) + " ms")
        print("  P95:  " + str(round(percentile(control_times, 95), 3)) + " ms")

    print()
    print("L1 Fast OCR")
    print("-" * 60)
    if l1_times:
        print("  P50:  " + str(round(percentile(l1_times, 50), 2)) + " ms")
        print("  P95:  " + str(round(percentile(l1_times, 95), 2)) + " ms")

    print()
    print("L2 Precise OCR")
    print("-" * 60)
    if l2_times:
        print("  P50:  " + str(round(percentile(l2_times, 50), 2)) + " ms")
        print("  P95:  " + str(round(percentile(l2_times, 95), 2)) + " ms")

    print()
    print("Security Response (event -> DLP decision)")
    print("-" * 60)
    if security_times:
        print("  P50:  " + str(round(percentile(security_times, 50), 2)) + " ms")
        print("  P95:  " + str(round(percentile(security_times, 95), 2)) + " ms")

    print()
    print("-" * 60)
    print("Snapdragon reference (AI Hub component benchmarks):")
    print("  EasyOCR detector uint8:    13.5 ms  [job jgk4j29wp]")
    print("  EasyOCR recognizer uint8:  10.5 ms  [job jp1n3jw7g]")
    print()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cold", action="store_true", help="Force cache miss for every OCR call")
    p.add_argument("--mixed", action="store_true", help="Realistic mixed workload (default)")
    p.add_argument("--cache", action="store_true", help="Measure only cache hot-path")
    args = p.parse_args()

    if args.cold:
        run_benchmark("cold", force_cache_clear=True)
    elif args.cache:
        run_benchmark("cache", force_cache_clear=False)
    else:
        run_benchmark("mixed", force_cache_clear=False)


if __name__ == "__main__":
    main()

