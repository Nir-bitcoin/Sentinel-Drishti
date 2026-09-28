<div align="center">

# 🐉 Sentinel Drishti

**An on-device AI agent for detecting and preventing sensitive data loss on enterprise laptops.**

[![Tests](https://img.shields.io/badge/tests-62%2F62_passing-22c55e?style=flat-square)](tests/)
[![F1](https://img.shields.io/badge/controlled_OCR→Entity_F1-1.00-22c55e?style=flat-square)](#evidence)
[![Offline](https://img.shields.io/badge/core-100%25_offline-22c55e?style=flat-square)](#zero-cloud)
[![Snapdragon](https://img.shields.io/badge/Snapdragon-QNN%20%2F%20HTP_target-e2231a?style=flat-square)](#snapdragon-validation)

<br>

[![Showcase](https://img.shields.io/badge/🌐_Showcase-Hugging%20Face-yellow?style=for-the-badge\&logo=huggingface\&logoColor=white)](https://huggingface.co/spaces/kuchvo/Sentinel-Drishti)
[![Live Demo](https://img.shields.io/badge/💻_Live_Demo-Streamlit-ff4b4b?style=for-the-badge\&logo=streamlit\&logoColor=white)](https://sentinel-drishti-kgxhnyuna9wmtswppmgmze.streamlit.app/)
[![GitHub](https://img.shields.io/badge/📦_Source-GitHub-181717?style=for-the-badge\&logo=github\&logoColor=white)](https://github.com/Nir-bitcoin/Sentinel-Drishti)

<br>

**SusDetect Team** — by **Niranjan Vishe**

Snapdragon AI Lab Build & Present Challenge 2026

</div>

---

# 30-Second Overview

> **The problem:** sensitive data can leave an enterprise laptop through ordinary actions such as `COPY → Clipboard → Gmail`.
>
> **The approach:** Sentinel Drishti combines data sensitivity, user behavior, destination and session context before making a DLP decision.
>
> **The key idea:** expensive AI processing is used only when security context justifies it.

<table>
<tr>
<td align="center"><strong>62/62</strong><br>automated tests<br><sub>25 unit · 33 security · 4 e2e</sub></td>
<td align="center"><strong>8.03 ms</strong><br>control-plane P50<br><sub>measured, no OCR</sub></td>
<td align="center"><strong>1.00</strong><br>macro F1<br><sub>30 controlled images</sub></td>
<td align="center"><strong>~9 s</strong><br>cold OCR<br><sub>CPU, after ROI optimization</sub></td>
</tr>
</table>

**Headline metrics are deliberately scoped:** the 8.03 ms figure is the control plane rather than full OCR latency, and the 1.00 F1 is from a controlled 30-image OCR→entity regression evaluation.

<!-- Add the final demo GIF/screenshot here when you have the repository asset. -->

<!-- Example: ![Sentinel Drishti demo](docs/demo.gif) -->

<div align="center">

[🎥 **Demo Video**](#demo-video) · [💻 **Live Dashboard**](https://sentinel-drishti-kgxhnyuna9wmtswppmgmze.streamlit.app/) · [🌐 **Showcase**](https://huggingface.co/spaces/kuchvo/Sentinel-Drishti) · [📚 **Documentation**](#documentation)

</div>

---

# The Story

Every enterprise laptop can contain sensitive information: PAN numbers, salary records, phone numbers, confidential contracts, and internal documents.

But a data leak does not always look like a sophisticated cyberattack.

Sometimes it looks like normal work:

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
```

No malware is required.

No complicated exploit is required.

The individual actions can look ordinary. The security meaning appears when the system connects the data, the action, the application, the destination and what happened earlier in the session.

That is the problem Sentinel Drishti is designed to address.

---

# The Solution

Sentinel Drishti is a local-first DLP agent that evaluates **context before enforcement**.

It asks four questions:

1. **What data is involved?**
2. **What is the user doing?**
3. **Where is the data going?**
4. **What happened earlier in the session?**

The policy engine then produces one of three outcomes:

```text
ALLOW / WARN / BLOCK
```

The system is designed to keep protected content on the endpoint while connecting AI perception with behavioral context and policy enforcement.

---

# Demo

The central demo is intentionally simple because it shows the main security behavior without needing a complicated attack.

## High-Risk Flow

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
 Data flow: EXFILTRATION
        ↓
 Intent: EXFILTRATION
        ↓
 Decision: BLOCK_AND_ALERT
        ↓
 PII masked in audit
        ↓
 Arduino: RED LED + buzzer
```

## Benign Flow

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

The same policy engine can therefore produce different outcomes based on context.

### Policy Outcomes

| Situation                               | Decision  |
| :-------------------------------------- | :-------- |
| Sensitive data → local `COPY`           | **ALLOW** |
| Sensitive data → Gmail → `PASTE`        | **BLOCK** |
| Sensitive data → Google Drive → `PASTE` | **WARN**  |
| Confidential file → local `READ`        | **ALLOW** |

---

# Core Innovation

Rather than presenting a long list of individual features, the project is built around three main ideas.

## 1. Context-Driven DLP ⭐

A sensitive value by itself does not automatically mean a security violation.

Sentinel Drishti combines:

```text
DATA SENSITIVITY
       +
USER BEHAVIOR
       +
DESTINATION
       +
SESSION CONTEXT
       ↓
CONTEXT-AWARE DLP
```

This lets the system distinguish between a local copy and a cross-application external transfer.

## 2. Event-Driven AI Compute ⭐

The system does not spend the same amount of AI compute on every frame.

```text
L0 → No relevant event → Skip OCR
L1 → Suspicious event → Fast OCR
L2 → Critical event → Precise OCR + coverage check
```

In the measured workload, **70% of frames take the L0 path**.

The goal is to reduce unnecessary compute on an always-on endpoint agent.

## 3. Data Flow + Session Risk ⭐

Instead of evaluating every event independently, Sentinel Drishti connects related actions:

```text
Excel
  ↓
Clipboard
  ↓
Gmail
```

A session-level risk engine then accumulates context across events, so a sequence such as `COPY → Gmail → PASTE` can be treated differently from a single local `COPY`.

### Also Part of the Implementation

* **Two-stage ROI OCR** — fast recognition first, precise re-recognition for low-confidence regions.
* **L2 coverage gate** — critical events can escalate when fast OCR does not provide sufficient sensitive-entity coverage.
* **Privacy-preserving audit** — raw PII is masked before storage and audit entries are chained with SHA-256 hashes.
* **Physical alerting** — Arduino UNO Q can provide LED/buzzer feedback, with a software fallback when hardware is unavailable.
* **Rule-based intent** — explicit, auditable rules instead of an additional black-box classifier.

---

# Architecture

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

No relevant security activity is present, so OCR is skipped.

### L1 — Suspicious Event

Used for actions such as `COPY` or `PASTE` with the faster recognition path.

### L2 — Critical Event

Used for higher-risk actions such as `USB`, `UPLOAD` or `EMAIL` with precise ROI recognition and the coverage gate.

```text
L2 critical event
      ↓
Precise ROI OCR
      ↓
Coverage check
      ↓
Full precise fallback when required
```

---

# Evidence

The measurements below come from the project's listed test and evaluation setups.

## 62/62 Automated Tests

```text
Unit tests ............... 25/25 passing
Security tests ........... 33/33 passing
End-to-end tests ......... 4/4 passing
-----------------------------------------
Total .................... 62/62 passing
```

**62/62 means 62 automated tests passed:** 25 unit tests, 33 security tests and 4 end-to-end tests.

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

> **Evaluation note:** this is a controlled 30-image regression evaluation and is not presented as a general real-world accuracy estimate.

## CPU Performance

```text
Unchanged screen .......... ~8 ms P50   (control plane, no OCR)
Cached screen ............. ~3 ms P50   (SHA-256 hash lookup)
Cold OCR .................. ~9 s        (after ROI optimization)
Final OCR confidence ...... 0.968
```

The cold OCR path was reduced from the earlier 15–16 second range after ROI optimization.

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

# Snapdragon Validation

Sentinel Drishti's target runtime is:

**Snapdragon QNN / Hexagon HTP**

The Snapdragon evidence is intentionally separated into three tiers so that target architecture, hosted NPU measurements and local end-to-end execution are not confused with each other.

## Three-Tier Evidence Model

| Tier  | What it represents                               | Where it ran                                              | Status                        |
| :---- | :----------------------------------------------- | :-------------------------------------------------------- | :---------------------------- |
| **A** | Snapdragon QNN / Hexagon HTP target architecture | Target design                                             | Snapdragon backend target     |
| **B** | EasyOCR detector/recognizer component benchmarks | Qualcomm AI Hub hosted Snapdragon X Elite NPU environment | Measured component benchmarks |
| **C** | Complete Sentinel Drishti pipeline               | Local CPU development environment                         | Measured end-to-end           |

### Physical Device Clarification

The complete Sentinel Drishti pipeline was **not** run end-to-end on a physical Snapdragon laptop in this development environment.

Tier B is real Snapdragon-related benchmark evidence from **Qualcomm AI Hub's hosted Snapdragon X Elite NPU environment**. Tier C is the local CPU end-to-end validation. The two are kept separate rather than presented as one end-to-end NPU number.

## Tier B — EasyOCR on Snapdragon X Elite

Compiled and benchmarked through Qualcomm AI Hub:

```text
EasyOCR detector (w8a8) ...... 12.64 ms  · NPU
EasyOCR recognizer (w8a8) .... 10.55 ms  · NPU
```

These are **component-level Snapdragon measurements**, not end-to-end Sentinel Drishti latency.

## Reproduce the Benchmark

```bash
pip install qai-hub qai-hub-models
qai-hub configure --api_token YOUR_TOKEN
qai-hub-models perf easyocr
```

Full notes:

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

# Evaluation Criteria

The challenge lists four evaluation areas. No weighting is stated in the provided challenge information, so this README maps evidence to the criteria without assigning scores or claiming that one criterion carries more marks.

| Criterion                             | Evidence in Sentinel Drishti                                                                                                                                                           | README evidence                                                                                           |
| :------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------- |
| **Technical Implementation**          | 12-stage pipeline, L0/L1/L2 event policy, ROI OCR, entity detection, behavior tracking, data-flow graph, session risk, rule-based intent, DLP engine, audit chain and Arduino alerting | [Architecture](#architecture) · [Evidence](#evidence)                                                     |
| **Application Use Case & Innovation** | Enterprise DLP use case, context-driven decisions, cross-application data flow, session-level risk, event-driven compute and OCR coverage gate                                         | [The Story](#the-story) · [Demo](#demo) · [Core Innovation](#core-innovation)                             |
| **Deployment & Accessibility**        | Offline local runtime, unified launcher, CPU fallback, Snapdragon QNN/HTP target, Streamlit dashboard and Hugging Face showcase                                                        | [Deployment & Accessibility](#deployment--accessibility) · [Setup](#setup)                                |
| **Presentation & Documentation**      | README, architecture/security documentation, benchmark notes, Snapdragon validation notes, reproducible commands and visual showcase                                                   | [Evidence](#evidence) · [Snapdragon Validation](#snapdragon-validation) · [Documentation](#documentation) |

---

# Zero Cloud

The core DLP pipeline is designed to operate without cloud processing of protected content.

```text
Internet required ....... NO
Cloud API required ...... NO
OCR processing .......... LOCAL
Entity detection ........ LOCAL
Risk engine ............. LOCAL
DLP policy .............. LOCAL
Audit chain ............. LOCAL
```

Offline verification blocks socket calls before executing the full pipeline:

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

# Deployment & Accessibility

Sentinel Drishti can be explored through multiple deployment paths:

### Local Runtime

Run the full pipeline locally with the unified launcher and verification scripts.

### Streamlit Dashboard

Interactive scenarios, decisions, entities, data flow and audit output:

https://sentinel-drishti-kgxhnyuna9wmtswppmgmze.streamlit.app/

### Hugging Face Showcase

A visual project overview with architecture and validation evidence:

https://huggingface.co/spaces/kuchvo/Sentinel-Drishti

### CPU Fallback

The runtime supports explicit CPU execution and automatic fallback when Snapdragon QNN/HTP is not available on the host.

---

# Try Sentinel Drishti

|  #  | Channel                | Link                                                                        | What it shows                                                |
| :-: | :--------------------- | :-------------------------------------------------------------------------- | :----------------------------------------------------------- |
|  1  | 🚀 **Offline Runtime** | [Run locally](#setup)                                                       | Real OCR, policy decisions, audit chain and local validation |
|  2  | 🌐 **Showcase Site**   | [Hugging Face](https://huggingface.co/spaces/kuchvo/Sentinel-Drishti)       | Project story, architecture and evidence                     |
|  3  | 💻 **Live Dashboard**  | [Streamlit](https://sentinel-drishti-kgxhnyuna9wmtswppmgmze.streamlit.app/) | Interactive scenarios, decisions and audit output            |
|  4  | 📦 **Source Code**     | [GitHub](https://github.com/Nir-bitcoin/Sentinel-Drishti)                   | Full implementation, tests and documentation                 |

---

# Rule-Based Intent Engine

The intent layer is deliberately **rule-based**, rather than a black-box learned classifier.

Example benign result:

```text
Intent: BENIGN
Matched rules: NONE
Evidence level: LOW
```

Example high-risk result:

```text
Intent: EXFILTRATION
Matched rules: PII_001, FIN_001
Evidence level: HIGH
```

The evidence level is derived from the policy rules that actually fired. The system does not add a separate probabilistic confidence score for intent.

---

# Privacy & Audit

Raw sensitive values are masked before being stored in the audit summary.

Example:

```text
ABCD****F
```

Audit entries are connected using a SHA-256 hash chain so changes can be detected.

The project therefore keeps the recorded security evidence useful without writing raw PII into the audit output.

---

# Design Trade-offs

Sentinel Drishti and conventional DLP systems can make different architectural trade-offs.

The comparison below describes the design priorities this project is intended to address.

```text
┌─────────────────────────────────────────────────────────────┐
│ Conventional DLP approach      │ Sentinel Drishti          │
├─────────────────────────────────────────────────────────────┤
│ Centralized / cloud-assisted*  │ On-device core            │
│ Data may leave endpoint*       │ Data stays local           │
│ Continuous monitoring*         │ Event-driven OCR          │
│ Point-in-time events           │ Data-flow graph            │
│ Limited session context*       │ Session-level risk         │
│ Sensitive audit retention*     │ Masked audit               │
└─────────────────────────────────────────────────────────────┘
```

*Architecture varies across DLP products. This comparison describes design trade-offs rather than making a universal claim about all DLP systems.

**Sentinel Drishti is optimized for:** on-device, context-aware and privacy-preserving DLP on Snapdragon-powered laptops.

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

## Launcher

```bash
python sentinel.py
```

Available modes:

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
* Deterministic scenarios
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

# Demo Video

The final submission video should show the same evidence presented in this README:

```text
Launcher
   ↓
Security demo
   ↓
Streamlit dashboard
   ↓
Hugging Face showcase
   ↓
Snapdragon / AI Hub validation
   ↓
GitHub tests + documentation
```

> Add the final video link here once uploaded.

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
