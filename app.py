# app.py
#
# Streamlit dashboard for Sentinel Drishti.
# Preset scenarios + image upload + telemetry bar.


import streamlit as st
import json
import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.vision.internvl_screen import InternVLScreenAnalyzer
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

st.info(
    "**DEMO MODE** — Text scenarios run fully. "
    "Endpoint actions (clipboard, USB interception, screen monitoring) "
    "are simulated in this browser demo."
)

with st.sidebar:
    st.header("Settings")

    mode = st.radio(
        "Backend:",
        ["snapdragon", "cpu"],
        format_func=lambda x: "Snapdragon-targeted" if x == "snapdragon" else "CPU (measured)"
    )

    if mode == "snapdragon":
        st.info("NPU values = Qualcomm AI Hub references. Hardware validation pending.")
    else:
        st.success("CPU execution — real, measured.")

    st.divider()
    st.subheader("About")
    st.caption(
        "Sentinel Drishti detects sensitive content, tracks user behavior, "
        "and blocks suspicious data transfer — all locally, no cloud."
    )

# ---- telemetry bar ----
st.divider()
tcol1, tcol2, tcol3, tcol4 = st.columns(4)
with tcol1:
    st.metric("Backend", "NPU" if mode == "snapdragon" else "CPU")
with tcol2:
    st.metric("Mode", "Target" if mode == "snapdragon" else "Local")
with tcol3:
    st.metric("Offline", "Active")
with tcol4:
    st.metric("Detection", "Enabled")
st.divider()


# ---- image upload ----
with st.expander("Upload Image (EasyOCR — local only)"):
    uploaded = st.file_uploader("Choose a screenshot", type=["png", "jpg", "jpeg"])

    if uploaded is not None:
        tmp_dir = Path("docs/screenshots")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = tmp_dir / "_uploaded.png"
        with open(tmp_path, "wb") as f:
            f.write(uploaded.getbuffer())

        st.success("Image uploaded: " + str(tmp_path))

        try:
            from src.vision.easyocr_screen import EasyOCRScreenAnalyzer
            ocr = EasyOCRScreenAnalyzer(mode)
            result = ocr.extract_text(str(tmp_path))

            st.write("**OCR status:** " + result["status"])
            st.write("**Confidence:** " + str(result["avg_confidence"]))
            st.write("**Text:** " + result["text"][:200])
        except Exception as e:
            st.warning("EasyOCR not available in this deployment: " + str(e))


# ---- preset scenarios ----
scenarios = {
    "Normal Work": {
        "content": "Team meeting scheduled for 3pm to discuss Q4 roadmap",
        "actions": [
            {"action": "OPEN", "app": "Notepad"},
            {"action": "TYPE", "app": "Notepad"},
            {"action": "SAVE", "app": "Notepad"},
        ],
        "desc": "Employee opens notes and types — benign activity.",
    },
    "PII → Personal Gmail": {
        "content": "Employee salary record: Name - Rajesh Kumar, PAN - ABCDE1234F, Phone - 9876543210",
        "actions": [
            {"action": "OPEN", "app": "Excel"},
            {"action": "COPY", "app": "Excel"},
            {"action": "OPEN", "app": "Gmail"},
            {"action": "PASTE", "app": "Gmail"},
        ],
        "desc": "Employee copies PII and pastes to personal Gmail — exfiltration.",
    },
    "PII → USB": {
        "content": "Employee salary record: PAN - ABCDE1234F, Phone - 9876543210",
        "actions": [
            {"action": "OPEN", "app": "Excel"},
            {"action": "COPY", "app": "Excel"},
            {"action": "INSERT", "app": "USB Drive"},
            {"action": "PASTE", "app": "USB Drive"},
        ],
        "desc": "Employee copies sensitive data to USB drive.",
    },
    "Confidential Read": {
        "content": "CONFIDENTIAL: Internal only - Q4 pricing strategy draft",
        "actions": [
            {"action": "OPEN", "app": "Word"},
            {"action": "READ", "app": "Word"},
        ],
        "desc": "Employee reads confidential doc locally — allowed with log.",
    },
}

