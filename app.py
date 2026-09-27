# app.py
# Sentinel Drishti — Streamlit Dashboard
# Uses the current pipeline (perception, behavior, risk, DLP, data flow, session risk).

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Sentinel Drishti",
    page_icon="🛡️",
    layout="wide",
)

# ---------- session state ----------
if "history" not in st.session_state:
    st.session_state.history = []
if "audit_entries" not in st.session_state:
    st.session_state.audit_entries = []

# ---------- lazy imports ----------
@st.cache_resource(show_spinner=False)
def load_pipeline():
    from src.vision.perception import TextPerception
    from src.policy.behavior_tracker import BehaviorTracker
    from src.policy.risk_scorer import RiskScorer
    from src.policy.dlp_engine import DLPEngine
    from src.policy.data_flow import DataFlowGraph
    from src.policy.session_risk import SessionRisk
    from src.reasoning.intent_classifier import RuleBasedIntentClassifier
    from src.security.masking import mask_all, summarize_entities

    return {
        "perception": TextPerception("cpu"),
        "tracker_cls": BehaviorTracker,
        "scorer": RiskScorer(),
        "dlp": DLPEngine(),
        "flow_cls": DataFlowGraph,
        "session_cls": SessionRisk,
        "intent_clf": RuleBasedIntentClassifier("cpu"),
        "mask_all": mask_all,
        "summarize_entities": summarize_entities,
    }


def run_scenario(actions, text):
    """Run one scenario through the full pipeline."""
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
    }


# ---------- presets ----------
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


# ---------- header ----------
st.title("🛡️ Sentinel Drishti")
st.caption("On-Device AI Compliance & Data Loss Prevention Agent for Snapdragon-Powered PCs")

# system status bar
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Backend", "CPU fallback")
with c2:
    st.metric("OCR", "Ready")
with c3:
    st.metric("Audit", "Valid")
with c4:
    st.metric("Network", "Offline core")

st.divider()

# ---------- layout ----------
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Scenario")
    preset_name = st.selectbox("Preset", list(PRESETS.keys()))
    preset = PRESETS[preset_name]

    custom_text = st.text_area("Text on screen", value=preset["text"], height=100)

    st.write("**Actions**")
    action_labels = []
    for a in preset["actions"]:
        action_labels.append(a["action"] + " → " + a["app"])
    st.write("\n".join("• " + x for x in action_labels))

    run_btn = st.button("▶ Run Pipeline", type="primary", use_container_width=True)
    clear_btn = st.button("🗑 Clear History", use_container_width=True)

    if clear_btn:
        st.session_state.history = []
        st.session_state.audit_entries = []
        st.rerun()

with col_right:
    st.subheader("Result")

    if run_btn:
        with st.spinner("Running pipeline..."):
            result = run_scenario(preset["actions"], custom_text)
            st.session_state.history.insert(0, result)

            # audit entry (masked)
            st.session_state.audit_entries.append({
                "ts": result["timestamp"],
                "decision": result["decision"]["decision"],
                "severity": result["decision"]["severity"],
                "rules": [m["rule_id"] for m in result["decision"]["matches"]],
                "risk": result["risk"]["score"],
                "masked": result["masked"][:120],
            })

    if st.session_state.history:
        r = st.session_state.history[0]

        # decision banner
        decision = r["decision"]["decision"]
        if decision == "BLOCK_AND_ALERT":
            st.error("🔴 BLOCK_AND_ALERT")
        elif decision == "WARN_AND_ALERT":
            st.warning("⚠️ WARN_AND_ALERT (user confirmation required)")
        else:
            st.success("🟢 ALLOW")

        # key metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Risk", str(r["risk"]["score"]) + "/100")
        m2.metric("Session Risk", str(r["session"]["session_risk_score"]) + "/100")
        m3.metric("Intent", r["intent"]["classification"])

        st.divider()

        # data flow
        st.markdown("**Data Flow**")
        flow = r["flow"]
        if flow.get("flow_detected"):
            st.write(
                "Source: **" + str(flow.get("source")) + "**  →  "
                + str(flow.get("transfer")) + "  →  "
                + "**" + str(flow.get("destination")) + "**"
                + "  (" + str(flow.get("destination_class", "?")) + ")"
            )
            st.write("Verdict: **" + str(flow.get("verdict")) + "**")
        else:
            st.write("No data flow detected.")

        # entities
        st.markdown("**Sensitive Entities**")
        if r["entities"]:
            for e in r["entities"]:
                st.write("• " + e)
        else:
            st.write("None")

        # behavior
        st.markdown("**Behavior**")
        st.write("Verdict: **" + r["behavior"]["verdict"] + "**")
        st.write("Destination: **" + r["behavior"].get("destination", "LOCAL") + "**")

        # evidence chain
        st.markdown("**Evidence Chain**")
        for line in r["decision"]["explanation"]:
            st.write("• " + line)

        # masked preview
        st.markdown("**Masked Text (as stored in audit)**")
        st.code(r["masked"], language=None)

        # enforcement
        if r["decision"].get("enforcement"):
            enf = r["decision"]["enforcement"]
            st.markdown("**Enforcement**")
            st.json(enf)
    else:
        st.info("Choose a preset and click **Run Pipeline**.")

# ---------- audit log ----------
st.divider()
st.subheader("Audit Log (this session)")
if st.session_state.audit_entries:
    st.dataframe(st.session_state.audit_entries, use_container_width=True)

    st.download_button(
        "⬇ Download audit JSON",
        data=json.dumps(st.session_state.audit_entries, indent=2),
        file_name="sentinel_audit_session.json",
        mime="application/json",
    )
else:
    st.write("No audit entries yet.")

# ---------- footer ----------
st.divider()
st.caption(
    "Browser demonstration of the perception and policy pipeline. "
    "Native OS-level monitoring is available in the local runtime "
    "(`python sentinel.py`)."
)