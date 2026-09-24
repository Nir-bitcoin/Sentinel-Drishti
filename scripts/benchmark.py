# benchmark - CPU vs Snapdragon comparison
#
# soch ye thi - judges ko prove karna hai ki NPU zaroori hai
# CPU pe bahut slow chalta hai, NPU pe fast
#
# abhi Snapdragon laptop nahi hai, isliye NPU ki values
# Qualcomm AI Hub ke published benchmarks se li hain
#
# N - 26 sept

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vision.internvl_screen import InternVLScreenAnalyzer
from src.reasoning.qwen_intent import QwenIntentClassifier


# ek PII wala sample le rahe hain
TXT = ("Employee salary record: Name - Rajesh Kumar, "
       "PAN - ABCDE1234F, Phone - 9876543210, "
       "Bank Account - 123456789012")


def main():
    print("=" * 68)
    print("SENTINEL DRISHTI - CPU vs Snapdragon-targeted benchmark")
    print("=" * 68)
    print()
    print("Test: " + TXT[:50] + "...")
    print()

    # CPU wala real chalega
    print("CPU benchmark chal raha hai (measured)...")
    cpu_v = InternVLScreenAnalyzer("cpu").analyze(TXT)["latency_ms"]
    cpu_i = QwenIntentClassifier("cpu").classify(TXT, ["PAN", "PHONE"])["latency_ms"]

    # Snapdragon wala reference hai
    print("Snapdragon benchmark chal raha hai (reference)...")
    npu_v = InternVLScreenAnalyzer("snapdragon").analyze(TXT)["latency_ms"]
    npu_i = QwenIntentClassifier("snapdragon").classify(TXT, ["PAN", "PHONE"])["latency_ms"]

    cpu_tot = cpu_v + cpu_i
    npu_tot = npu_v + npu_i

    print()
    print("-" * 68)
    print("%-28s %12s %12s %10s" % ("Stage", "CPU(ms)", "NPU(ms)", "Speedup"))
    print("-" * 68)
    print("%-28s %12.1f %12.1f %9.1fx" % (
        "Perception", cpu_v, npu_v, cpu_v / npu_v))
    print("%-28s %12.1f %12.1f %9.1fx" % (
        "Reasoning (rule engine)", cpu_i, npu_i, cpu_i / npu_i))
    print("-" * 68)
    print("%-28s %12.1f %12.1f %9.1fx" % (
        "TOTAL", cpu_tot, npu_tot, cpu_tot / npu_tot))
    print()
    print("CPU:  measured on this laptop")
    print("NPU:  Qualcomm AI Hub benchmark reference")
    print("      (real hardware validation pending)")
    print()
    print("End-to-end reference latency: %.0f ms" % npu_tot)

    if npu_tot < 500:
        print("Target <500ms : PASS (reference)")
    else:
        print("Target <500ms : FAIL")

    print()


if __name__ == "__main__":
    main()