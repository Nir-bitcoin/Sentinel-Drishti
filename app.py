
import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.vision.internvl_screen import InternVLScreenAnalyzer
from src.vision.easyocr_screen import EasyOCRScreenAnalyzer
from src.reasoning.qwen_intent import QwenIntentClassifier
from src.reasoning.translator import AlertTranslator
from src.policy.dlp_engine import DLPEngine
from src.policy.behavior_tracker import BehaviorTracker
from src.policy.risk_scorer import RiskScorer


st.set_page_config(
    page_title="Sentinel Drishti",
    page_icon="🛡",
    layout="wide"
)

st.title("🛡 Sentinel Drishti")
st.caption("On-Device AI Compliance & Data Loss Prevention")
st.caption("Snapdragon AI Lab Build & Present Challenge 2026")

with st.sidebar:
    st.header("Mode")
    mode = st.radio(
        "Backend:",
        ["snapdragon", "cpu"],
        format_func=lambda x: "Snapdragon-targeted" if x == "snapdragon" else "CPU (measured)"
    )

    if mode == "snapdragon":
        st.info("NPU values are Qualcomm AI Hub references. Hardware validation pending.")
    else:
        st.success("CPU execution - real, measured.")

    st.divider()
    st.caption("Test scenarios:")
    scenario = st.selectbox(
        "Choose input",
        ["PII text", "Image (EasyOCR)", "Confidential doc", "USB copy"]
    )

if scenario == "PII text":
    content = "Employee salary record: Name - Rajesh Kumar, PAN - ABCDE1234F, Phone - 9876543210"
    image_mode = False
    actions = [
        {"action": "OPEN", "app": "Excel"},
        {"action": "COPY", "app": "Excel"},
        {"action": "OPEN", "app": "Gmail"},
        {"action": "PASTE", "app": "Gmail"},
    ]
elif scenario == "Image (EasyOCR)":
    content = "docs/screenshots/hr_screenshot.png"
    image_mode = True
    actions = [
        {"action": "OPEN", "app": "Excel"},
        {"action": "COPY", "app": "Excel"},
        {"action": "OPEN", "app": "Gmail"},
        {"action": "PASTE", "app": "Gmail"},
    ]
elif scenario == "Confidential doc":
    content = "CONFIDENTIAL: Internal only - Q4 pricing strategy draft"
    image_mode = False
    actions = [
        {"action": "OPEN", "app": "Word"},
        {"action": "READ", "app": "Word"},
    ]
else:
    content = "Employee salary record: PAN - ABCDE1234F, Phone - 9876543210"
    image_mode = False
    actions = [
        {"action": "OPEN", "app": "Excel"},
        {"action": "COPY", "app": "Excel"},
        {"action": "INSERT", "app": "USB Drive"},
        {"action": "PASTE", "app": "USB Drive"},
    ]

if not image_mode:
    content = st.text_area("Screen content:", value=content, height=100)
else:
    st.write("**Image:** " + content)

st.write("**Behavior sequence:**")
for a in actions:
    st.write("- " + a["action"] + " on " + a["app"])

if st.button("Run Analysis", type="primary"):
    with st.spinner("Running pipeline..."):
        if image_mode:
            ocr = EasyOCRScreenAnalyzer(mode)
            o = ocr.extract_text(content)
            text_content = o["text"]
        else:
            text_content = content
            o = None

        vis = InternVLScreenAnalyzer(mode)
        rea = QwenIntentClassifier(mode)
        trk = BehaviorTracker()
        scr = RiskScorer()
        dlp = DLPEngine()

        v = vis.analyze(text_content)
        for a in actions:
            trk.record(a["action"], a["app"])
        b = trk.assess_risk()
        r = scr.calculate(v["entities"], b)
        i = rea.classify(text_content, v["entities"])
        d = dlp.evaluate(text_content, i, b, r)

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Risk Score", str(r["score"]) + "/100", r["level"])
    with col2:
        icon = "🔴" if d["triggered"] else "🟢"
        st.metric("Action", icon + " " + d["action"])
    with col3:
        if d.get("enforcement"):
            st.metric("Enforcement", "SIMULATED")

    if o:
        st.subheader("OCR (EasyOCR)")
        st.write("Status: " + o["status"])
        st.write("Confidence: " + str(o["avg_confidence"]))
        st.write("Image size: " + o["image_size"])
        st.write("Passes: " + str(o["passes_used"]))
        st.write("Inference: " + str(o["inference_ms"]) + " ms [CPU]")
        st.write("Snapdragon reference: ~39.5 ms detector + ~19.3 ms recognizer")

    tab1, tab2, tab3, tab4 = st.tabs(["Perception", "Behavior", "Risk", "Alerts"])

    with tab1:
        st.write("**Entities:**")
        for e in v["entities"]:
            st.code(e)

    with tab2:
        st.write("Verdict: **" + b["verdict"] + "**")
        st.write("Destination: " + b.get("destination", "LOCAL"))
        st.write("Reason: " + b["reason"])

    with tab3:
        st.write("**Risk breakdown:**")
        for x in r["reasons"]:
            st.write("- " + x)

    with tab4:
        if d.get("enforcement"):
            e = d["enforcement"]
            st.write("**Blocked:** " + e["blocked_action"])
            trans = AlertTranslator()
            msg = d["action"] + " - " + e["blocked_action"]
            st.write("**EN:** " + msg)
            st.write("**HI:** " + trans.translate(msg, "hi")["text"])
            st.write("**MR:** " + trans.translate(msg, "mr")["text"])
            st.write("**TA:** " + trans.translate(msg, "ta")["text"])
            st.write("**TE:** " + trans.translate(msg, "te")["text"])
        else:
            st.write("No alert triggered.")

    st.subheader("Explanation")
    for line in d["explanation"]:
        st.write("• " + line)

st.divider()
st.caption("GitHub: https://github.com/Nir-bitcoin/Sentinel-Drishti")