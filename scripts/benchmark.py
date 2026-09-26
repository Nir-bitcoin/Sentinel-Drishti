# benchmark.py
#
# Real benchmark - runs pipeline 5 times and reports stats.

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vision.perception import TextPerception
from src.policy.behavior_tracker import BehaviorTracker
from src.policy.risk_scorer import RiskScorer
from src.policy.dlp_engine import DLPEngine
from src.reasoning.intent_classifier import RuleBasedIntentClassifier


TEST_TEXT = (
    "Employee salary record: Name - Rajesh Kumar, "
    "PAN - ABCDE1234F, Phone - 9876543210"
)


def run_pipeline_once(mode):
    vis = TextPerception(mode)
    rea = RuleBasedIntentClassifier(mode)
    trk = BehaviorTracker()
    scr = RiskScorer()
    dlp = DLPEngine()

    v = vis.analyze(TEST_TEXT)
    trk.record("OPEN", "Excel")
    trk.record("COPY", "Excel")
    trk.record("OPEN", "Gmail")
    trk.record("PASTE", "Gmail")
    b = trk.assess_risk()
    r = scr.calculate(v["entities"], b)
    i = rea.classify(TEST_TEXT, v["entities"])
    d = dlp.evaluate(TEST_TEXT, i, b, r)
    return d["action"]


def main():
    print("=" * 60)
    print("  SENTINEL DRISHTI - Pipeline Benchmark")
    print("=" * 60)
    print()
    print("Test: " + TEST_TEXT[:50] + "...")
    print()

    run_pipeline_once("cpu")

    runs = []
    for n in range(5):
        t0 = time.time()
        action = run_pipeline_once("cpu")
        ms = round((time.time() - t0) * 1000, 2)
        runs.append(ms)
        print("Run " + str(n + 1) + ": " + str(ms) + " ms   [action=" + action + "]")

    runs_sorted = sorted(runs)
    print()
    print("-" * 60)
    print("Statistics (pipeline-only, no OCR):")
    print("  Min:    " + str(min(runs)) + " ms")
    print("  Median: " + str(runs_sorted[2]) + " ms")
    print("  Max:    " + str(max(runs)) + " ms")
    print()
    print("Note: This measures the regex + rule engine + DLP pipeline.")
    print("EasyOCR inference (~7.1-7.4 s on CPU) is measured separately.")
    print()
    print("Qualcomm AI Hub references (hosted Snapdragon X Elite):")
    print("  EasyOCR detector:   ~39.5 ms  [job jpxlmx3jp]")
    print("  EasyOCR recognizer: ~19.3 ms  [job jprl9wnvp]")
    print()


if __name__ == "__main__":
    main()