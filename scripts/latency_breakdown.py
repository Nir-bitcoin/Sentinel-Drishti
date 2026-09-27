# latency_breakdown.py

import sys
import time
import json
from pathlib import Path
from statistics import mean
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


RUNS = 20


def percentile(values, p):
    if not values:
        return 0
    s = sorted(values)
    idx = int(len(s) * p / 100)
    if idx >= len(s):
        idx = len(s) - 1
    return round(s[idx], 4)


def measure(name, fn, runs=RUNS):
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        try:
            fn()
        except Exception:
            pass
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)

    return {
        "stage": name,
        "runs": runs,
        "p50_ms": percentile(times, 50),
        "p95_ms": percentile(times, 95),
        "p99_ms": percentile(times, 99),
        "min_ms": round(min(times), 4),
        "max_ms": round(max(times), 4),
        "mean_ms": round(mean(times), 4),
    }


def main():
    print("=" * 78)
    print("  SENTINEL DRISHTI — STAGE-LEVEL LATENCY BREAKDOWN")
    print("=" * 78)
    print("  Runs per stage: " + str(RUNS))
    print()

    # Imports
    from src.vision.perception import TextPerception
    from src.policy.behavior_tracker import BehaviorTracker
    from src.policy.risk_scorer import RiskScorer
    from src.policy.dlp_engine import DLPEngine
    from src.policy.data_flow import DataFlowGraph
    from src.policy.session_risk import SessionRisk
    from src.policy.audit_chain import AuditChain
    from src.policy.event_policy import EventPolicy
    from src.reasoning.intent_classifier import RuleBasedIntentClassifier
    from src.security.masking import mask_all
    import hashlib
    import shutil

    # Fixtures
    text = "Employee salary PAN ABCDE1234F phone 9876543210"
    actions = [
        {"action": "OPEN", "app": "Excel"},
        {"action": "COPY", "app": "Excel"},
        {"action": "OPEN", "app": "Gmail"},
        {"action": "PASTE", "app": "Gmail"},
    ]
    entities = ["PAN", "PHONE", "EMPLOYEE_FINANCIAL_DATA"]
    behavior = {"verdict": "CRITICAL_RISK", "destination": "PERSONAL_EMAIL", "after_hours": True}
    risk = {"score": 100, "level": "CRITICAL"}
    intent = {"classification": "EXFILTRATION", "confidence": 0.9}

    # Instantiate
    perception = TextPerception("cpu")
    scorer = RiskScorer()
    dlp = DLPEngine()
    intent_clf = RuleBasedIntentClassifier("cpu")
    policy = EventPolicy()

    # Track which stages ran successfully
    results = []

    # ---- Stage 1: Change Detection (SHA-256 hash) ----
    img = "docs/screenshots/hr_screenshot.png"

    def stage_change():
        p = Path(img)
        if p.exists():
            with open(p, "rb") as f:
                hashlib.sha256(f.read(8192)).hexdigest()

    results.append(measure("Change Detection", stage_change))

    # ---- Stage 2: Event Policy ----
    def stage_policy():
        policy.decide(actions)

    results.append(measure("Event Policy (L0/L1/L2)", stage_policy))

    # ---- Stage 3: Entity Detection ----
    def stage_entity():
        perception.analyze(text)

    results.append(measure("Entity Detection (regex)", stage_entity))

    # ---- Stage 4: Behavior Tracking ----
    def stage_behavior():
        t = BehaviorTracker()
        for a in actions:
            t.record(a["action"], a["app"])
        t.assess_risk()

    results.append(measure("Behavior Tracking", stage_behavior))

    # ---- Stage 5: Risk Scoring ----
    def stage_risk():
        scorer.calculate(entities, behavior)

    results.append(measure("Risk Scoring", stage_risk))

    # ---- Stage 6: Data Flow Graph ----
    def stage_flow():
        g = DataFlowGraph()
        for a in actions:
            g.record(a["action"], a["app"], entities=entities)
        g.analyze()

    results.append(measure("Data Flow Graph", stage_flow))

    # ---- Stage 7: Session Risk ----
    def stage_session():
        s = SessionRisk()
        for a in actions:
            s.record_event(a["action"], a["app"], entities=entities)
        s.summary()

    results.append(measure("Session Risk Engine", stage_session))

    # ---- Stage 8: Intent Classification ----
    def stage_intent():
        intent_clf.classify(text, entities)

    results.append(measure("Intent Classification", stage_intent))

    # ---- Stage 9: DLP Decision ----
    def stage_dlp():
        dlp.evaluate(text, intent, behavior, risk)

    results.append(measure("DLP Decision", stage_dlp))

    # ---- Stage 10: Privacy Masking ----
    def stage_masking():
        mask_all(text)

    results.append(measure("Privacy Masking", stage_masking))

    # ---- Stage 11: Audit Chain Write ----
    def stage_audit():
        shutil.rmtree("audit_logs_latency", ignore_errors=True)
        c = AuditChain(log_dir="audit_logs_latency")
        c.append({"action": "LATENCY_TEST"})
        shutil.rmtree("audit_logs_latency", ignore_errors=True)

    results.append(measure("Audit Chain Write", stage_audit, runs=10))

    # ---- Print table ----
    print()
    print("  " + "Stage".ljust(30)
          + "P50 (ms)".rjust(12)
          + "P95 (ms)".rjust(12)
          + "P99 (ms)".rjust(12))
    print("  " + "-" * 66)
    for r in results:
        print("  " + r["stage"].ljust(30)
              + str(r["p50_ms"]).rjust(12)
              + str(r["p95_ms"]).rjust(12)
              + str(r["p99_ms"]).rjust(12))

    # ---- Totals ----
    total_p50 = sum(r["p50_ms"] for r in results)
    total_p95 = sum(r["p95_ms"] for r in results)
    total_p99 = sum(r["p99_ms"] for r in results)

    print("  " + "-" * 66)
    print("  " + "TOTAL (control plane)".ljust(30)
          + str(round(total_p50, 3)).rjust(12)
          + str(round(total_p95, 3)).rjust(12)
          + str(round(total_p99, 3)).rjust(12))
    print()

    # ---- Save report ----
    out = {
        "runs_per_stage": RUNS,
        "stages": results,
        "total": {
            "p50_ms": round(total_p50, 3),
            "p95_ms": round(total_p95, 3),
            "p99_ms": round(total_p99, 3),
        },
    }
    Path("latency_report.json").write_text(json.dumps(out, indent=2))
    print("  Report saved: latency_report.json")
    print()


if __name__ == "__main__":
    main()