st.subheader("Choose a Scenario")
st.caption("Click a scenario button to run the full pipeline instantly.")

cols = st.columns(4)
selected = None
for i, name in enumerate(scenarios.keys()):
    with cols[i]:
        if st.button(name, use_container_width=True):
            selected = name

with st.expander("Or enter custom content"):
    custom_content = st.text_area("Screen content:", height=80)
    if custom_content:
        selected = "Custom"
        scenarios["Custom"] = {
            "content": custom_content,
            "actions": [
                {"action": "OPEN", "app": "Excel"},
                {"action": "COPY", "app": "Excel"},
                {"action": "OPEN", "app": "Gmail"},
                {"action": "PASTE", "app": "Gmail"},
            ],
            "desc": "Custom input",
        }


if selected:
    sc = scenarios[selected]

    st.divider()
    st.subheader("Pipeline: " + selected)
    st.caption(sc["desc"])

    with st.spinner("Running pipeline..."):
        vis = InternVLScreenAnalyzer(mode)
        rea = QwenIntentClassifier(mode)
        trk = BehaviorTracker()
        scr = RiskScorer()
        dlp = DLPEngine()

        v = vis.analyze(sc["content"])
        for a in sc["actions"]:
            trk.record(a["action"], a["app"])
        b = trk.assess_risk()
        r = scr.calculate(v["entities"], b)
        i = rea.classify(sc["content"], v["entities"])
        d = dlp.evaluate(sc["content"], i, b, r)

    stage1, stage2, stage3, stage4 = st.columns(4)
    with stage1:
        st.metric("OCR / Input", "TEXT", "loaded")
    with stage2:
        st.metric("Entities", str(len(v["entities"])), "detected")
    with stage3:
        st.metric("Risk", str(r["score"]) + "/100", r["level"])
    with stage4:
        icon = "🚫" if d["triggered"] else "✅"
        st.metric("Decision", icon + " " + d["action"])

    st.divider()
    if d["triggered"]:
        st.error("🚫 BLOCKED")
    else:
        st.success("✅ ALLOWED")

    st.subheader("Why this decision?")
    for line in d["explanation"]:
        st.write("✓ " + line)

    tab1, tab2, tab3, tab4 = st.tabs(["Entities", "Behavior", "Risk Detail", "Alerts"])

    with tab1:
        st.write("**Detected entities:**")
        if v["entities"]:
            for e in v["entities"]:
                st.code(e)
        else:
            st.write("None")

    with tab2:
        st.write("**Behavior sequence:**")
        for a in sc["actions"]:
            st.write("• " + a["action"] + " on " + a["app"])
        st.write("**Verdict:** " + b["verdict"])
        st.write("**Destination:** " + b.get("destination", "LOCAL"))

    with tab3:
        st.write("**Risk breakdown:**")
        for x in r["reasons"]:
            st.write("• " + x)

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

    st.divider()
    st.subheader("Audit Report")

    audit = {
        "event_id": "SD-" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "scenario": selected,
        "mode": mode,
        "entities": v["entities"],
        "behavior_verdict": b["verdict"],
        "destination": b.get("destination", "LOCAL"),
        "risk_score": r["score"],
        "risk_level": r["level"],
        "action": d["action"],
        "explanation": d["explanation"],
    }

    st.code(json.dumps(audit, indent=2), language="json")

    st.download_button(
        label="Download Audit Report (JSON)",
        data=json.dumps(audit, indent=2),
        file_name=audit["event_id"] + ".json",
        mime="application/json",
    )

st.divider()
st.caption(
    "GitHub: https://github.com/Nir-bitcoin/Sentinel-Drishti  |  "
    "Automated tests: https://github.com/Nir-bitcoin/Sentinel-Drishti/actions"
)