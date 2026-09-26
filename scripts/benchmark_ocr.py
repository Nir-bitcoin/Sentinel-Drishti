# benchmark_ocr.py

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vision.easyocr_screen import EasyOCRScreenAnalyzer


TEST_IMAGE = "docs/screenshots/hr_screenshot.png"
RUNS = 10


def percentile(values, p):
    s = sorted(values)
    idx = int(len(s) * p / 100)
    if idx >= len(s):
        idx = len(s) - 1
    return s[idx]


def main():
    print("=" * 60)
    print("  SENTINEL DRISHTI - OCR Benchmark")
    print("=" * 60)
    print()

    img = Path(TEST_IMAGE)
    if not img.exists():
        print("Test image not found: " + TEST_IMAGE)
        return

    print("Test image: " + TEST_IMAGE)
    print("Runs:       " + str(RUNS))
    print()

    # warmup (load model)
    print("Warmup...")
    a = EasyOCRScreenAnalyzer(mode="cpu")
    a.extract_text(TEST_IMAGE, use_cache=False)
    print()

    # benchmark runs (no cache)
    times = []
    confidences = []

    for i in range(RUNS):
        r = a.extract_text(TEST_IMAGE, use_cache=False)
        ms = r["inference_ms"]
        times.append(ms)
        confidences.append(r["avg_confidence"])
        print("Run " + str(i + 1).rjust(2) + ": " + str(ms).rjust(9) + " ms   conf=" + str(r["avg_confidence"]))

    print()
    print("-" * 60)
    print("OCR Statistics (two-stage pipeline)")
    print("  Min:     " + str(round(min(times), 2)) + " ms")
    print("  P50:     " + str(round(percentile(times, 50), 2)) + " ms")
    print("  P95:     " + str(round(percentile(times, 95), 2)) + " ms")
    print("  Max:     " + str(round(max(times), 2)) + " ms")
    print()
    print("  Avg confidence: " + str(round(sum(confidences) / len(confidences), 3)))
    print()

    # cache test
    print("-" * 60)
    print("Cache test (2nd read of same image):")
    t0 = time.time()
    r2 = a.extract_text(TEST_IMAGE, use_cache=True)
    cache_ms = round((time.time() - t0) * 1000, 2)
    print("  Cache hit:  " + str(r2["cache_hit"]))
    print("  Lookup:     " + str(cache_ms) + " ms")

    print()
    print("-" * 60)
    print("Snapdragon reference (AI Hub component benchmarks):")
    print("  EasyOCR detector uint8:    13.5 ms  [job jgk4j29wp]")
    print("  EasyOCR recognizer uint8:  10.5 ms  [job jp1n3jw7g]")
    print()


if __name__ == "__main__":
    main()