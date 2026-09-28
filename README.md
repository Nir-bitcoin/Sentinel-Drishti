<div align="center">

# 🐉 Sentinel Drishti

**An on-device AI agent for detecting and preventing sensitive data loss on enterprise laptops.**

[![Tests](https://img.shields.io/badge/tests-62%2F62_passing-22c55e?style=flat-square)](tests/)
[![F1](https://img.shields.io/badge/OCR→Entity_F1-1.00-22c55e?style=flat-square)](#evidence)
[![Offline](https://img.shields.io/badge/core-100%25_offline-22c55e?style=flat-square)](#zero-cloud)
[![Snapdragon](https://img.shields.io/badge/Snapdragon-QNN%20%2F%20HTP-e2231a?style=flat-square)](docs/snapdragon_validation.md)

<br>

[![Showcase](https://img.shields.io/badge/🌐_Showcase-Hugging%20Face-yellow?style=for-the-badge\&logo=huggingface\&logoColor=white)](https://huggingface.co/spaces/kuchvo/Sentinel-Drishti)
[![Live Demo](https://img.shields.io/badge/💻_Live_Demo-Streamlit-ff4b4b?style=for-the-badge\&logo=streamlit\&logoColor=white)](https://sentinel-drishti-kgxhnyuna9wmtswppmgmze.streamlit.app/)
[![GitHub](https://img.shields.io/badge/📦_Source-GitHub-181717?style=for-the-badge\&logo=github\&logoColor=white)](https://github.com/Nir-bitcoin/Sentinel-Drishti)

<br>

**SusDetect Team** — by **Niranjan Vishe**

Snapdragon AI Lab Build & Present Challenge 2026

</div>

---

## Core Contribution

Sentinel Drishti is an on-device DLP agent that combines:

* **Data-flow tracking** across applications such as Excel → Clipboard → Gmail
* **Session-level risk** built from related events
* **Context-aware DLP decisions** based on data, behavior and destination
* **Tamper-evident audit records** with sensitive content masked before storage
* **Offline processing** so sensitive content does not need to leave the endpoint

The main design idea is:

> **Spend AI compute only when security context justifies it.**

---

## Try Sentinel Drishti

There are four ways to explore the project:

|  #  | Channel                | Link                                                                        | What it shows                                                |
| :-: | :--------------------- | :-------------------------------------------------------------------------- | :----------------------------------------------------------- |
|  1  | 🚀 **Offline Runtime** | [Run locally](#setup)                                                       | Real OCR, policy decisions, audit chain and local validation |
|  2  | 🌐 **Showcase Site**   | [Hugging Face](https://huggingface.co/spaces/kuchvo/Sentinel-Drishti)       | Project story, architecture and evidence                     |
|  3  | 💻 **Live Dashboard**  | [Streamlit](https://sentinel-drishti-kgxhnyuna9wmtswppmgmze.streamlit.app/) | Interactive scenarios, decisions and audit output            |
|  4  | 📦 **Source Code**     | [GitHub](https://github.com/Nir-bitcoin/Sentinel-Drishti)                   | Full implementation, tests and documentation                 |

---

# The Story

Enterprise laptops can contain sensitive information such as PAN numbers, salary data, phone numbers, contracts and internal documents.

A data-loss event does not always look like a sophisticated attack.

It can be something as simple as:

```text
Employee data
     ↓
   Excel
     ↓
   COPY
     ↓
 Clipboard
     ↓
Personal Gmail
```

The individual actions may look ordinary. The sequence is what creates the risk.

Sentinel Drishti treats data protection as a **context problem**, not only a text-detection problem.

It looks at:

* What information is present
* What the user is doing
* Where the information is going
* What happened earlier in the session

The result is a local-first DLP pipeline that connects perception, behavioral context and policy enforcement.

> **Spend AI compute only when security context justifies it.**

---

# Context-Driven DLP

A sensitive value by itself does not always tell us whether an action is risky.

Sentinel Drishti combines:

```text
      DATA SENSITIVITY
             +
        USER BEHAVIOR
             +
         DESTINATION
             ↓
      CONTEXT-AWARE DLP
             ↓
       ALLOW / WARN / BLOCK
```

This allows the same type of data to produce different decisions depending on context.

For example:

* A single `COPY` event can remain low risk → **ALLOW**
* `COPY → Gmail → PASTE` can represent an external transfer → **BLOCK**
* `READ` of a confidential file can remain allowed when no transfer occurs → **ALLOW**
* `COPY → Google Drive → PASTE` can trigger **WARN** and require confirmation

The important distinction is that the system evaluates the **sequence and context**, not just the presence of sensitive text.

---

# What It Does

When an employee copies sensitive information from Excel, Sentinel Drishti can track the related actions across applications.

A typical high-risk path is:

```text
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
 Session risk increases
        ↓
 Intent: EXFILTRATION
        ↓
 Decision: BLOCK_AND_ALERT
        ↓
 Audit recorded with masked PII
        ↓
 Arduino: RED LED + buzzer
```

For benign activity:

```text
Team meeting notes
        ↓
       Word
        ↓
       READ
        ↓
      LOCAL
        ↓
   No data flow
        ↓
      ALLOW
        ↓
   Audit recorded
```

The policy engine supports three outcomes:

* **ALLOW** — the action is permitted
* **WARN** — the action requires user confirmation
* **BLOCK** — the action is prevented and an alert is generated

---

# Evidence

The measurements below come from the listed test and evaluation setups.

## Test Results

```text
Unit tests ............... 25/25 passing
Security tests ........... 33/33 passing
End-to-end tests ......... 4/4 passing
-----------------------------------------
Total .................... 62/62 passing
```

## OCR → Entity Evaluation

**30 controlled labeled images**

```text
PAN ................ Precision 1.00 · Recall 1.00 · F1 1.00
PHONE .............. Precision 1.00 · Recall 1.00 · F1 1.00
FINANCIAL .......... Precision 1.00 · Recall 1.00 · F1 1.00
CONFIDENTIAL ....... Precision 1.00 · Recall 1.00 · F1 1.00

Macro average ...... Precision 1.00 · Recall 1.00 · F1 1.00
False positives .... 0
False negatives .... 0
```

> **Evaluation note:** These results come from a controlled 30-image regression dataset and are not presented as a general real-world accuracy estimate.

## CPU Performance

```text
Unchanged screen .......... ~8 ms P50   (control plane, no OCR)
Cached screen ............. ~3 ms P50   (SHA-256 hash lookup)
Cold OCR .................. ~9 s        (after ROI optimization)
Final OCR confidence ...... 0.968
```

The cold OCR path was reduced from the earlier 15–16 second range after the ROI optimization.

## Stage-Level Control Plane

Measured over 20 runs per stage:

```text
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
-----------------------------------------
TOTAL control plane ....... 8.03 ms P50
```

Run the breakdown locally:

```powershell
python scripts\latency_breakdown.py
```

---

# How It Works

Sentinel Drishti is organized as a 12-stage pipeline:

```text
Screen / Event
      ↓
Change Detector ───────────► SKIP if unchanged
      ↓
Event Policy (L0 / L1 / L2)
      ↓
Two-Stage ROI OCR ─────────► LRU Cache
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

## Compute Levels

### L0 — No Security Event

No relevant security event is present.

```text
No relevant change
       ↓
    Skip OCR
```

### L1 — Suspicious Event

Used for actions such as `COPY` or `PASTE`.

```text
COPY / PASTE
      ↓
   Fast OCR
```

### L2 — Critical Event

Used for higher-risk actions such as USB insertion, upload or email transfer.

```text
Critical event
      ↓
Precise ROI OCR
      ↓
Coverage check
      ↓
Full precise fallback when required
```

In the measured workload, **70% of frames take the L0 path**, avoiding unnecessary OCR work.

---

# What Makes It Different

## Event-Driven OCR

OCR is triggered around security-relevant actions instead of being run continuously on every frame.

## Two-Stage ROI OCR

A fast pass is performed first. Low-confidence regions can then be processed more precisely.

The change reduced the measured cold OCR path from roughly 16 seconds to roughly 9 seconds on CPU.

## Coverage Gate

For critical events, insufficient sensitive-entity coverage can trigger a stronger recognition pass.

## Data Flow Graph

The system tracks how information moves between applications:

```text
Excel
  ↓
Clipboard
  ↓
Gmail
```

This gives the policy engine more context than isolated events provide.

## Session Risk Engine

Risk can accumulate across related actions within a session.

For example:

```text
COPY
  ↓
Gmail
  ↓
PASTE
```

has a different security context from a single local `COPY`.

## Privacy-Preserving Audit

Raw sensitive values are masked before being stored in the audit summary.

Example:

```text
ABCD****F
```

Audit entries are linked with a SHA-256 hash chain so changes can be detected.

## Physical Alerting

An Arduino UNO Q can provide a physical warning using an LED and buzzer.

When the hardware is unavailable, the software alert path remains active.

---

# Rule-Based Intent Engine

The intent layer is deliberately **rule-based** rather than a black-box classifier.

It produces explicit, auditable results.

Example:

```text
Intent: BENIGN
Matched rules: NONE
Evidence level: LOW
```

For a high-risk transfer:

```text
Intent: EXFILTRATION
Matched rules: PII_001, FIN_001
Evidence level: HIGH
```

The evidence level is derived from the policy rules that actually fired. The system does not add a separate probabilistic confidence score to the demo.

---

# Design Trade-offs

Sentinel Drishti and conventional DLP systems can make different architectural trade-offs.

The comparison below describes the design priorities of this project rather than claiming that one architecture is universally better.

```text
┌─────────────────────────────────────────────────────────────┐
│ Conventional DLP approach      │ Sentinel Drishti          │
├─────────────────────────────────────────────────────────────┤
│ Centralized / cloud-assisted*  │ On-device core            │
│ Data may leave endpoint*       │ Data stays local          │
│ Continuous monitoring*         │ Event-driven OCR          │
│ Point-in-time events           │ Data-flow graph            │
│ Limited session context*       │ Session-level risk        │
│ Sensitive audit retention*     │ Masked audit              │
└─────────────────────────────────────────────────────────────┘
```

*Architecture varies across DLP products. This comparison describes the design trade-offs Sentinel Drishti is intended to address.

**Sentinel Drishti is optimized for:** on-device, context-aware and privacy-preserving DLP on Snapdragon-powered laptops.

---

# Snapdragon Validation

Sentinel Drishti's target runtime is:

**Snapdragon QNN / Hexagon HTP**

The Snapdragon-targeted perception components have been compiled, profiled and benchmarked through Qualcomm AI Hub on a hosted Snapdragon X Elite NPU environment.

The complete Sentinel Drishti pipeline is validated end-to-end on the local CPU development environment.

Full end-to-end validation on a physical Snapdragon PC is the remaining hardware-dependent step.

## Three-Tier Evidence Model

```text
Tier A
Snapdragon QNN / HTP
Target architecture

        ↓

Tier B
Qualcomm AI Hub
Hosted Snapdragon X Elite
Component validation

        ↓

Tier C
Local CPU
End-to-end pipeline validation
```

These tiers are reported separately and are **not combined into a single performance number**.

## Tier B — EasyOCR on Snapdragon X Elite

Compiled and benchmarked through Qualcomm AI Hub:

```text
EasyOCR detector (w8a8) ...... 12.64 ms  · NPU
EasyOCR recognizer (w8a8) .... 10.55 ms  · NPU
```

These are **component-level Snapdragon benchmarks**, not end-to-end Sentinel timings.

## Reproduce the Benchmark

```bash
pip install qai-hub qai-hub-models
qai-hub configure --api_token YOUR_TOKEN
qai-hub-models perf easyocr
```

Full validation notes:

[docs/snapdragon_validation.md](docs/snapdragon_validation.md)

## Backend Selection

```powershell
python sentinel.py --backend qnn     # Request QNN / HTP
python sentinel.py --backend cpu     # Force CPU
python sentinel.py --backend auto    # Auto-detect
```

On a compatible Snapdragon host, `--backend qnn` requests the Hexagon NPU path.

On an unsupported host, the runtime falls back to CPU and reports the reason.

---

# Zero Cloud

The core DLP pipeline is designed to operate without cloud processing of the protected content.

```text
Internet required ....... NO
Cloud API required ...... NO
OCR processing .......... LOCAL
Entity detection ........ LOCAL
Risk engine ............. LOCAL
DLP policy .............. LOCAL
Audit chain ............. LOCAL
```

Offline verification is tested by blocking socket calls before running the full pipeline:

```powershell
python tests/test_offline.py
```

Expected result:

```text
Blocking all network calls...
Network block: ACTIVE

Full pipeline ran with ZERO network calls.

============================================================
  OFFLINE VERIFICATION: PASS
============================================================
```

---

# Setup

## Windows

```powershell
git clone https://github.com/Nir-bitcoin/Sentinel-Drishti
cd Sentinel-Drishti
.\setup.ps1
.\run.ps1
```

## Linux / macOS

```bash
git clone https://github.com/Nir-bitcoin/Sentinel-Drishti
cd Sentinel-Drishti
bash setup.sh
bash run.sh
```

## Or Use the Launcher

```bash
python sentinel.py
```

The launcher provides:

```text
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

# Verify Everything

Run the checks independently:

```powershell
python tests/test_pipeline.py
python tests/test_security_deep.py
python tests/test_e2e.py
python tests/test_offline.py
python scripts/health_check.py
python scripts/deployment_check.py
python scripts/run_scenario.py --all
python evaluation/run_ocr_entity_eval.py
python scripts/latency_breakdown.py
```

These cover:

* Unit tests
* Security tests
* End-to-end scenarios
* Offline verification
* System health
* Deployment validation
* Deterministic scenario validation
* OCR/entity evaluation
* Performance measurements

---

# Repository Structure

```text
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
├── evaluation/        30-image OCR → entity evaluation
├── demo_scenarios/    5 YAML scenarios
├── docs/              documentation
├── sentinel.py        unified launcher
├── setup.ps1
├── run.ps1
├── setup.sh
├── run.sh
└── app.py             Streamlit dashboard
```

The modules are separated so individual components can be tested or replaced independently.

---

# Roadmap

* Physical Snapdragon X Elite validation of the full pipeline
* QNN-compiled EasyOCR model deployed directly on-device
* OS-level clipboard and USB interception
* Multi-language OCR beyond English
* MDM integration for enterprise deployment

---

# Documentation

| File                                                           | What it contains                    |
| :------------------------------------------------------------- | :---------------------------------- |
| [docs/architecture.md](docs/architecture.md)                   | Full pipeline and design decisions  |
| [docs/benchmark.md](docs/benchmark.md)                         | Benchmark methodology               |
| [docs/benchmark_comparison.md](docs/benchmark_comparison.md)   | Tier A/B/C comparison               |
| [docs/security.md](docs/security.md)                           | Threat model and security design    |
| [docs/use_cases.md](docs/use_cases.md)                         | Enterprise scenarios                |
| [docs/innovation.md](docs/innovation.md)                       | Project innovation and design ideas |
| [docs/snapdragon_validation.md](docs/snapdragon_validation.md) | Snapdragon validation evidence      |

---

# Links

| Channel               | Link                                                                        |
| :-------------------- | :-------------------------------------------------------------------------- |
| 🌐 **Showcase Site**  | [Hugging Face](https://huggingface.co/spaces/kuchvo/Sentinel-Drishti)       |
| 💻 **Live Dashboard** | [Streamlit](https://sentinel-drishti-kgxhnyuna9wmtswppmgmze.streamlit.app/) |
| 📦 **Source Code**    | [GitHub](https://github.com/Nir-bitcoin/Sentinel-Drishti)                   |
| ⚙️ **CI/CD**          | [GitHub Actions](https://github.com/Nir-bitcoin/Sentinel-Drishti/actions)   |
| 💼 **LinkedIn**       | [Niranjan Vishe](https://www.linkedin.com/in/nirvishe/)                     |

---

<div align="center">

**Sentinel Drishti**

**SusDetect Team — Niranjan Vishe**

Snapdragon AI Lab Build & Present Challenge 2026

</div>
