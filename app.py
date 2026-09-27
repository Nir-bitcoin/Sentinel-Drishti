# app.py
# Sentinel Drishti — Streamlit Dashboard
# Clean, professional layout for judge presentation.

import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="Sentinel Drishti",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


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
# HERO — CENTERED
# ============================================================
st.markdown(
    "<h1 style='text-align:center; margin-bottom:0;'>🛡️ Sentinel Drishti</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#8896ab; font-size:1.05rem; margin-top:8px;'>"
    "On-Device AI Compliance & Data Loss Prevention Agent"
    "</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#8896ab; font-size:0.9rem;'>"
    "Snapdragon AI Lab Challenge 2026 · Solo submission by <b>Niranjan Vishe</b>"
    "</p>",
    unsafe_allow_html=True,
)

st.write("")


# ============================================================
# STATUS STRIP
# ============================================================
s1, s2, s3, s4, s5 = st.columns(5)
with s1:
    st.metric("Target Backend", "QNN / NPU")
with s2:
    st.metric("Fallback", "CPU")
with s3:
    st.metric("Tests", "62 / 62")
with s4:
    st.metric("F1 Score", "1.00")
with s5:
    st.metric("Core Mode", "Offline")

st.divider()


# ============================================================
# RUNTIME BACKEND
# ============================================================
st.subheader("⚙️ Runtime Backend")

backend = st.radio(
    "Choose runtime target:",
    ["🎯 Snapdragon QNN / Hexagon HTP (target)", "💻 CPU (fallback)"],
    index=0,
    horizontal=True,
    label_visibility="collapsed",
)

if backend.startswith("🎯"):
    st.success(
        "**Target runtime — Snapdragon QNN / Hexagon HTP**  \n"
        "EasyOCR components validated on hosted Snapdragon X Elite via Qualcomm AI Hub: "
        "**Detector 12.64 ms** · **Recognizer 10.55 ms** (w8a8).  \n"
        "Native runtime: `python sentinel.py --backend qnn`"
    )
else:
    st.info(
        "**Fallback runtime — CPU**  \n"
        "Development and validation environment. Native runtime auto-selects QNN "
        "when Snapdragon hardware is detected. Never silent."
    )

st.divider()


# ============================================================
# TWO COLUMNS — INFO / SCENARIO
# ============================================================
left, right = st.columns([1, 1.3], gap="large")


# ------------------------------------------------------------
# LEFT — INFORMATION
# ------------------------------------------------------------
with left:

    # TARGET
    st.subheader("🎯 Target Platform")
    with st.container(border=True):
        st.markdown("**Runtime:** Snapdragon QNN / Hexagon HTP")
        st.markdown("**Hardware:** Hexagon Tensor Processor (NPU)")
        st.markdown("**Benchmark source:** Qualcomm AI Hub (hosted)")
        st.markdown("")
        st.markdown("**EasyOCR on Snapdragon X Elite:**")
        st.markdown("- Detector — **12.64 ms** (w8a8)")
        st.markdown("- Recognizer — **10.55 ms** (w8a8)")
        st.markdown("")
        st.markdown("**Fallback:** CPU (dev / validation)")

    st.write("")

    # Q&A
    st.subheader("❓ Q&A")
    with st.container(border=True):
        with st.expander("🟢 What is ALLOW?"):
            st.write(
                "Safe action. No sensitive data, no risky behavior, "
                "or local/trusted destination."
            )
        with st.expander("🟡 What is WARN?"):
            st.write(
                "Some risk detected. User confirmation required before proceeding."
            )
        with st.expander("🔴 What is BLOCK?"):
            st.write(
                "Sensitive data being exfiltrated. Action prevented, "
                "physical alert fires."
            )
        with st.expander("Why is a preset showing ALLOW?"):
            st.write(
                "Benign presets correctly return ALLOW. Choose "
                "**PII → Personal Gmail** to see BLOCK."
            )
        with st.expander("What is Session Risk?"):
            st.write(
                "Accumulates across events. Single COPY = low. "
                "COPY → Gmail → PASTE = high."
            )

    st.write("")

    # TROUBLESHOOTING
    st.subheader("🔧 Troubleshooting")
    with st.container(border=True):
        with st.expander("Data Flow: No flow detected?"):
            st.write(
                "A data flow requires **COPY in App A → PASTE in App B**. "
                "Single-app actions stay local."
            )
        with st.expander("Cache / performance looks off?"):
            st.write(
                "First run loads OCR (~5–10 s on CPU). Subsequent runs use "
                "content-hash cache (~3 ms)."
            )
        with st.expander("Where is Snapdragon NPU used?"):
            st.write(
                "Target is **Snapdragon QNN / Hexagon HTP**. This browser "
                "demo runs the pipeline on CPU."
            )
        with st.expander("Streamlit Cloud 'Oh no' error?"):
            st.write(
                "Usually a memory limit (1 GB free tier). Try "
                "**⋮ → Reboot app** in Streamlit Cloud."
            )
        with st.expander("Pipeline error?"):
            st.write(
                "Try a different preset. If it persists, check the "
                "repository issues page."
            )


