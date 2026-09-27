# app.py
# Sentinel Drishti — Streamlit Dashboard
# All values, names, and metrics fully visible.

import streamlit as st
import json
import html
import textwrap
from datetime import datetime

st.set_page_config(
    page_title="Sentinel Drishti",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS — larger, fully-visible values
# ============================================================
st.markdown(textwrap.dedent("""
<style>
.stApp {
    background: #07111f;
    color: #e8eef7;
}
.main .block-container {
    max-width: 1600px;
    padding-top: 1.5rem;
}
section[data-testid="stSidebar"] {
    background: #081321;
    border-right: 1px solid rgba(255,255,255,0.08);
    min-width: 340px !important;
    max-width: 340px !important;
}
section[data-testid="stSidebar"] > div {
    padding: 1rem 1.2rem;
}

/* ---------- METRICS — bigger, no truncation ---------- */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    padding: 18px 16px;
    border-radius: 14px;
    overflow: visible !important;
}
div[data-testid="stMetricLabel"] {
    color: #91a4bd !important;
    font-size: 0.85rem !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}
div[data-testid="stMetricValue"] {
    color: #f5f8fc !important;
    font-weight: 750 !important;
    font-size: 1.5rem !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    word-break: break-word !important;
    line-height: 1.2 !important;
}
div[data-testid="stMetricDelta"] {
    white-space: normal !important;
}

/* ---------- BUTTONS ---------- */
.stButton > button {
    border-radius: 10px;
    min-height: 46px;
    font-weight: 650;
    font-size: 0.95rem;
}

/* ---------- EXPANDERS ---------- */
div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
}
div[data-testid="stExpander"] summary {
    font-size: 0.9rem !important;
    padding: 10px 12px !important;
}
div[data-testid="stExpander"] p,
div[data-testid="stExpander"] li {
    font-size: 0.9rem !important;
    line-height: 1.55 !important;
}

/* ---------- HERO ---------- */
.hero {
    padding: 28px 32px;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(20,45,78,0.95), rgba(15,28,50,0.94));
    border: 1px solid rgba(255,255,255,0.10);
    margin-bottom: 22px;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 10px;
    color: #ffffff;
    line-height: 1.15;
}
.hero-subtitle {
    color: #a9bbd1;
    font-size: 1.02rem;
    line-height: 1.6;
    max-width: 1000px;
}
.hero-badges {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 18px;
}
.badge {
    padding: 7px 14px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 650;
    border: 1px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.055);
    color: #dbe7f5;
    white-space: nowrap;
}

/* ---------- DECISION CARD ---------- */
.decision {
    padding: 22px 24px;
    border-radius: 16px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.10);
}
.decision-block {
    background: rgba(220,38,38,0.14);
    border-color: rgba(248,113,113,0.40);
}
.decision-warn {
    background: rgba(234,179,8,0.14);
    border-color: rgba(250,204,21,0.40);
}
.decision-allow {
    background: rgba(34,197,94,0.14);
    border-color: rgba(74,222,128,0.35);
}
.decision-main {
    font-size: 1.45rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.25;
}
.decision-sub {
    font-size: 0.95rem;
    margin-top: 8px;
    color: #c0cfe0;
    line-height: 1.55;
}

/* ---------- FLOW BOX ---------- */
.flow-box {
    padding: 18px 20px;
    background: rgba(59,130,246,0.09);
    border: 1px solid rgba(96,165,250,0.22);
    border-radius: 12px;
    margin-top: 10px;
}
.flow-line {
    font-size: 1.05rem;
    font-weight: 650;
    color: #dce9f8;
    line-height: 1.6;
    word-break: break-word;
}
.flow-verdict {
    margin-top: 10px;
    color: #b3c2d4;
    font-size: 0.92rem;
}

/* ---------- INFO BOXES ---------- */
.stAlert p {
    font-size: 0.92rem !important;
    line-height: 1.55 !important;
}

/* ---------- FOOTER ---------- */
.footer {
    text-align: center;
    color: #8fa4bd;
    font-size: 0.85rem;
    padding: 16px;
    line-height: 1.6;
}

/* ---------- SIDEBAR HEADINGS ---------- */
section[data-testid="stSidebar"] h1 {
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    margin-bottom: 2px !important;
}
section[data-testid="stSidebar"] h2 {
    font-size: 1.05rem !important;
    font-weight: 750 !important;
    margin-top: 4px !important;
    margin-bottom: 8px !important;
}
section[data-testid="stSidebar"] h3 {
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    margin-top: 6px !important;
    margin-bottom: 8px !important;
}
section[data-testid="stSidebar"] label {
    font-size: 0.9rem !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.92rem !important;
    padding: 6px 0 !important;
}

/* ---------- TEXTAREA / SELECTBOX ---------- */
textarea, input, div[data-baseweb="select"] {
    font-size: 0.94rem !important;
}
</style>
"""), unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("# 🛡️ Sentinel Drishti")
    st.caption("On-Device AI DLP Agent")
    st.divider()

    # ---------- BACKEND ----------
    st.subheader("⚙️ Runtime Backend")

    backend = st.radio(
        "Runtime target",
        options=["🎯 Snapdragon QNN (target)", "💻 CPU (fallback)"],
        index=0,
        label_visibility="collapsed",
    )

    if backend.startswith("🎯"):
        st.info(
            "**Target runtime**\n\n"
            "Snapdragon QNN / Hexagon HTP\n\n"
            "EasyOCR validated on hosted Snapdragon X Elite:\n\n"
            "• Detector — **12.64 ms**\n\n"
            "• Recognizer — **10.55 ms**\n\n"
            "Native: `python sentinel.py --backend qnn`"
        )
    else:
        st.warning(
            "**Fallback runtime**\n\n"
            "CPU — used for development and validation.\n\n"
            "Native runtime auto-selects QNN when Snapdragon hardware is detected."
        )

    st.divider()

    # ---------- Q&A ----------
    st.subheader("❓ Q&A / Help")

    with st.expander("🟢 What is ALLOW?"):
        st.write("Safe action. No sensitive data, no risky behavior, or local/trusted destination.")

    with st.expander("🟡 What is WARN?"):
        st.write("Some risk detected. User confirmation required before proceeding.")

    with st.expander("🔴 What is BLOCK?"):
        st.write("Sensitive data being exfiltrated. Action prevented, physical alert fires.")

    with st.expander("Why preset showing ALLOW?"):
        st.write("Benign presets correctly return ALLOW. Choose **PII → Personal Gmail** to see BLOCK.")

    with st.expander("Data Flow: No flow detected?"):
        st.write("A data flow requires **COPY in App A → PASTE in App B**.")

    with st.expander("Cache / performance?"):
        st.write("First run loads OCR (~5–10 s). Subsequent runs use cache (~3 ms).")

    with st.expander("Where is Snapdragon NPU used?"):
        st.write("Target: **Snapdragon QNN / Hexagon HTP**. This browser demo runs on CPU.")

    with st.expander("Session Risk meaning?"):
        st.write("Accumulates across events. Single COPY = low. COPY → Gmail → PASTE = high.")

    st.divider()

    # ---------- LEGEND ----------
    st.subheader("📖 Legend")
    st.markdown(
        "🔴 **BLOCK** — action prevented  \n"
        "🟡 **WARN** — user confirmation  \n"
        "🟢 **ALLOW** — action permitted  \n"
        "🔀 **FLOW** — cross-app transfer  \n"
        "📊 **RISK** — 0 to 100"
    )

    st.divider()

    # ---------- TEAM ----------
    st.subheader("👤 Submission")
    st.markdown("**Solo submission**")
    st.markdown("**Niranjan Vishe**")
    st.caption("niranjanvishe62@gmail.com")
    st.caption("Snapdragon AI Lab Challenge 2026")

    st.divider()

    # ---------- LINKS ----------
    st.subheader("🔗 Links")
    st.markdown(
        "[📦 Source code](https://github.com/Nir-bitcoin/Sentinel-Drishti)  \n"
        "[📚 Documentation](https://github.com/Nir-bitcoin/Sentinel-Drishti/tree/main/docs)  \n"
        "[🌐 Showcase](https://huggingface.co/spaces/kuchvo/Sentinel-Drishti)"
    )


# ============================================================
# SESSION STATE
# ============================================================
if "history" not in st.session_state:
    st.session_state.history = []
if "audit_entries" not in st.session_state:
    st.session_state.audit_entries = []


# ============================================================
# PIPELINE — LAZY LOAD
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


# ============================================================
# ERROR HELPER
# ============================================================
def _get_user_hint(error_text):
    e = error_text.lower()
    if "memory" in e or "out of memory" in e:
        return "🛑 Memory limit reached. Try **⋮ → Reboot app** in Streamlit Cloud."
    if "no module named" in e or "modulenotfound" in e:
        return "📦 Missing module. Wait 1–2 min and refresh."
    if "file not found" in e or "filenotfound" in e:
        return "📁 File not found. Try rebooting the app."
    if "timeout" in e:
        return "⏱️ Timeout. Wait and try again (first run: 5–10 s)."
    if "opencv" in e or "libgl" in e:
        return "🖼️ OpenCV GUI library missing. Cloud needs `opencv-python-headless`."
    return "⚠️ Unexpected error. Try a different preset."


# ============================================================
# RUN SCENARIO
# ============================================================
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

        for action in actions:
            flow.record(action["action"], action["app"], entities=entities)
            session.record_event(action["action"], action["app"], entities=entities)
            tracker.record(action["action"], action["app"])

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
        return {
            "error": str(e),
            "user_hint": _get_user_hint(str(e)),
        }


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
# HERO HEADER
# ============================================================
st.markdown(textwrap.dedent("""
<div class="hero">
    <div class="hero-title">🛡️ Sentinel Drishti</div>
    <div class="hero-subtitle">
        On-device AI compliance and data-loss prevention for enterprise endpoints.
        The pipeline combines perception, behavior tracking, session risk,
        data-flow analysis, and policy enforcement before sensitive data leaves
        the device.
    </div>
    <div class="hero-badges">
        <span class="badge">⚡ Event-driven AI</span>
        <span class="badge">🔒 Offline Core</span>
        <span class="badge">🧠 Snapdragon QNN Target</span>
        <span class="badge">✅ 62/62 Tests</span>
        <span class="badge">📊 F1 1.00</span>
    </div>
</div>
"""), unsafe_allow_html=True)


# ============================================================
# TOP METRICS
# ============================================================
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("🎯 Target Backend", "QNN / NPU")
with c2:
    st.metric("💻 Fallback", "CPU")
with c3:
    st.metric("✅ Tests Passing", "62 / 62")
with c4:
    st.metric("🔒 Core Mode", "Offline")


# ============================================================
# MAIN LAYOUT
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)

col_left, col_right = st.columns([0.9, 1.6], gap="large")


# ============================================================
# LEFT — SCENARIO
# ============================================================
with col_left:
    st.subheader("🎬 Scenario")

    preset_name = st.selectbox("Preset", list(PRESETS.keys()))
    preset = PRESETS[preset_name]

    custom_text = st.text_area(
        "Text on screen",
        value=preset["text"],
        height=110,
    )

    st.markdown("**Activity sequence**")
    for a in preset["actions"]:
        st.markdown(f"• `{a['action']}` → {a['app']}")

    st.markdown("<br>", unsafe_allow_html=True)

    run_btn = st.button(
        "▶  Run Security Pipeline",
        type="primary",
        use_container_width=True,
    )

    clear_btn = st.button(
        "🗑  Clear Session",
        use_container_width=True,
    )

    if clear_btn:
        st.session_state.history = []
        st.session_state.audit_entries = []
        st.rerun()


# ============================================================
# RIGHT — RESULT
# ============================================================
with col_right:
    st.subheader("🔎 Security Decision")

    if run_btn:
        with st.spinner("Running Sentinel Drishti pipeline..."):
            result = run_scenario(preset["actions"], custom_text)

            if result.get("error"):
                st.error("🔴 Pipeline error occurred")
                st.write("**What happened:**")
                st.code(result["error"], language=None)
                st.write("**What to do:**")
                st.info(result.get("user_hint", "Try again or reboot the app."))
                st.stop()

            st.session_state.history.insert(0, result)
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
        decision = r["decision"]["decision"]

        # ---------- DECISION CARD ----------
        if decision == "BLOCK_AND_ALERT":
            st.markdown(textwrap.dedent("""
            <div class="decision decision-block">
                <div class="decision-main">🔴 BLOCK AND ALERT</div>
                <div class="decision-sub">
                    Sensitive data transfer identified as a critical exfiltration event.
                </div>
            </div>
            """), unsafe_allow_html=True)
        elif decision == "WARN_AND_ALERT":
            st.markdown(textwrap.dedent("""
            <div class="decision decision-warn">
                <div class="decision-main">🟡 WARN AND ALERT</div>
                <div class="decision-sub">
                    Risk detected. User confirmation required before proceeding.
                </div>
            </div>
            """), unsafe_allow_html=True)
        else:
            st.markdown(textwrap.dedent("""
            <div class="decision decision-allow">
                <div class="decision-main">🟢 ALLOW</div>
                <div class="decision-sub">
                    The current action is permitted by the policy engine.
                </div>
            </div>
            """), unsafe_allow_html=True)

        # ---------- METRICS ----------
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("📊 Risk Score", f"{r['risk']['score']}/100")
        with m2:
            st.metric("🧠 Session Risk", f"{r['session']['session_risk_score']}/100")
        with m3:
            st.metric("🎯 Intent", r["intent"]["classification"])

        st.markdown("<br>", unsafe_allow_html=True)

        # ---------- TABS ----------
        tab_flow, tab_entities, tab_behavior, tab_evidence = st.tabs(
            ["🔀 Data Flow", "🔍 Entities", "🧠 Behavior", "🔐 Evidence"]
        )

        with tab_flow:
            flow = r["flow"]
            if flow.get("flow_detected"):
                src = html.escape(str(flow.get("source")))
                tr = html.escape(str(flow.get("transfer")))
                dst = html.escape(str(flow.get("destination")))
                dst_class = html.escape(str(flow.get("destination_class", "?")))
                verdict = html.escape(str(flow.get("verdict")))

                st.markdown(textwrap.dedent(f"""
                <div class="flow-box">
                    <div class="flow-line">
                        {src} &nbsp;→&nbsp; {tr} &nbsp;→&nbsp; {dst}
                    </div>
                    <div style="margin-top:8px;color:#b3c2d4;font-size:0.9rem;">
                        Destination class: <b>{dst_class}</b>
                    </div>
                    <div class="flow-verdict">Verdict: <b>{verdict}</b></div>
                </div>
                """), unsafe_allow_html=True)
            else:
                st.info("No cross-application data flow detected.")
                st.caption("A data flow requires COPY in one app and PASTE in another.")

        with tab_entities:
            if r["entities"]:
                for entity in r["entities"]:
                    st.markdown(f"🔒 **{html.escape(str(entity))}**")
            else:
                st.success("No sensitive entities detected.")

        with tab_behavior:
            b1, b2 = st.columns(2)
            with b1:
                st.metric("Behavior Verdict", str(r["behavior"]["verdict"]))
            with b2:
                st.metric("Destination", str(r["behavior"].get("destination", "LOCAL")))

            st.markdown("**Session context**")
            st.code(json.dumps({
                "actions": [f"{a['action']} → {a['app']}" for a in preset["actions"]],
                "session_risk": r["session"]["session_risk_score"],
            }, indent=2), language="json")

        with tab_evidence:
            st.markdown("**Decision reasoning**")
            for line in r["decision"]["explanation"]:
                st.write(f"• {line}")

            st.markdown("**Masked text stored in audit**")
            st.code(r["masked"], language=None)

            if r["decision"].get("enforcement"):
                st.markdown("**Enforcement**")
                st.json(r["decision"]["enforcement"])
    else:
        st.info("👈 Choose a scenario and click **Run Security Pipeline** to begin.")


# ============================================================
# AUDIT LOG
# ============================================================
st.divider()
st.subheader("📜 Session Audit Log")
st.caption("Decision history for this browser session. Sensitive text is masked.")

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
    st.caption("No audit entries yet.")


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.markdown(textwrap.dedent("""
<div class="footer">
    <b>Sentinel Drishti</b> · On-Device AI Compliance & Data Loss Prevention
    <br>
    Browser dashboard · Native OS monitoring: <code>python sentinel.py</code>
</div>
"""), unsafe_allow_html=True)