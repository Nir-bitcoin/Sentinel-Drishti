# test_e2e.py


import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vision.perception import TextPerception
from src.policy.behavior_tracker import BehaviorTracker
from src.policy.risk_scorer import RiskScorer
from src.policy.dlp_engine import DLPEngine
from src.reasoning.intent_classifier import RuleBasedIntentClassifier


def test_pii_exfiltration_pipeline():
    perception = TextPerception("cpu")
    tracker = BehaviorTracker()
    scorer = RiskScorer()
    dlp = DLPEngine()
    intent_clf = RuleBasedIntentClassifier("cpu")

    text = "Employee salary PAN ABCDE1234F phone 9876543210"
    perc = perception.analyze(text)
    entities = perc["entities"]
    assert "PAN" in entities

    tracker.record("OPEN", "Excel")
    tracker.record("COPY", "Excel")
    tracker.record("OPEN", "Gmail")
    tracker.record("PASTE", "Gmail")
    behavior = tracker.assess_risk()
    assert behavior["verdict"] == "CRITICAL_RISK"

    risk = scorer.calculate(entities, behavior)
    assert risk["score"] >= 70

    intent = intent_clf.classify(text, entities)
    assert intent["classification"] in ["EXFILTRATION", "CONFIDENTIAL_DATA_ACCESS"]

    decision = dlp.evaluate(text, intent, behavior, risk)
    assert decision["triggered"] == True


def test_benign_pipeline_allows():
    perception = TextPerception("cpu")
    tracker = BehaviorTracker()
    scorer = RiskScorer()
    dlp = DLPEngine()
    intent_clf = RuleBasedIntentClassifier("cpu")

    text = "team meeting at 3pm"
    perc = perception.analyze(text)
    entities = perc["entities"]

    tracker.record("OPEN", "Notepad")
    tracker.record("TYPE", "Notepad")
    behavior = tracker.assess_risk()

    risk = scorer.calculate(entities, behavior)
    intent = intent_clf.classify(text, entities)
    decision = dlp.evaluate(text, intent, behavior, risk)

    assert decision["triggered"] == False


def test_usb_exfiltration_pipeline():
    perception = TextPerception("cpu")
    tracker = BehaviorTracker()
    scorer = RiskScorer()
    dlp = DLPEngine()
    intent_clf = RuleBasedIntentClassifier("cpu")

    text = "PAN ABCDE1234F salary record 5000000"
    perc = perception.analyze(text)
    entities = perc["entities"]

    tracker.record("OPEN", "Excel")
    tracker.record("COPY", "Excel")
    tracker.record("USB_INSERT", "USB")
    tracker.record("PASTE", "USB")
    behavior = tracker.assess_risk()
    assert behavior["verdict"] == "CRITICAL_RISK"

    risk = scorer.calculate(entities, behavior)
    intent = intent_clf.classify(text, entities)
    decision = dlp.evaluate(text, intent, behavior, risk)

    assert decision["triggered"] == True


def test_confidential_read_local_allows():
    perception = TextPerception("cpu")
    tracker = BehaviorTracker()
    scorer = RiskScorer()
    dlp = DLPEngine()
    intent_clf = RuleBasedIntentClassifier("cpu")

    text = "CONFIDENTIAL internal only"
    perc = perception.analyze(text)
    entities = perc["entities"]

    tracker.record("OPEN", "Notepad")
    tracker.record("TYPE", "Notepad")
    behavior = tracker.assess_risk()

    risk = scorer.calculate(entities, behavior)
    intent = intent_clf.classify(text, entities)
    decision = dlp.evaluate(text, intent, behavior, risk)

    assert decision["triggered"] == False


if __name__ == "__main__":
    tests = [
        test_pii_exfiltration_pipeline,
        test_benign_pipeline_allows,
        test_usb_exfiltration_pipeline,
        test_confidential_read_local_allows,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print("PASS: " + t.__name__)
            passed += 1
        except Exception as e:
            print("FAIL: " + t.__name__ + " -> " + str(e))
    print()
    print("Total: " + str(passed) + "/" + str(len(tests)) + " passing")