# ------------------------------------------------------------
# RIGHT — SCENARIO
# ------------------------------------------------------------
with right:

    st.subheader("🎬 Scenario")

    with st.container(border=True):
        preset_name = st.selectbox("Choose a preset", list(PRESETS.keys()))
        preset = PRESETS[preset_name]

        st.write("")

        custom_text = st.text_area(
            "Text on screen",
            value=preset["text"],
            height=100,
        )

        st.write("")
        st.markdown("**Activity sequence:**")
        for a in preset["actions"]:
            st.markdown(f"- `{a['action']}` → {a['app']}")

        st.write("")

        run_col, clear_col = st.columns(2)
        with run_col:
            run_btn = st.button(
                "▶  Run Pipeline",
                type="primary",
                use_container_width=True,
            )
        with clear_col:
            clear_btn = st.button(
                "🗑  Clear Session",
                use_container_width=True,
            )

        if clear_btn:
            st.session_state.history = []
            st.session_state.audit_entries = []
            st.rerun()

    # RUN
    if run_btn:
        with st.spinner("Running Sentinel Drishti pipeline..."):
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


# ============================================================
# RESULT — FULL WIDTH BELOW
# ============================================================
st.divider()
st.subheader("🔎 Security Decision")

if st.session_state.history:
    r = st.session_state.history[0]
    decision = r["decision"]["decision"]

    with st.container(border=True):

        # DECISION BANNER
        if decision == "BLOCK_AND_ALERT":
            st.error("🔴  **BLOCK AND ALERT** — sensitive data exfiltration prevented")
        elif decision == "WARN_AND_ALERT":
            st.warning("🟡  **WARN AND ALERT** — user confirmation required")
        else:
            st.success("🟢  **ALLOW** — action permitted by policy engine")

        st.write("")

        # METRICS
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Risk Score", f"{r['risk']['score']} / 100")
        with m2:
            st.metric("Session Risk", f"{r['session']['session_risk_score']} / 100")
        with m3:
            st.metric("Intent", r["intent"]["classification"])
        with m4:
            st.metric("Severity", r["decision"]["severity"])

        st.write("")

        # TABS
        tab1, tab2, tab3, tab4 = st.tabs(
            ["🔀 Data Flow", "🔍 Entities", "🧠 Behavior", "🔐 Evidence"]
        )

        with tab1:
            flow = r["flow"]
            if flow.get("flow_detected"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Source:** {flow.get('source')}")
                    st.markdown(f"**Transfer:** {flow.get('transfer')}")
                with c2:
                    st.markdown(f"**Destination:** {flow.get('destination')}")
                    st.markdown(f"**Class:** {flow.get('destination_class', '?')}")
                st.write("")
                st.markdown(f"**Verdict:** `{flow.get('verdict')}`")
            else:
                st.info("No cross-application data flow detected.")
                st.caption("A data flow requires COPY in one app and PASTE in another.")

        with tab2:
            if r["entities"]:
                st.markdown("**Detected entities:**")
                for e in r["entities"]:
                    st.markdown(f"- 🔒 **{e}**")
            else:
                st.success("No sensitive entities detected.")

        with tab3:
            b1, b2 = st.columns(2)
            with b1:
                st.metric("Behavior Verdict", str(r["behavior"]["verdict"]))
            with b2:
                st.metric("Destination", str(r["behavior"].get("destination", "LOCAL")))

            st.write("")
            st.markdown("**Session context:**")
            st.json({
                "actions": [f"{a['action']} → {a['app']}" for a in preset["actions"]],
                "session_risk": r["session"]["session_risk_score"],
            })

        with tab4:
            st.markdown("**Decision reasoning:**")
            for line in r["decision"]["explanation"]:
                st.markdown(f"- {line}")

            st.write("")
            st.markdown("**Masked text (stored in audit):**")
            st.code(r["masked"], language=None)

            if r["decision"].get("enforcement"):
                st.write("")
                st.markdown("**Enforcement:**")
                st.json(r["decision"]["enforcement"])

else:
    st.info("👆 Choose a preset above and click **▶ Run Pipeline** to see the decision.")


# ============================================================
# AUDIT LOG
# ============================================================
st.divider()
st.subheader("📜 Session Audit Log")
st.caption("Decision history for this browser session. Sensitive text is masked before storage.")

if st.session_state.audit_entries:
    st.dataframe(
        st.session_state.audit_entries,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "⬇ Download Audit JSON",
        data=json.dumps(st.session_state.audit_entries, indent=2),
        file_name="sentinel_audit_session.json",
        mime="application/json",
    )
else:
    st.caption("No audit entries yet. Run a scenario to populate the log.")


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.markdown(
    "<p style='text-align:center; color:#71859d; font-size:0.85rem;'>"
    "<b>Sentinel Drishti</b> · Snapdragon AI Lab Challenge 2026  <br>"
    "Browser dashboard for pipeline demonstration · "
    "Native OS monitoring: <code>python sentinel.py</code>"
    "</p>",
    unsafe_allow_html=True,
)