# app.py
# Sentinel Drishti — Streamlit Dashboard

import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="Sentinel Drishti",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS — stylish polish
# ============================================================
st.markdown("""
<style>
/* ---------- HEADER ---------- */
.hero-head {
    text-align: center;
    padding: 8px 0 4px 0;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: -1px;
    line-height: 1.1;
    background: linear-gradient(135deg, #22c55e 0%, #0891b2 60%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 4px;
}
.hero-sub {
    color: #8896ab;
    font-size: 0.92rem;
    font-weight: 500;
    letter-spacing: 0.3px;
}
.hero-sub .name {
    color: #dbe7f5;
    font-weight: 700;
}

/* ---------- METRIC CARDS — softer ---------- */
div[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(34,197,94,0.06), rgba(8,145,178,0.03));
    border: 1px solid rgba(34,197,94,0.15);
    padding: 14px 16px;
    border-radius: 12px;
    transition: all 0.2s;
}
div[data-testid="stMetric"]:hover {
    border-color: rgba(34,197,94,0.35);
    transform: translateY(-1px);
}
div[data-testid="stMetricLabel"] {
    color: #91a4bd !important;
    font-size: 0.78rem !important;
}
div[data-testid="stMetricValue"] {
    color: #f5f8fc !important;
    font-weight: 750 !important;
    font-size: 1.35rem !important;
}

/* ---------- BORDERED CONTAINERS — glow ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px !important;
    border-color: rgba(34,197,94,0.12) !important;
}

/* ---------- BUTTONS ---------- */
.stButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 650;
    transition: all 0.15s;
}
.stButton > button:hover {
    transform: translateY(-1px);
}

/* ---------- EXPANDERS ---------- */
div[data-testid="stExpander"] {
    border-radius: 10px;
    border-color: rgba(255,255,255,0.08);
}

/* ---------- FOOTER ---------- */
.footer-card {
    text-align: center;
    padding: 22px 18px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(34,197,94,0.06), rgba(8,145,178,0.04));
    border: 1px solid rgba(34,197,94,0.15);
    margin-top: 10px;
}
.footer-team {
    font-size: 1.1rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.3px;
    margin-bottom: 4px;
}
.footer-team .accent {
    background: linear-gradient(135deg, #22c55e, #0891b2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.footer-sub {
    color: #8896ab;
    font-size: 0.82rem;
    margin-bottom: 14px;
}
.footer-links {
    font-size: 0.88rem;
    line-height: 2;
}
.footer-links a {
    color: #22c55e;
    text-decoration: none;
    font-weight: 600;
    margin: 0 8px;
    transition: color 0.15s;
}
.footer-links a:hover {
    color: #4ade80;
}

/* ---------- SECTION HEADINGS ---------- */
h5 {
    font-weight: 750 !important;
    letter-spacing: -0.2px;
}
</style>
""", unsafe_allow_html=True)


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
# HEADER — DRAGON STYLE
# ============================================================
st.markdown("""
<div class="hero-head">
    <div class="hero-title">🐉 Sentinel Drishti</div>
    <div class="hero-sub">
        On-Device AI Compliance & Data Loss Prevention · 
</div>
""", unsafe_allow_html=True)

st.write("")


# ============================================================
# MAIN LAYOUT
# ============================================================
left, right = st.columns([1, 1.4], gap="large")


