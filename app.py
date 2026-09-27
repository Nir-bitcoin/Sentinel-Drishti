# app.py
# Sentinel Drishti — Stylish Streamlit Dashboard
# Same pipeline logic, upgraded UI for judge/demo presentation.

import streamlit as st
import json
import html
from pathlib import Path
from datetime import datetime


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Sentinel Drishti",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown(
    """
    <style>
    /* ---------- GLOBAL ---------- */
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(59,130,246,0.08), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(168,85,247,0.07), transparent 25%),
            #07111f;
        color: #e8eef7;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* ---------- SIDEBAR ---------- */
    section[data-testid="stSidebar"] {
        background: #081321;
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem;
    }

    /* ---------- TEXT ---------- */
    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    h1 {
        font-weight: 800 !important;
    }

    /* ---------- METRICS ---------- */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 16px 18px;
        border-radius: 14px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }

    div[data-testid="stMetricLabel"] {
        color: #91a4bd !important;
        font-size: 0.82rem !important;
    }

    div[data-testid="stMetricValue"] {
        color: #f5f8fc !important;
        font-weight: 750 !important;
    }

    /* ---------- BUTTONS ---------- */
    .stButton > button {
        border-radius: 10px;
        min-height: 44px;
        font-weight: 650;
        border: 1px solid rgba(255,255,255,0.10);
        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        border-color: rgba(255,255,255,0.22);
    }

    /* ---------- INPUTS ---------- */
    div[data-baseweb="select"] > div,
    textarea,
    input {
        border-radius: 10px !important;
    }

    /* ---------- EXPANDERS ---------- */
    div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        margin-bottom: 8px;
    }

    /* ---------- DATAFRAME ---------- */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
    }

    /* ---------- HERO ---------- */
    .hero {
        position: relative;
        padding: 28px 30px;
        border-radius: 20px;
        background:
            linear-gradient(
                135deg,
                rgba(20,45,78,0.95),
                rgba(15,28,50,0.94)
            );
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 20px 55px rgba(0,0,0,0.22);
        margin-bottom: 20px;
        overflow: hidden;
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        right: -80px;
        top: -90px;
        border-radius: 50%;
        background: rgba(59,130,246,0.12);
        filter: blur(5px);
    }

    .hero-title {
        font-size: 2.15rem;
        font-weight: 850;
        margin-bottom: 7px;
        position: relative;
        z-index: 1;
    }

    .hero-subtitle {
        color: #a9bbd1;
        font-size: 1rem;
        max-width: 900px;
        position: relative;
        z-index: 1;
        line-height: 1.55;
    }

    .hero-badges {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 16px;
        position: relative;
        z-index: 1;
    }

    .badge {
        padding: 6px 11px;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 700;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.045);
        color: #dbe7f5;
    }

    /* ---------- SECTION CARD ---------- */
    .panel {
        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 14px;
    }

    .panel-title {
        font-size: 0.95rem;
        font-weight: 750;
        color: #c8d6e7;
        margin-bottom: 8px;
    }

    .panel-text {
        color: #8fa4bd;
        font-size: 0.86rem;
        line-height: 1.55;
    }

    /* ---------- DECISION ---------- */
    .decision {
        padding: 18px 20px;
        border-radius: 16px;
        margin-bottom: 18px;
        border: 1px solid rgba(255,255,255,0.10);
    }

    .decision-block {
        background: rgba(220,38,38,0.10);
        border-color: rgba(248,113,113,0.35);
    }

    .decision-warn {
        background: rgba(234,179,8,0.10);
        border-color: rgba(250,204,21,0.35);
    }

    .decision-allow {
        background: rgba(34,197,94,0.10);
        border-color: rgba(74,222,128,0.30);
    }

    .decision-main {
        font-size: 1.25rem;
        font-weight: 800;
    }

    .decision-sub {
        font-size: 0.82rem;
        margin-top: 4px;
        color: #a9bbd1;
    }

    /* ---------- FLOW ---------- */
    .flow-box {
        padding: 14px 16px;
        background: rgba(59,130,246,0.07);
        border: 1px solid rgba(96,165,250,0.18);
        border-radius: 12px;
        margin-top: 8px;
    }

    .flow-line {
        font-size: 0.95rem;
        font-weight: 650;
        color: #dce9f8;
    }

    .flow-verdict {
        margin-top: 7px;
        color: #8fa4bd;
        font-size: 0.82rem;
    }

    /* ---------- CODE / AUDIT ---------- */
    code {
        border-radius: 8px !important;
    }

    /* ---------- TOP INFO ---------- */
    .demo-strip {
        text-align: center;
        font-size: 0.77rem;
        color: #8fa4bd;
        margin-top: 5px;
        margin-bottom: 18px;
    }

    /* ---------- FOOTER ---------- */
    .footer {
        text-align: center;
        color: #71859d;
        font-size: 0.76rem;
        padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div style="
            padding:14px 14px 12px 14px;
            border-radius:14px;
            background:rgba(255,255,255,0.035);
            border:1px solid rgba(255,255,255,0.08);
            margin-bottom:15px;
        ">
            <div style="font-size:1.15rem;font-weight:800;">
                🛡️ Sentinel Drishti
            </div>
            <div style="color:#8fa4bd;font-size:0.78rem;margin-top:4px;">
                On-Device AI DLP Agent
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- BACKEND ----------
    st.subheader("⚙️ Runtime Backend")

    backend = st.radio(
        "Runtime target",
        options=[
            "🎯 Snapdragon QNN (target)",
            "💻 CPU (fallback)",
        ],
        index=0,
        label_visibility="collapsed",
        help=(
            "**Snapdragon QNN / Hexagon HTP** is the primary target runtime.\n\n"
            "**CPU** is the development / validation fallback."
        ),
    )

    if backend.startswith("🎯"):
        st.info(
            "**Target runtime**\n\n"
            "Snapdragon QNN / Hexagon HTP\n\n"
            "Hosted Snapdragon X Elite validation:\n"
            "- Detector: **12.64 ms**\n"
            "- Recognizer: **10.55 ms**\n\n"
            "_This browser demo runs on CPU. Native runtime selects QNN "
            "when compatible hardware is available._"
        )
    else:
        st.warning(
            "**Fallback runtime**\n\n"
            "CPU — used for development and validation.\n\n"
            "Native runtime auto-selects QNN when Snapdragon hardware is detected."
        )

    st.divider()

    # ---------- HELP ----------
    st.subheader("❓ Q&A / Help")

    with st.expander("🟢 What is ALLOW?"):
        st.write(
            "**ALLOW** means the pipeline decided the action is safe. "
            "This happens when there is no sensitive data, no risky behavior, "
            "or the destination is local/trusted.\n\n"
            "**Example:** Reading a confidential file locally."
        )

    with st.expander("🟡 What is WARN?"):
        st.write(
            "**WARN** means there is some risk, but not enough to block. "
            "User confirmation is required before proceeding.\n\n"
            "**Example:** Pasting a PAN number into Google Drive."
        )

    with st.expander("🔴 What is BLOCK?"):
        st.write(
            "**BLOCK** means sensitive data is being exfiltrated to an external "
            "destination. The action is prevented and a physical alert fires "
            "(Arduino LED + buzzer).\n\n"
            "**Example:** Pasting salary + PAN into personal Gmail."
        )

    with st.expander("Why is my preset showing ALLOW?"):
        st.write(
            "Each preset is deterministic. If you chose a benign preset "
            "(for example, 'Normal work'), the pipeline correctly returns ALLOW.\n\n"
            "**To see a BLOCK:** choose **PII → Personal Gmail**."
        )

    with st.expander("Why is 'Data Flow: No flow detected'?"):
        st.write(
            "A data flow requires a cross-application transfer:\n\n"
            "**COPY in App A → PASTE in App B**"
        )

    with st.expander("Cache / performance looks off?"):
        st.write(
            "The first run loads OCR models and can take several seconds on CPU. "
            "Subsequent runs use the content-hash cache and are much faster."
        )

    with st.expander("Where is Snapdragon NPU used?"):
        st.write(
            "Target runtime is **Snapdragon QNN / Hexagon HTP**.\n\n"
            "EasyOCR components benchmarked on hosted Snapdragon X Elite:\n"
            "- Detector: **12.64 ms**\n"
            "- Recognizer: **10.55 ms**\n\n"
            "Native runtime:\n"
            "`python sentinel.py --backend qnn`"
        )

    with st.expander("What's a 'Session Risk' score?"):
        st.write(
            "**Session risk** accumulates across events in one session.\n\n"
            "- Single COPY → lower risk\n"
            "- COPY → Gmail → PASTE → higher risk"
        )

    st.divider()

    # ---------- LEGEND ----------
    st.subheader("📖 Decision Legend")

    st.markdown(
        """
        <div style="font-size:0.82rem;line-height:2;">
        🔴 <b>BLOCK</b> — action prevented<br>
        🟡 <b>WARN</b> — user confirmation<br>
        🟢 <b>ALLOW</b> — action permitted<br>
        🔀 <b>FLOW</b> — cross-app transfer<br>
        📊 <b>RISK</b> — 0 to 100
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ---------- TEAM ----------
    st.subheader("👤 Submission")

    st.caption("Solo submission")
    st.write("**Niranjan Vishe**")
    st.caption("Snapdragon AI Lab Challenge 2026")

    st.divider()

    # ---------- LINKS ----------
    st.subheader("🔗 Project Links")

    st.markdown(
        """
        [📦 Source code](https://github.com/Nir-bitcoin/Sentinel-Drishti)

        [📚 Documentation](https://github.com/Nir-bitcoin/Sentinel-Drishti/tree/main/docs)

        [🌐 Showcase](https://huggingface.co/spaces/kuchvo/Sentinel-Drishti)
        """
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
    """Map technical errors to user-friendly hints."""
    e = error_text.lower()

    if "memory" in e or "out of memory" in e:
        return "🛑 Memory limit reached. Try **⋮ → Reboot app** in Streamlit Cloud."

    if "no module named" in e or "modulenotfound" in e:
        return "📦 Missing module. Wait 1–2 min and refresh."

    if "file not found" in e or "filenotfound" in e:
        return "📁 File not found. Try rebooting the app."

    if "timeout" in e:
        return "⏱️ Timeout. Wait and try again. First run may take several seconds."

    if "opencv" in e or "libgl" in e:
        return (
            "🖼️ OpenCV GUI library missing. "
            "Cloud needs `opencv-python-headless`."
        )

    return "⚠️ Unexpected error. Try a different preset."


# ============================================================
# RUN SCENARIO
# ============================================================
def run_scenario(actions, text):
    """Run one scenario through the full pipeline."""
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
            flow.record(
                action["action"],
                action["app"],
                entities=entities,
            )

            session.record_event(
                action["action"],
                action["app"],
                entities=entities,
            )

            tracker.record(
                action["action"],
                action["app"],
            )

        behavior = tracker.assess_risk()
        risk = scorer.calculate(entities, behavior)
        intent = intent_clf.classify(text, entities)
        decision = dlp.evaluate(
            text,
            intent,
            behavior,
            risk,
        )

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
st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🛡️ Sentinel Drishti</div>

        <div class="hero-subtitle">
            On-device AI compliance and data-loss prevention for enterprise endpoints.
            The pipeline combines perception, behavior tracking, session risk,
            data-flow analysis and policy enforcement before sensitive data leaves
            the device.
        </div>

        <div class="hero-badges">
            <span class="badge">⚡ Event-driven AI</span>
            <span class="badge">🔒 Offline Core</span>
            <span class="badge">🧠 Snapdragon QNN Target</span>
            <span class="badge">✅ 62/62 Tests</span>
            <span class="badge">📊 F1 1.00*</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="demo-strip">
        Interactive security demonstration · Deterministic scenarios ·
        CPU browser fallback
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TOP METRICS
# ============================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("🎯 Target Backend", "QNN / NPU")

with c2:
    st.metric("💻 Fallback", "CPU")

with c3:
    st.metric("✅ Tests", "62 / 62")

with c4:
    st.metric("🔒 Core Mode", "Offline")


# ============================================================
# MAIN LAYOUT
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)

