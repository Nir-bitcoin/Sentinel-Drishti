<div align="center">

<br/>

<img src="https://img.shields.io/badge/⚡_QUALCOMM-SNAPDRAGON_AI_LAB_2026-8B0000?style=for-the-badge&labelColor=1a1a1a" alt="Snapdragon AI Lab 2026"/>

<br/><br/>

<h1>
🛡️ Sentinel&nbsp;Drishti
</h1>

<h3><i>Watches every screen. Explains every decision. Never leaves the device.</i></h3>

<p><b>An on-device AI agent that stops sensitive data from leaving enterprise laptops —<br/>
without sending a single byte to the cloud.</b></p>

<br/>

<img src="https://img.shields.io/badge/tests-62%2F62_passing-2EA043?style=flat-square"/>&nbsp;
<img src="https://img.shields.io/badge/OCR→Entity_F1-1.00-2EA043?style=flat-square"/>&nbsp;
<img src="https://img.shields.io/badge/precision-1.00-2EA043?style=flat-square"/>&nbsp;
<img src="https://img.shields.io/badge/core-100%25_offline-1E88E5?style=flat-square"/>&nbsp;
<img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square"/>

<br/><br/>

[![Watch Demo](https://img.shields.io/badge/▶_WATCH_DEMO_VIDEO-DA1E28?style=for-the-badge)](your-video-link)
&nbsp;
[![Try Live Dashboard](https://img.shields.io/badge/🌐_TRY_LIVE_DASHBOARD-1E88E5?style=for-the-badge)](your-streamlit-link)

<br/><br/>

<sub>Built solo for the Snapdragon AI Lab Build & Present Challenge 2026 🇮🇳</sub>

<br/><br/>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

</div>
---

## The story

Every enterprise laptop holds sensitive data — PAN numbers, salaries, phone numbers, confidential contracts. And every day, someone copies a row from Excel and pastes it into their personal Gmail. No sophisticated attack. No malware. Just a single keystroke.

Existing DLP tools can't solve this. They're either cloud-based (which means your data leaves the device to be scanned — a privacy violation by design), or they watch every frame of your screen (which kills battery on a laptop built for all-day use).

**Sentinel Drishti is a different approach.** It runs entirely on-device, watches only when security context justifies the compute, and produces tamper-evident audit decisions with physical alerting.

The core idea:

> **Spend AI compute only when security context justifies it.**

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

**Three outcomes. One policy engine.** Every decision is evidence-based — matched rules, evidence level, policy action. No fake confidence scores.

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
Intent Classifier
    ↓
DLP Policy Engine
    ↓
ALLOW / WARN / BLOCK
    ↓
Audit Chain + Arduino
```

**The three compute levels:**

- **L0** — no security event. Skip OCR entirely. Costs ~3.93 ms.
- **L1** — suspicious event (COPY, PASTE). Run fast OCR.
- **L2** — critical event (USB insert, upload, email). Run precise ROI OCR.

70% of frames take the L0 path. That's the whole point.

**What makes it different from every other DLP agent:**

- **Event-driven, not frame-driven.** OCR runs on user actions, not every tick.
- **Two-stage ROI OCR.** Fast pass on the full image. Precise re-recognition only on the low-confidence regions. Cold path dropped from 16 s to 9 s on CPU.
- **Data flow graph.** Tracks how data moves across apps — Excel → Clipboard → Gmail — not just individual events.
- **Session risk engine.** Accumulates weighted risk across a session. A single COPY is low-risk. COPY → Gmail → PASTE is not.
- **Coverage gate (L2).** On critical events, if fast OCR misses sensitive entities, it escalates to a full precise pass. Safety net.
- **Privacy-preserving audit.** SHA-256 hash chain. Raw PII is never stored — only a masked summary like `ABCD****F`.
- **Physical alerting.** Arduino UNO Q with LED and buzzer. Software fallback if hardware is absent.

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
Unchanged screen .......... 3.93 ms P50  (control plane, no OCR)
Cached screen ............. ~3 ms P50    (SHA-256 hash lookup)
Cold OCR .................. ~9 s         (was 15–16 s before ROI)
Final OCR confidence ...... 0.968
```

**Stage-level control plane breakdown** (20 runs per stage):

```
Change Detection .......... 0.15 ms P50
Event Policy .............. 0.002 ms P50
Entity Detection .......... 0.008 ms P50
Behavior Tracking ......... 0.011 ms P50
Risk Scoring .............. 0.001 ms P50
Data Flow Graph ........... 0.016 ms P50
Session Risk Engine ....... 0.009 ms P50
Intent Classification ..... 0.001 ms P50
DLP Decision .............. 1.06 ms P50
Privacy Masking ........... 0.007 ms P50
Audit Chain Write ......... 2.66 ms P50
────────────────────────────────────────
TOTAL control plane ....... 3.93 ms P50
```

Run it yourself:

```powershell
python scripts\latency_breakdown.py
```

---

## Snapdragon

**The honest version.**

Sentinel Drishti's target runtime is Snapdragon QNN / Hexagon HTP. The QNN backend is architecturally complete — it auto-selects when the Qualcomm Execution Provider is available, and falls back to CPU with a visible reason when it isn't.

I do not have physical Snapdragon hardware in my development environment. So I've kept the evidence in three clearly separated tiers:

```
Tier A — Snapdragon QNN target architecture         (QNN backend, ready)
Tier B — EasyOCR component benchmarks on X Elite    (Qualcomm AI Hub, hosted)
Tier C — End-to-end pipeline validation             (local CPU, measured)
```

Tiers are never merged into a single number.

**Tier B evidence** — EasyOCR compiled and benchmarked on hosted Snapdragon X Elite, run through Qualcomm AI Hub:

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

## Getting started

### Windows

```powershell
git clone https://github.com/Nir-bitcoin/Sentinel-Drishti
cd Sentinel-Drishti
.\setup.ps1
.\run.ps1
```

### Linux / macOS

```bash
git clone https://github.com/Nir-bitcoin/Sentinel-Drishti
cd Sentinel-Drishti
bash setup.sh
bash run.sh
```

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

### Switching backends

```powershell
python sentinel.py --backend qnn     # Request QNN/HTP (Snapdragon)
python sentinel.py --backend cpu     # Force CPU (development)
python sentinel.py --backend auto    # Auto-detect (default)
```

On a Snapdragon host, `--backend qnn` selects the Hexagon NPU. On any other host, it falls back to CPU with a visible reason.

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
│   ├── reasoning/     Intent classifier
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

## Limitations

I'd rather tell you what doesn't work than pretend.

- **No physical Snapdragon validation.** The QNN backend is ready, but I haven't run the full pipeline on a real Hexagon NPU. Tier B component benchmarks are from Qualcomm AI Hub, not local hardware.
- **Enforcement is simulated.** The DLP decision is produced, but OS-level clipboard and USB interception are not implemented in this prototype.
- **Cold OCR is slow on CPU.** ~9 seconds. That's what happens without an NPU. On Snapdragon X Elite (Tier B), the same EasyOCR components run at 12.64 ms and 10.55 ms.
- **English only.** Multi-language OCR beyond English is on the roadmap.

These are documented in [docs/snapdragon_validation.md](docs/snapdragon_validation.md) and reflected in the three-tier evidence model.

---

## Roadmap

- Physical Snapdragon X Elite validation of the full pipeline
- QNN-compiled EasyOCR model deployed on-device (pipeline scripted)
- OS-level clipboard and USB interception
- Multi-language OCR
- MDM integration for enterprise fleet rollout

---

## Why this exists

Data leaks on enterprise laptops are not a cybersecurity problem. They're a design problem. The tools that exist are either too invasive (cloud-based) or too expensive (server-heavy) or too dumb (frame-blind). None of them respect the two constraints that actually matter: **privacy** and **battery**.

Sentinel Drishti is a small attempt to fix that. It spends compute only when there's a reason to. It keeps audit logs that prove *that* a block happened, not *what* was blocked. It produces decisions a compliance officer can defend, not a black-box score.

And it runs on the machine that owns the data. Always.

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
| [docs/snapdragon_validation.md](docs/snapdragon_validation.md) | Honest Snapdragon evidence |

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

Solo submission.

<br>



</div>