# ------------------------------------------------------------
# LEFT
# ------------------------------------------------------------
with left:

    st.markdown("##### ⚙️ Runtime Backend")

    backend = st.radio(
        "Choose runtime target:",
        ["🎯 Snapdragon QNN / Hexagon HTP (target)", "💻 CPU (fallback)"],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("##### 🎯 Target Platform")
    with st.container(border=True):
        st.caption("**Runtime:** Snapdragon QNN / Hexagon HTP")
        st.caption("**Hardware:** Hexagon Tensor Processor (NPU)")
        st.caption("**Source:** Qualcomm AI Hub (hosted)")
        st.caption("**EasyOCR Detector:** 12.64 ms (w8a8)")
        st.caption("**EasyOCR Recognizer:** 10.55 ms (w8a8)")

    st.markdown("##### 📊 Key Metrics")
    with st.container(border=True):
        st.caption("**Target Backend:** QNN / NPU")
        st.caption("**Fallback:** CPU")
        st.caption("**Tests:** 62 / 62")
        st.caption("**F1 Score:** 1.00")
        st.caption("**Core Mode:** Offline")


# ------------------------------------------------------------
# RIGHT
# ------------------------------------------------------------
with right:

    st.markdown("##### 🎬 Scenario")

    with st.container(border=True):
        preset_name = st.selectbox("Choose a preset", list(PRESETS.keys()))
        preset = PRESETS[preset_name]

        custom_text = st.text_area(
            "Text on screen",
            value=preset["text"],
            height=100,
        )

        st.write("**Activity sequence:**")
        for a in preset["actions"]:
            st.markdown(f"- `{a['action']}` → {a['app']}")

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

    # RESULT — below scenario
    if st.session_state.history:
        r = st.session_state.history[0]
        decision = r["decision"]["decision"]

        st.markdown("##### 🔎 Result")

        with st.container(border=True):

            if decision == "BLOCK_AND_ALERT":
                st.error("🔴  **BLOCK AND ALERT** — sensitive data exfiltration prevented")
            elif decision == "WARN_AND_ALERT":
                st.warning("🟡  **WARN AND ALERT** — user confirmation required")
            else:
                st.success("🟢  **ALLOW** — action permitted by policy engine")

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Risk", f"{r['risk']['score']}/100")
            with m2:
                st.metric("Session Risk", f"{r['session']['session_risk_score']}/100")
            with m3:
                st.metric("Intent", r["intent"]["classification"])
            with m4:
                st.metric("Severity", r["decision"]["severity"])

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
                    st.markdown(f"**Verdict:** `{flow.get('verdict')}`")
                else:
                    st.info("No cross-application data flow detected.")

            with tab2:
                if r["entities"]:
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

                st.markdown("**Session context:**")
                st.json({
                    "actions": [f"{a['action']} → {a['app']}" for a in preset["actions"]],
                    "session_risk": r["session"]["session_risk_score"],
                })

            with tab4:
                st.markdown("**Decision reasoning:**")
                for line in r["decision"]["explanation"]:
                    st.markdown(f"- {line}")

                st.markdown("**Masked text (stored in audit):**")
                st.code(r["masked"], language=None)

                if r["decision"].get("enforcement"):
                    st.markdown("**Enforcement:**")
                    st.json(r["decision"]["enforcement"])
    else:
        st.caption("Run a scenario to see the decision.")


# ============================================================
# AUDIT LOG
# ============================================================
st.divider()
st.markdown("##### 📜 Session Audit Log")
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
# Q&A
# ============================================================
st.divider()
st.markdown("##### ❓ Q&A")

qa_col1, qa_col2 = st.columns(2)

with qa_col1:
    with st.expander("🟢 What is ALLOW?"):
        st.write("Safe action. No sensitive data, no risky behavior, or local/trusted destination.")
    with st.expander("🟡 What is WARN?"):
        st.write("Some risk detected. User confirmation required before proceeding.")
    with st.expander("🔴 What is BLOCK?"):
        st.write("Sensitive data being exfiltrated. Action prevented, physical alert fires.")

with qa_col2:
    with st.expander("Why is a preset showing ALLOW?"):
        st.write("Benign presets correctly return ALLOW. Choose **PII → Personal Gmail** to see BLOCK.")
    with st.expander("What is Session Risk?"):
        st.write("Accumulates across events. Single COPY = low. COPY → Gmail → PASTE = high.")
    with st.expander("Where is Snapdragon NPU used?"):
        st.write("Target is **Snapdragon QNN / Hexagon HTP**. This browser demo runs on CPU.")


# ============================================================
# TROUBLESHOOTING
# ============================================================
st.markdown("##### 🔧 Troubleshooting")

tr_col1, tr_col2 = st.columns(2)

with tr_col1:
    with st.expander("Data Flow: No flow detected?"):
        st.write("A data flow requires **COPY in App A → PASTE in App B**.")
    with st.expander("Cache / performance looks off?"):
        st.write("First run loads OCR (~5–10 s). Subsequent runs use cache (~3 ms).")

with tr_col2:
    with st.expander("Streamlit Cloud 'Oh no' error?"):
        st.write("Usually a memory limit (1 GB free tier). Try **⋮ → Reboot app**.")
    with st.expander("Pipeline error?"):
        st.write("Try a different preset. If it persists, check the repository issues page.")


# ============================================================
# FOOTER — TEAM
# ============================================================
st.divider()

st.markdown("""
<div class="footer-card">
    <div class="footer-team">
        <span class="accent">SusDetect</span> Team
    </div>
    <div class="footer-sub">
        by Niranjan Vishe · Snapdragon AI Lab Challenge 2026
    </div>
    <div class="footer-links">
        <a href="mailto:niranjanvishe62@gmail.com">📧 Email</a>
        <a href="https://www.linkedin.com/in/nirvishe/" target="_blank">💼 LinkedIn</a>
        <a href="https://github.com/Nir-bitcoin" target="_blank">🐙 GitHub</a>
        <a href="https://github.com/Nir-bitcoin/Sentinel-Drishti" target="_blank">📦 Repository</a>
    </div>
</div>
""", unsafe_allow_html=True)