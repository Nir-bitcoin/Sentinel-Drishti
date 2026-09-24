# routes.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import FastAPI
from pydantic import BaseModel

from src.vision.screen_capture import ScreenCapture
from src.vision.internvl_screen import InternVLScreenAnalyzer
from src.reasoning.qwen_intent import QwenIntentClassifier
from src.policy.dlp_engine import DLPEngine
from src.policy.behavior_tracker import BehaviorTracker
from src.policy.risk_scorer import RiskScorer
from simulation.simulated_arduino import SimulatedArduino


app = FastAPI(title="Sentinel Drishti")

# init once
capture = ScreenCapture()
vision = InternVLScreenAnalyzer(True)
reason = QwenIntentClassifier(True)
tracker = BehaviorTracker()
scorer = RiskScorer()
dlp = DLPEngine()
arduino = SimulatedArduino()


class ScreenRequest(BaseModel):
    screen_text: str
    app: str = "Unknown"
    actions: list = []


@app.get("/")
def root():
    return {"service": "Sentinel Drishti", "status": "ok"}


@app.post("/analyze")
def analyze(req: ScreenRequest):
    # Stage 1
    c = capture.capture_text(req.screen_text, req.app)

    # Stage 2
    vr = vision.analyze(c["content"])

    # Stage 3
    for act in req.actions:
        tracker.record(act.get("action", "OPEN"), act.get("app", "Unknown"))
    beh = tracker.assess_risk()

    # Stage 4
    risk = scorer.calculate(vr["entities"], beh)

    # Stage 5
    ir = reason.classify(c["content"], vr["entities"])

    # Stage 6
    dr = dlp.evaluate(c["content"], ir, beh, risk)

    # Stage 7
    if dr["triggered"]:
        arduino.trigger_alert(dr["severity"])
    else:
        arduino.reset()

    return {
        "capture": c,
        "vision": vr,
        "behavior": beh,
        "risk": risk,
        "intent": ir,
        "dlp": dr,
        "arduino": {"led": arduino.led, "buzzer": arduino.buzzer}
    }