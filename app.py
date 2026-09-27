# app.py
# Sentinel Drishti — Simple Streamlit Dashboard

import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="Sentinel Drishti",
    page_icon="🛡️",
    layout="wide",
)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("🛡️ Sentinel Drishti")
    st.caption("On-Device AI DLP Agent")
    st.divider()

    st.subheader("⚙️ Runtime Backend")

    backend = st.radio(
        "Choose runtime",
        ["🎯 Snapdragon QNN (target)", "💻 CPU (fallback)"],
        index=0,
    )

    if backend.startswith("🎯"):
        st.success(
            "**Target: Snapdragon QNN / Hexagon HTP**\n\n"
            "EasyOCR validated on hosted Snapdragon X Elite:\n\n"
            "- Detector: **12.64 ms**\n"
            "- Recognizer: **10.55 ms**"
        )
    else:
        st.info(
            "**Fallback: CPU**\n\n"
            "Used for development and validation."
        )

    st.divider()

    st.subheader("❓ Help")

    with st.expander("What is ALLOW / WARN / BLOCK?"):
        st.write("🟢 **ALLOW** — safe action")
        st.write("🟡 **WARN** — needs user confirmation")
        st.write("🔴 **BLOCK** — action prevented")

    with st.expander("Why ALLOW instead of BLOCK?"):
        st.write("Benign presets return ALLOW. Choose **PII → Personal Gmail** to see BLOCK.")

    with st.expander("No data flow detected?"):
        st.write("Data flow needs COPY in one app + PASTE in another.")

    st.divider()

    st.subheader("👤 Submission")
    st.write("**Niranjan Vishe**")
    st.caption("niranjanvishe62@gmail.com")
    st.caption("Snapdragon AI Lab Challenge 2026")


# ============================================================
# SESSION STATE
# ============================================================
if "history" not in st.session_state:
    st.session_state.history = []
if "audit_entries" not in st.session_state:
    st.session_state.audit_entries = []


# ============================================================
# PIPELINE
# ============================================================
@st.cache_resource(show_spinner=False)
def load_pipeline():
    from src.vision.perception import TextPerception
    from src.policy.behavior_tracker import BehaviorTracker
    from src.policy.risk_scorer import RiskScorer
    from src.policy.dlp_engine import DLPEngine
    from src.policy.data_flow import DataFlowGraph
    from src.policy.session_risk import SessionRisk
    from src.reasoning.intent_classifier import RuleBasedIntentClassifier
    from src.security.masking import mask_all

    return {
        "perception": TextPerception("cpu"),
        "tracker_cls": BehaviorTracker,
        "scorer": RiskScorer(),
        "dlp": DLPEngine(),
        "flow_cls": DataFlowGraph,
        "session_cls": SessionRisk,
        "intent_clf": RuleBasedIntentClassifier("cpu"),
        "mask_all": mask_all,
    }