col_left, col_right = st.columns(
    [0.85, 1.6],
    gap="large",
)


# ============================================================
# LEFT — SCENARIO CONTROL
# ============================================================
with col_left:

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">🎬 Scenario Control</div>
            <div class="panel-text">
                Select a deterministic security scenario and run the complete
                perception → behavior → risk → DLP pipeline.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    preset_name = st.selectbox(
        "Preset",
        list(PRESETS.keys()),
    )

    preset = PRESETS[preset_name]

    custom_text = st.text_area(
        "Text on screen",
        value=preset["text"],
        height=110,
    )

    st.markdown("**Activity sequence**")

    action_labels = [
        f"{a['action']} → {a['app']}"
        for a in preset["actions"]
    ]

    for action_label in action_labels:
        st.markdown(
            f"""
            <div style="
                padding:9px 11px;
                margin:5px 0;
                border-radius:9px;
                background:rgba(255,255,255,0.028);
                border:1px solid rgba(255,255,255,0.06);
                color:#cbd8e7;
                font-size:0.82rem;
            ">
                {html.escape(action_label)}
            </div>
            """,
            unsafe_allow_html=True,
        )

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

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">🔎 Security Decision</div>
            <div class="panel-text">
                The result below is generated by the same policy pipeline used
                by the local Sentinel Drishti runtime.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if run_btn:

        with st.spinner("Running Sentinel Drishti pipeline..."):

            result = run_scenario(
                preset["actions"],
                custom_text,
            )

            # ------------------------------------------------
            # ERROR
            # ------------------------------------------------
            if result.get("error"):

                st.error("🔴 Pipeline error occurred")

                st.write("**What happened:**")
                st.code(
                    result["error"],
                    language=None,
                )

                st.write("**What to do:**")
                st.info(
                    result.get(
                        "user_hint",
                        "Try again or reboot the app.",
                    )
                )

                st.stop()

            # ------------------------------------------------
            # SAVE HISTORY
            # ------------------------------------------------
            st.session_state.history.insert(
                0,
                result,
            )

            st.session_state.audit_entries.append(
                {
                    "ts": result["timestamp"],
                    "decision": result["decision"]["decision"],
                    "severity": result["decision"]["severity"],
                    "rules": [
                        m["rule_id"]
                        for m in result["decision"]["matches"]
                    ],
                    "risk": result["risk"]["score"],
                    "masked": result["masked"][:120],
                }
            )

    # ========================================================
    # SHOW LATEST RESULT
    # ========================================================
    if st.session_state.history:

        r = st.session_state.history[0]

        decision = r["decision"]["decision"]

        # ----------------------------------------------------
        # DECISION CARD
        # ----------------------------------------------------
        if decision == "BLOCK_AND_ALERT":

            st.markdown(
                """
                <div class="decision decision-block">
                    <div class="decision-main">
                        🔴 BLOCK AND ALERT
                    </div>
                    <div class="decision-sub">
                        Sensitive data transfer was identified as a critical
                        exfiltration event.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif decision == "WARN_AND_ALERT":

            st.markdown(
                """
                <div class="decision decision-warn">
                    <div class="decision-main">
                        🟡 WARN AND ALERT
                    </div>
                    <div class="decision-sub">
                        Risk detected. User confirmation is required before
                        proceeding.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="decision decision-allow">
                    <div class="decision-main">
                        🟢 ALLOW
                    </div>
                    <div class="decision-sub">
                        The current action is permitted by the policy engine.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ----------------------------------------------------
        # SUMMARY METRICS
        # ----------------------------------------------------
        m1, m2, m3 = st.columns(3)

        with m1:
            st.metric(
                "📊 Risk",
                f"{r['risk']['score']}/100",
            )

        with m2:
            st.metric(
                "🧠 Session Risk",
                f"{r['session']['session_risk_score']}/100",
            )

        with m3:
            st.metric(
                "🎯 Intent",
                r["intent"]["classification"],
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # TABS
        # ----------------------------------------------------
        tab_flow, tab_entities, tab_behavior, tab_evidence = st.tabs(
            [
                "🔀 Data Flow",
                "🔍 Entities",
                "🧠 Behavior",
                "🔐 Evidence",
            ]
        )

        # ====================================================
        # DATA FLOW
        # ====================================================
        with tab_flow:

            flow = r["flow"]

            if flow.get("flow_detected"):

                source = html.escape(
                    str(flow.get("source"))
                )
                transfer = html.escape(
                    str(flow.get("transfer"))
                )
                destination = html.escape(
                    str(flow.get("destination"))
                )
                destination_class = html.escape(
                    str(flow.get("destination_class", "?"))
                )
                verdict = html.escape(
                    str(flow.get("verdict"))
                )

                st.markdown(
                    f"""
                    <div class="flow-box">
                        <div class="flow-line">
                            {source}
                            &nbsp; → &nbsp;
                            {transfer}
                            &nbsp; → &nbsp;
                            {destination}
                        </div>
                        <div style="
                            margin-top:6px;
                            color:#8fa4bd;
                            font-size:0.78rem;
                        ">
                            Destination class: {destination_class}
                        </div>
                        <div class="flow-verdict">
                            Verdict: <b>{verdict}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:

                st.info(
                    "No cross-application data flow detected."
                )

                st.caption(
                    "A data flow requires COPY in one app and PASTE in another."
                )

        # ====================================================
        # ENTITIES
        # ====================================================
        with tab_entities:

            entities = r["entities"]

            if entities:

                for entity in entities:

                    st.markdown(
                        f"""
                        <div style="
                            display:inline-block;
                            padding:7px 11px;
                            margin:3px;
                            border-radius:999px;
                            background:rgba(239,68,68,0.10);
                            border:1px solid rgba(248,113,113,0.25);
                            color:#fecaca;
                            font-size:0.80rem;
                            font-weight:650;
                        ">
                            🔒 {html.escape(str(entity))}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            else:

                st.success(
                    "No sensitive entities detected."
                )

        # ====================================================
        # BEHAVIOR
        # ====================================================
        with tab_behavior:

            behavior = r["behavior"]

            b1, b2 = st.columns(2)

            with b1:
                st.metric(
                    "Behavior Verdict",
                    str(behavior["verdict"]),
                )

            with b2:
                st.metric(
                    "Destination",
                    str(
                        behavior.get(
                            "destination",
                            "LOCAL",
                        )
                    ),
                )

            st.markdown("**Session context**")

            st.code(
                json.dumps(
                    {
                        "actions": [
                            f"{a['action']} → {a['app']}"
                            for a in preset["actions"]
                        ],
                        "session_risk":
                            r["session"]["session_risk_score"],
                    },
                    indent=2,
                ),
                language="json",
            )

        # ====================================================
        # EVIDENCE
        # ====================================================
        with tab_evidence:

            st.markdown("**Decision reasoning**")

            for line in r["decision"]["explanation"]:
                st.write(f"• {line}")

            st.markdown("**Masked text stored in audit**")

            st.code(
                r["masked"],
                language=None,
            )

            if r["decision"].get("enforcement"):

                st.markdown("**Enforcement**")

                st.json(
                    r["decision"]["enforcement"]
                )

    else:

        st.info(
            "👈 Choose a scenario and click "
            "**Run Security Pipeline** to begin."
        )


# ============================================================
# AUDIT LOG
# ============================================================
st.divider()

st.markdown(
    """
    <div class="panel">
        <div class="panel-title">📜 Session Audit Log</div>
        <div class="panel-text">
            Decision history for this browser session. Sensitive text is masked
            before being stored in the audit view.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.audit_entries:

    st.dataframe(
        st.session_state.audit_entries,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "⬇ Download Audit JSON",
        data=json.dumps(
            st.session_state.audit_entries,
            indent=2,
        ),
        file_name="sentinel_audit_session.json",
        mime="application/json",
        use_container_width=False,
    )

else:

    st.caption("No audit entries yet.")


# ============================================================
# DEMO VIDEO PLACEHOLDER
# ============================================================
st.divider()

st.markdown(
    """
    <div class="panel">
        <div class="panel-title">🎬 Demo Video</div>
        <div class="panel-text">
            Full end-to-end demonstration video will be added here.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info("🎥 Demo video — Coming soon")


# ============================================================
# FOOTER
# ============================================================
st.divider()

st.markdown(
    """
    <div class="footer">
        <b>Sentinel Drishti</b> · On-Device AI Compliance & Data Loss Prevention
        <br>
        Browser dashboard for pipeline demonstration ·
        Native OS monitoring available through <code>python sentinel.py</code>
    </div>
    """,
    unsafe_allow_html=True,
)