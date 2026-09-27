<div align="center">

# 🐉 Sentinel Drishti

**An on-device AI agent that stops sensitive data from leaving enterprise laptops.**

<br>

[![Tests](https://img.shields.io/badge/62%2F62-tests_passing-22c55e?style=for-the-badge&logo=pytest&logoColor=white)](#evidence)
[![F1](https://img.shields.io/badge/OCR→Entity-F1_1.00-22c55e?style=for-the-badge)](#evidence)
[![Offline](https://img.shields.io/badge/core-100%25_offline-22c55e?style=for-the-badge&logo=windows&logoColor=white)](#zero-cloud)
[![Snapdragon](https://img.shields.io/badge/Snapdragon-QNN_%2F_HTP-e2231a?style=for-the-badge&logo=qualcomm&logoColor=white)](docs/snapdragon_validation.md)

<br>

| 🚀 [**Run offline**](#four-ways-to-experience-sentinel-drishti) | 🌐 [**Showcase**](https://huggingface.co/spaces/kuchvo/Sentinel-Drishti) | 💻 [**Live demo**](https://sentinel-drishti.streamlit.app) | 📦 [**Source**](https://github.com/Nir-bitcoin/Sentinel-Drishti) |
|:---:|:---:|:---:|:---:|
| One-command install | Visual overview | Interactive pipeline | Full repository |

<br>

> **Core contribution:** Sentinel Drishti is an on-device DLP agent that
> reasons about *data flow across applications* (Excel → Clipboard → Gmail),
> accumulates *session-level risk* across events, and produces *tamper-evident
> audit decisions* — all without a single byte leaving the machine.

</div>

---

## The story

Every enterprise laptop holds sensitive data — PAN numbers, salaries, phone numbers, confidential contracts. And every day, someone copies a row from Excel and pastes it into their personal Gmail. No sophisticated attack. No malware. Just a single keystroke.

Conventional DLP tools struggle with this class of leak. Centralized and cloud-assisted approaches require data to leave the endpoint for scanning. Continuous-monitoring approaches burn battery on laptops built for all-day use. Neither design was built for the trade-off that enterprise Snapdragon PCs actually present.

**Sentinel Drishti is a different design.** It runs entirely on-device, watches only when security context justifies the compute, and produces tamper-evident audit decisions with physical alerting.

The core idea:

> **Spend AI compute only when security context justifies it.**

---

## The central innovation

```
      DATA SENSITIVITY
            +
      USER BEHAVIOR
            +
      DESTINATION
            ↓
  CONTEXT-AWARE DLP DECISION
            ↓
     ALLOW / WARN / BLOCK
```

Sentinel Drishti does not classify a single event in isolation. It combines **data sensitivity**, **user behavior**, and **destination** to produce a context-aware decision — with a tamper-evident audit trail.

This is why:

- A single `COPY` is **low-risk** → ALLOW
- `COPY → Gmail → PASTE` is **exfiltration** → BLOCK
- `READ` of a confidential file is **allowed** (local, no transfer)
- `COPY → Google Drive → PASTE` triggers **WARN** (user confirmation)

The same engine, four different outcomes. That is the difference between **event-driven** and **context-driven** DLP.

---

## What it does

When an employee copies sensitive data from Excel, Sentinel Drishti notices. When they open Gmail, it notices that too. When they paste — it builds a data flow graph across apps, accumulates session risk, classifies intent, and makes a decision.

Here's the demo scenario the judges will see:

```
Employee salary data
        ↓
      Excel
        ↓
      COPY
        ↓
    Clipboard
        ↓
   Personal Gmail
        ↓
  Data flow detected: EXFILTRATION
        ↓
     Session risk: 95/100
        ↓
   Decision: BLOCK_AND_ALERT
        ↓
  Audit recorded (PII masked)
        ↓
  Arduino: RED LED + buzzer
```

And here's what happens when it's benign:

```
Team meeting notes
        ↓
      Word
        ↓
      READ
        ↓
     LOCAL
        ↓
    No flow
        ↓
     ALLOW
        ↓
  Audit recorded (nothing exposed)
```

**Three outcomes. One policy engine.** Every decision is evidence-based — matched rules, evidence level, policy action. No fabricated confidence scores.

---

## Evidence

Everything below was measured. Nothing is estimated.

### Tests

```
Unit tests ............... 25/25 passing
Security tests ........... 33/33 passing
End-to-end tests ......... 4/4 passing
Total .................... 62/62 passing
```

### OCR → Entity evaluation (30 labeled images)

```
PAN ................ Precision 1.00 · Recall 1.00 · F1 1.00
PHONE .............. Precision 1.00 · Recall 1.00 · F1 1.00
FINANCIAL .......... Precision 1.00 · Recall 1.00 · F1 1.00
CONFIDENTIAL ....... Precision 1.00 · Recall 1.00 · F1 1.00

Macro average ...... Precision 1.00 · Recall 1.00 · F1 1.00
False positives .... 0
False negatives .... 0
```

### Performance (measured on CPU)

```
Unchanged screen .......... ~8 ms P50   (control plane, no OCR)
Cached screen ............. ~3 ms P50   (SHA-256 hash lookup)
Cold OCR .................. ~9 s        (was 15–16 s before ROI)
Final OCR confidence ...... 0.968
```

**Stage-level control plane breakdown** (20 runs per stage):

```
Change Detection .......... 0.27 ms P50
Event Policy .............. 0.003 ms P50
Entity Detection .......... 0.014 ms P50
Behavior Tracking ......... 0.020 ms P50
Risk Scoring .............. 0.002 ms P50
Data Flow Graph ........... 0.029 ms P50
Session Risk Engine ....... 0.017 ms P50
Rule-Based Intent Engine .. 0.003 ms P50
DLP Decision .............. 2.71 ms P50
Privacy Masking ........... 0.016 ms P50
Audit Chain Write ......... 4.94 ms P50
────────────────────────────────────────
TOTAL control plane ....... 8.03 ms P50
```

Run it yourself:

```powershell
python scripts\latency_breakdown.py
```

---

## How it works

Sentinel Drishti is a 12-stage pipeline. Here's the flow:

```
Screen / Event
    ↓
Change Detector ───────► SKIP (if unchanged)
    ↓
Event Policy (L0 / L1 / L2)
    ↓
Two-Stage ROI OCR ─────► LRU Cache
    ↓
Entity Detection
    ↓
Behavior Tracker + Data Flow Graph
    ↓
Risk Engine + Session Risk
    ↓
Rule-Based Intent Engine
    ↓
DLP Policy Engine
    ↓
ALLOW / WARN / BLOCK
    ↓
Audit Chain + Arduino
```

**The three compute levels:**

- **L0** — no security event. Skip OCR entirely. Costs ~8 ms.
- **L1** — suspicious event (COPY, PASTE). Run fast OCR.
- **L2** — critical event (USB insert, upload, email). Run precise ROI OCR.

70% of frames take the L0 path. That's the whole point.

**What makes it different:**

- **Event-driven, not frame-driven.** OCR runs on user actions, not every tick.
- **Two-stage ROI OCR.** Fast pass on the full image. Precise re-recognition only on the low-confidence regions. Cold path dropped from 16 s to 9 s on CPU.
- **Data flow graph.** Tracks how data moves across apps — Excel → Clipboard → Gmail — not just individual events.
- **Session risk engine.** Accumulates weighted risk across a session. A single COPY is low-risk. COPY → Gmail → PASTE is not.
- **Coverage gate (L2).** On critical events, if fast OCR misses sensitive entities, it escalates to a full precise pass. Safety net.
- **Privacy-preserving audit.** SHA-256 hash chain. Raw PII is never stored — only a masked summary like `ABCD****F`.
- **Physical alerting.** Arduino UNO Q with LED and buzzer. Software fallback if hardware is absent.

### Rule-based intent engine

The intent layer is **rule-based**, not a black-box classifier. It produces
explicit, auditable output:

```
Intent: BENIGN
Matched rules: NONE
Evidence level: LOW
```

or

```
Intent: EXFILTRATION
Matched rules: PII_001, FIN_001
Evidence level: HIGH
```

No probabilistic score is fabricated. The evidence level is derived from the
policy rules that actually fired.

---

## Design Trade-offs — vs Conventional DLP

Conventional DLP and Sentinel Drishti make **different architectural trade-offs**. This is not a claim that one is universally better — it is a clear statement of which design priorities Sentinel Drishti is optimized for.

```
┌─────────────────────────────────────────────────────────────┐
│ CONVENTIONAL DLP APPROACH       vs      SENTINEL DRISHTI   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Centralized / cloud-assisted*            On-device core    │
│ Sensitive data may leave endpoint        Data stays local   │
│ Recurring infrastructure costs*          Local processing   │
│ Continuous scanning can be costly*       70% frames skip    │
│ Compute-heavy monitoring*                Event-driven OCR   │
│ Point-in-time events                     Data-flow graph    │
│ Limited session context*                 Session risk       │
│ Sensitive audit data may be retained*    Masked audit       │
│                                                             │
│              Different design priorities                    │
│       Centralized controls  ↔  Local, context-aware DLP     │
└─────────────────────────────────────────────────────────────┘
```

\*Architecture varies across DLP products; comparison describes
the design trade-offs Sentinel Drishti is intended to address.

**Sentinel Drishti is optimized for:** on-device, context-aware, privacy-preserving DLP on Snapdragon-powered laptops.

---

## Snapdragon Validation

Sentinel Drishti's target runtime is Snapdragon QNN / Hexagon HTP.

The Snapdragon-targeted perception components have been compiled, profiled,
and benchmarked through Qualcomm AI Hub on a hosted Snapdragon X Elite NPU
environment.

The complete Sentinel Drishti pipeline is validated end-to-end on the local
CPU development environment. Full end-to-end validation on a physical
Snapdragon PC remains the hardware-dependent step.

### Three-tier evidence model

```
Tier A — Snapdragon QNN target architecture         (QNN backend, ready)
Tier B — EasyOCR component benchmarks on X Elite    (Qualcomm AI Hub, hosted)
Tier C — End-to-end pipeline validation             (local CPU, measured)
```

Tiers are never merged into a single number.

### Tier B evidence — EasyOCR on Snapdragon X Elite

Compiled and benchmarked on hosted Snapdragon X Elite via Qualcomm AI Hub:

```
EasyOCR detector (w8a8) ...... 12.64 ms  · NPU · 20 MB peak
EasyOCR recognizer (w8a8) .... 10.55 ms  · NPU · 10 MB peak
```

Reproducible:

```bash
pip install qai-hub qai-hub-models
qai-hub configure --api_token YOUR_TOKEN
qai-hub-models perf easyocr
```

Full tier model: [docs/snapdragon_validation.md](docs/snapdragon_validation.md)

### Backend selection

```powershell
python sentinel.py --backend qnn     # Request QNN/HTP (Snapdragon)
python sentinel.py --backend cpu     # Force CPU (development)
python sentinel.py --backend auto    # Auto-detect (default)
```

On a Snapdragon host, `--backend qnn` selects the Hexagon NPU. On any other
host, it falls back to CPU with a visible reason.

---

## Zero cloud

The core DLP pipeline never leaves the device.

```
Internet required ....... NO
Cloud API required ...... NO
OCR processing .......... LOCAL
Entity detection ........ LOCAL
Risk engine ............. LOCAL
DLP policy .............. LOCAL
Audit chain ............. LOCAL
```

There's a test that proves it. It blocks all socket calls and then runs the full pipeline:

```powershell
python tests/test_offline.py
```

Expected output:

```
Blocking all network calls...
Network block: ACTIVE

Full pipeline ran with ZERO network calls.

============================================================
  OFFLINE VERIFICATION: PASS
============================================================
```

---

## Four ways to experience Sentinel Drishti

> **Deployment & Accessibility.** Sentinel Drishti runs in four distinct
> environments — from a fully offline one-command install to a live
> browser dashboard. Pick the one that fits how you want to evaluate it.

### 1. 🚀 One-command offline (real pipeline)

Run the full pipeline locally — real OCR, real DLP decisions, real audit chain.

```powershell
git clone https://github.com/Nir-bitcoin/Sentinel-Drishti
cd Sentinel-Drishti
.\setup.ps1
.\run.ps1
```

Linux / macOS:

```bash
git clone https://github.com/Nir-bitcoin/Sentinel-Drishti
cd Sentinel-Drishti
bash setup.sh
bash run.sh
```

### 2. 🌐 Showcase site (visual overview)

Landing page with features, architecture, and evidence:

👉 [huggingface.co/spaces/kuchvo/Sentinel-Drishti](https://huggingface.co/spaces/kuchvo/Sentinel-Drishti)

### 3. 💻 Live dashboard (interactive)

Click-through the pipeline with preset scenarios:

👉 [sentinel-drishti.streamlit.app](https://sentinel-drishti.streamlit.app)

### 4. 📦 Source code

Full repository, 62 tests, documentation:

👉 [github.com/Nir-bitcoin/Sentinel-Drishti](https://github.com/Nir-bitcoin/Sentinel-Drishti)

### Or use the launcher

```bash
python sentinel.py
```

The launcher presents an interactive menu:

```
[1] Interactive Demo
[2] Live Monitoring
[3] Benchmark
[4] System Health
[5] Deployment Check
[6] Offline Verify
[7] Run Scenarios
[8] Streamlit Dashboard
[9] Provider Diagnostic
```

---

## Verify everything

Run each check independently, cheapest first:

```powershell
python tests/test_pipeline.py            # 25 unit tests
python tests/test_security_deep.py       # 33 security tests
python tests/test_e2e.py                 # 4 end-to-end tests
python tests/test_offline.py             # zero network calls
python scripts/health_check.py           # 12 components
python scripts/deployment_check.py       # 13 validations
python scripts/run_scenario.py --all     # 5 deterministic scenarios
python evaluation/run_ocr_entity_eval.py # 30-image F1 evaluation
python scripts/latency_breakdown.py      # per-stage P50/P95/P99
```

Every command is deterministic. Every number is reproducible.

---

## Repository structure

```
Sentinel-Drishti/
├── src/
│   ├── backend/       CPUBackend, QNNBackend, fallback selector
│   ├── vision/        EasyOCR two-stage ROI, change detector
│   ├── policy/        DLP engine, event policy, audit chain,
│   │                  data flow graph, session risk, policy loader
│   ├── reasoning/     Rule-based intent engine
│   ├── security/      Privacy masking
│   └── action/        Arduino alert
├── config/            policy.yaml
├── tests/             62 tests
├── scripts/           benchmarks, health, deployment, latency
├── evaluation/        30-image OCR→entity evaluation
├── demo_scenarios/    5 YAML scenarios
├── docs/              6 documentation files
├── sentinel.py        unified launcher
├── setup.ps1 / run.ps1 / setup.sh / run.sh
└── app.py             Streamlit dashboard
```

Each module is self-contained. Any one can be swapped or tested independently.

---

## Roadmap

- Physical Snapdragon X Elite validation of the full pipeline
- QNN-compiled EasyOCR model deployed on-device (pipeline scripted)
- OS-level clipboard and USB interception (currently simulated)
- Multi-language OCR beyond English
- MDM integration for enterprise fleet rollout

---

## Documentation

| File | What's in it |
|:---|:---|
| [docs/architecture.md](docs/architecture.md) | Full pipeline + design decisions |
| [docs/benchmark.md](docs/benchmark.md) | Benchmark methodology |
| [docs/benchmark_comparison.md](docs/benchmark_comparison.md) | Tier A/B/C comparison |
| [docs/security.md](docs/security.md) | Threat model + security depth |
| [docs/use_cases.md](docs/use_cases.md) | Enterprise scenarios |
| [docs/innovation.md](docs/innovation.md) | What's actually novel |
| [docs/snapdragon_validation.md](docs/snapdragon_validation.md) | Snapdragon validation evidence |

---

<div align="center">

### Built with

![Python](https://img.shields.io/badge/Python-3.10+-3b82f6?style=flat-square&logo=python&logoColor=white)
![EasyOCR](https://img.shields.io/badge/EasyOCR-bundled-22c55e?style=flat-square)
![Qualcomm AI Hub](https://img.shields.io/badge/Qualcomm%20AI%20Hub-validated-e2231a?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-ff4b4b?style=flat-square&logo=streamlit&logoColor=white)
![Arduino](https://img.shields.io/badge/Arduino-UNO%20Q-00979d?style=flat-square&logo=arduino&logoColor=white)

<br>

**Snapdragon AI Lab Build & Present Challenge 2026**

Solo submission by **Niranjan Vishe** · **niranjanvishe62@gmail.com**

<br>

*Built with ❤️ for on-device privacy.*

</div>