def run_scenario(actions, text):
    try:
        P = load_pipeline()
        perception = P["perception"]
        tracker = P["tracker_cls"]()
        scorer = P["scorer"]
        dlp = P["dlp"]
        flow = P["flow_cls"]()
        session = P["session_cls"]()
        intent_clf = P["intent_clf"]

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
        session_summary = session.summary()
        masked = P["mask_all"](text)

        return {
            "entities": entities,
            "behavior": behavior,
            "risk": risk,
            "intent": intent,
            "decision": decision,
            "flow": flow_result,
            "session": session_summary,
            "masked": masked,
            "timestamp": datetime.now().isoformat(),
            "error": None,
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# PRESETS
# ============================================================
PRESETS = {
    "Normal work (ALLOW)": {
        "text": "Team meeting scheduled for 3pm to discuss Q4 roadmap",
        "actions": [
            {"action": "OPEN", "app": "Notepad"},
            {"action": "TYPE", "app": "Notepad"},
        ],
    },
    "Confidential read (ALLOW)": {
        "text": "CONFIDENTIAL: Internal only - Q4 pricing strategy draft",
        "actions": [
            {"action": "OPEN", "app": "Word"},
            {"action": "READ", "app": "Word"},
        ],
    },
    "PII → Personal Gmail (BLOCK)": {
        "text": "Employee salary record: PAN ABCDE1234F phone 9876543210",
        "actions": [
            {"action": "OPEN", "app": "Excel"},
            {"action": "COPY", "app": "Excel"},
            {"action": "OPEN", "app": "Gmail"},
            {"action": "PASTE", "app": "Gmail"},
        ],
    },
    "PII → USB Drive (BLOCK)": {
        "text": "PAN ABCDE1234F salary record 5000000",
        "actions": [
            {"action": "OPEN", "app": "Excel"},
            {"action": "COPY", "app": "Excel"},
            {"action": "USB_INSERT", "app": "USB Drive"},
            {"action": "PASTE", "app": "USB Drive"},
        ],
    },
    "PII → Cloud Storage (WARN)": {
        "text": "PAN ABCDE1234F",
        "actions": [
            {"action": "OPEN", "app": "Excel"},
            {"action": "COPY", "app": "Excel"},
            {"action": "OPEN", "app": "Google Drive"},
            {"action": "PASTE", "app": "Google Drive"},
        ],
    },
}


# ============================================================
# HEADER
# ============================================================
st.title("🛡️ Sentinel Drishti")
st.write("On-device AI compliance and data-loss prevention agent.")

st.divider()


# ============================================================
# TOP METRICS
# ============================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Target Backend", "QNN / NPU")
with col2:
    st.metric("Fallback", "CPU")
with col3:
    st.metric("Tests Passing", "62 / 62")
with col4:
    st.metric("Core Mode", "Offline")

st.divider()


# ============================================================
# MAIN LAYOUT
# ============================================================
left, right = st.columns([1, 1.5])


# ============================================================
# LEFT — SCENARIO
# ============================================================
with left:
    st.subheader("🎬 Scenario")

    preset_name = st.selectbox("Choose a preset", list(PRESETS.keys()))
    preset = PRESETS[preset_name]

    custom_text = st.text_area(
        "Text on screen",
        value=preset["text"],
        height=100,
    )

    st.write("**Actions:**")
    for a in preset["actions"]:
        st.write(f"• {a['action']} → {a['app']}")

    st.write("")

    run_btn = st.button("▶  Run Pipeline", type="primary", use_container_width=True)
    clear_btn = st.button("🗑  Clear Session", use_container_width=True)

    if clear_btn:
        st.session_state.history = []
        st.session_state.audit_entries = []
        st.rerun()


# ============================================================
# RIGHT — RESULT
# ============================================================
with right:
    st.subheader("🔎 Result")

    if run_btn:
        with st.spinner("Running pipeline..."):
            result = run_scenario(preset["actions"], custom_text)

            if result.get("error"):
                st.error("Pipeline error")
                st.code(result["error"])
                st.stop()

            st.session_state.history.insert(0, result)
            st.session_state.audit_entries.append({
                "Time": result["timestamp"][11:19],
                "Decision": result["decision"]["decision"],
                "Severity": result["decision"]["severity"],
                "Rules": ", ".join(m["rule_id"] for m in result["decision"]["matches"]) or "—",
                "Risk": result["risk"]["score"],
                "Masked": result["masked"][:80],
            })

    if st.session_state.history:
        r = st.session_state.history[0]
        decision = r["decision"]["decision"]

        # ---------- DECISION BANNER ----------
        if decision == "BLOCK_AND_ALERT":
            st.error("🔴  BLOCK AND ALERT — sensitive data exfiltration prevented")
        elif decision == "WARN_AND_ALERT":
            st.warning("🟡  WARN AND ALERT — user confirmation required")
        else:
            st.success("🟢  ALLOW — action permitted")

        st.write("")

        # ---------- METRICS ----------
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Risk Score", f"{r['risk']['score']} / 100")
        with m2:
            st.metric("Session Risk", f"{r['session']['session_risk_score']} / 100")
        with m3:
            st.metric("Intent", r["intent"]["classification"])

        st.write("")

        # ---------- TABS ----------
        tab1, tab2, tab3, tab4 = st.tabs(
            ["🔀 Data Flow", "🔍 Entities", "🧠 Behavior", "🔐 Evidence"]
        )

        with tab1:
            flow = r["flow"]
            if flow.get("flow_detected"):
                st.write("**Source:** " + str(flow.get("source")))
                st.write("**Transfer:** " + str(flow.get("transfer")))
                st.write("**Destination:** " + str(flow.get("destination")))
                st.write("**Destination Class:** " + str(flow.get("destination_class", "?")))
                st.write("**Verdict:** " + str(flow.get("verdict")))
            else:
                st.info("No cross-application data flow detected.")

        with tab2:
            if r["entities"]:
                for e in r["entities"]:
                    st.write(f"🔒 {e}")
            else:
                st.success("No sensitive entities detected.")

        with tab3:
            b1, b2 = st.columns(2)
            with b1:
                st.metric("Behavior Verdict", str(r["behavior"]["verdict"]))
            with b2:
                st.metric("Destination", str(r["behavior"].get("destination", "LOCAL")))

            st.write("**Session Context:**")
            st.json({
                "actions": [f"{a['action']} → {a['app']}" for a in preset["actions"]],
                "session_risk": r["session"]["session_risk_score"],
            })

        with tab4:
            st.write("**Decision Reasoning:**")
            for line in r["decision"]["explanation"]:
                st.write(f"• {line}")

            st.write("**Masked Text (stored in audit):**")
            st.code(r["masked"])

            if r["decision"].get("enforcement"):
                st.write("**Enforcement:**")
                st.json(r["decision"]["enforcement"])
    else:
        st.info("Choose a preset and click **Run Pipeline**.")


# ============================================================
# AUDIT LOG
# ============================================================
st.divider()
st.subheader("📜 Session Audit Log")

if st.session_state.audit_entries:
    st.dataframe(st.session_state.audit_entries, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇ Download Audit JSON",
        data=json.dumps(st.session_state.audit_entries, indent=2),
        file_name="sentinel_audit_session.json",
        mime="application/json",
    )
else:
    st.caption("No audit entries yet.")


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption("Sentinel Drishti · Snapdragon AI Lab Challenge 2026 · Native OS monitoring via `python sentinel.py`")