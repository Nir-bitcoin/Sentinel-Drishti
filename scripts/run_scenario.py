# run_scenario.py


import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from src.vision.perception import TextPerception
from src.policy.behavior_tracker import BehaviorTracker
from src.policy.risk_scorer import RiskScorer
from src.policy.dlp_engine import DLPEngine
from src.policy.data_flow import DataFlowGraph
from src.policy.session_risk import SessionRisk
from src.reasoning.intent_classifier import RuleBasedIntentClassifier


def load_scenario(path):
    if not HAS_YAML:
        raise RuntimeError("pyyaml required: pip install pyyaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_scenario(scenario):
    name = scenario.get("name", "(unnamed)")
    description = scenario.get("description", "")
    actions = scenario.get("actions", [])
    text = scenario.get("text", "")
    expected = scenario.get("expected", {})

    print("=" * 60)
    print("  " + name)
    if description:
        print("  " + description)
    print("=" * 60)
    print()

    perception = TextPerception("cpu")
    tracker = BehaviorTracker()
    scorer = RiskScorer()
    dlp = DLPEngine()
    intent_clf = RuleBasedIntentClassifier("cpu")
    flow = DataFlowGraph()
    session = SessionRisk()

    perc = perception.analyze(text)
    entities = perc.get("entities", [])

    for a in actions:
        flow.record(a["action"], a["app"], entities=entities)
        session.record_event(a["action"], a["app"], entities=entities)
        tracker.record(a["action"], a["app"])

    behavior = tracker.assess_risk()
    risk = scorer.calculate(entities, behavior)
    intent = intent_clf.classify(text, entities)
    decision = dlp.evaluate(text, intent, behavior, risk)
    flow_result = flow.analyze()

    print("  Entities:      " + str(entities))
    print("  Behavior:      " + behavior["verdict"])
    print("  Destination:   " + behavior.get("destination", "LOCAL"))
    print("  Risk:          " + str(risk["score"]) + "/100 (" + risk["level"] + ")")
    print("  Intent:        " + intent["classification"])
    print("  Data flow:     " + flow_result.get("verdict", "NO_FLOW"))
    print("  Session risk:  " + str(session.score()) + "/100")
    print("  Decision:      " + decision["decision"])
    print()

    failures = []
    if "entities" in expected and set(expected["entities"]) != set(entities):
        failures.append("entities: expected " + str(expected["entities"]) +
                        ", got " + str(entities))
    if "behavior" in expected and behavior["verdict"] != expected["behavior"]:
        failures.append("behavior: expected " + expected["behavior"] +
                        ", got " + behavior["verdict"])
    if "destination" in expected:
        got = behavior.get("destination", "LOCAL")
        if got != expected["destination"]:
            failures.append("destination: expected " + expected["destination"] +
                            ", got " + got)
    if "decision" in expected and decision["decision"] != expected["decision"]:
        failures.append("decision: expected " + expected["decision"] +
                        ", got " + decision["decision"])

    if failures:
        print("  RESULT: FAIL")
        for f in failures:
            print("    - " + f)
    else:
        print("  RESULT: PASS")
    print()
    return len(failures) == 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("scenario", nargs="?")
    p.add_argument("--all", action="store_true")
    args = p.parse_args()

    scenarios = []
    if args.all:
        d = Path("demo_scenarios")
        if not d.exists():
            print("demo_scenarios/ not found")
            return
        scenarios = sorted(d.glob("*.yaml"))
    elif args.scenario:
        scenarios = [Path(args.scenario)]
    else:
        print("Usage: python scripts/run_scenario.py <scenario.yaml>")
        print("       python scripts/run_scenario.py --all")
        return

    passed = 0
    total = 0
    for s in scenarios:
        total += 1
        try:
            if run_scenario(load_scenario(s)):
                passed += 1
        except Exception as e:
            print("  ERROR: " + str(s) + " -> " + str(e))
            print()

    print("=" * 60)
    print("  SCENARIOS: " + str(passed) + "/" + str(total) + " passed")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()