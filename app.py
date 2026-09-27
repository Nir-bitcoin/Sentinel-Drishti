# app.py
# Sentinel Drishti — Streamlit Dashboard
# Includes Q&A sidebar, backend selector, error handling, and audit log.

import streamlit as st
import json
from pathlib import Path
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

    # ---------- BACKEND SELECTOR ----------
    st.subheader("⚙️ Backend")

    backend = st.radio(
        "Runtime target",
        options=["🎯 Snapdragon QNN (target)", "💻 CPU (fallback)"],
        index=0,
        help=(
            "**Snapdragon QNN / Hexagon HTP** is the primary target runtime.\n\n"
            "**CPU** is the development / validation fallback."
        ),
    )

    if backend.startswith("🎯"):
        st.info(
            "**Target runtime**\n\n"
            "Snapdragon QNN / Hexagon HTP\n\n"
            "EasyOCR components validated on hosted Snapdragon X Elite:\n"
            "- Detector: **12.64 ms**\n"
            "- Recognizer: **10.55 ms**\n\n"
            "_This browser demo runs on CPU. The native runtime selects QNN "
            "when the hardware is available._"
        )
    else:
        st.warning(
            "**Fallback runtime**\n\n"
            "CPU — used for development and validation.\n\n"
            "Native runtime auto-selects QNN when Snapdragon host detected."
        )

    st.divider()

    # ---------- Q&A / HELP ----------
    st.subheader("❓ Q&A / Help")

    with st.expander("🟢 What is ALLOW?"):
        st.write(
            "**ALLOW** means the pipeline decided the action is safe. "
            "This happens when there is no sensitive data, or no risky behavior, "
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
            "(e.g., 'Normal work'), the pipeline correctly returns ALLOW.\n\n"
            "**To see a BLOCK**, choose **'PII → Personal Gmail'**."
        )

    with st.expander("Why is 'Data Flow: No flow detected'?"):
        st.write(
            "This appears when the actions do not form a cross-app transfer.\n\n"
            "A data flow requires: **COPY in App A → PASTE in App B**."
        )

    with st.expander("Cache / performance looks off?"):
        st.write(
            "The first run loads OCR models (~5–10 s on CPU). "
            "Subsequent runs use the content-hash cache (~3 ms)."
        )

    with st.expander("Streamlit Cloud shows 'Oh no'?"):
        st.write(
            "Usually a memory limit (1 GB free tier).\n\n"
            "Try: **⋮ → Reboot app** in Streamlit Cloud."
        )

    with st.expander("Where is Snapdragon NPU used?"):
        st.write(
            "Target runtime is **Snapdragon QNN / Hexagon HTP**.\n\n"
            "EasyOCR components benchmarked on hosted Snapdragon X Elite:\n"
            "- Detector: **12.64 ms**\n"
            "- Recognizer: **10.55 ms**\n\n"
            "Native runtime: `python sentinel.py --backend qnn`"
        )

    with st.expander("What's a 'Session Risk' score?"):
        st.write(
            "**Session risk** accumulates across events in one session.\n\n"
            "- A single COPY = low risk\n"
            "- COPY → Gmail → PASTE = **high risk**"
        )

    st.divider()

    # ---------- LEGEND ----------
    st.subheader("📖 Legend")
    st.markdown(
        "| Icon | Meaning |\n"
        "|:---:|:---|\n"
        "| 🔴 | Block and alert |\n"
        "| 🟡 | Warn — user confirmation |\n"
        "| 🟢 | Allow — safe action |\n"
        "| 🔀 | Data flow detected |\n"
        "| 📊 | Risk score (0–100) |"
    )

    st.divider()

    # ---------- TEAM ----------
    st.subheader("👤 Team")
    st.caption("Solo submission")
    st.write("**Niranjan Vishe**")
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
        return "⏱️ Timeout. Wait and try again (first run: 5–10 s)."
    if "opencv" in e or "libgl" in e:
        return "🖼️ OpenCV GUI library missing. Cloud needs `opencv-python-headless`."
    return "⚠️ Unexpected error. Try a different preset."


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
        return {"error": str(e), "user_hint": _get_user_hint(str(e))}


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
st.caption(
    "On-Device AI Compliance & Data Loss Prevention Agent · "
    "Snapdragon QNN / Hexagon HTP target · 62/62 tests · F1 = 1.00"
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Target backend", "QNN / NPU")
with c2:
    st.metric("Fallback", "CPU")
with c3:
    st.metric("Tests", "62 / 62")
with c4:
    st.metric("Core", "Offline")

st.divider()


# ============================================================
# LAYOUT
# ============================================================
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Scenario")
    preset_name = st.selectbox("Preset", list(PRESETS.keys()))
    preset = PRESETS[preset_name]

    custom_text = st.text_area("Text on screen", value=preset["text"], height=100)

    st.write("**Actions**")
    action_labels = [f"{a['action']} → {a['app']}" for a in preset["actions"]]
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

            # ---- ERROR HANDLING ----
            if result.get("error"):
                st.error("🔴 Pipeline error occurred")
                st.write("**What happened:**")
                st.code(result["error"], language=None)
                st.write("**What to do:**")
                st.info(result.get("user_hint", "Try again or reboot the app."))
                st.divider()
                st.caption(
                    "Still stuck? Check the sidebar **Q&A / Help** section, "
                    "or reboot the app from Streamlit Cloud."
                )
                st.stop()

            # ---- NORMAL RESULT ----
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
        if decision == "BLOCK_AND_ALERT":
            st.error("🔴 BLOCK_AND_ALERT")
        elif decision == "WARN_AND_ALERT":
            st.warning("⚠️ WARN_AND_ALERT (user confirmation required)")
        else:
            st.success("🟢 ALLOW")

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
            st.caption("A data flow requires COPY in one app and PASTE in another.")

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
            st.markdown("**Enforcement**")
            st.json(r["decision"]["enforcement"])
    else:
        st.info("Choose a preset and click **▶ Run Pipeline**.")


# ============================================================
# AUDIT LOG
# ============================================================
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


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    "Browser demonstration of the perception and policy pipeline. "
    "Native OS-level monitoring is available in the local runtime "
    "(`python sentinel.py`)."
)