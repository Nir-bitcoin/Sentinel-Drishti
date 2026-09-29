<div align="center">

# 🐉 Sentinel Drishti

**An on-device AI agent for detecting and preventing sensitive data loss on enterprise laptops.**

[![Tests](https://img.shields.io/badge/tests-62%2F62_passing-22c55e?style=flat-square)](tests/)
[![F1](https://img.shields.io/badge/controlled_OCR→Entity_F1-1.00-22c55e?style=flat-square)](#evidence)
[![Dataset](https://img.shields.io/badge/eval_dataset-540_images-22c55e?style=flat-square)](#evidence)
[![Offline](https://img.shields.io/badge/core-100%25_offline-22c55e?style=flat-square)](#zero-cloud)
[![Snapdragon](https://img.shields.io/badge/Snapdragon-QNN%20%2F%20HTP_target-e2231a?style=flat-square)](#snapdragon-validation)

<br>

[![Showcase](https://img.shields.io/badge/🌐_Showcase-Hugging%20Face-yellow?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/spaces/kuchvo/Sentinel-Drishti)
[![Live Demo](https://img.shields.io/badge/💻_Live_Demo-Streamlit-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)](https://sentinel-drishti-kgxhnyuna9wmtswppmgmze.streamlit.app/)
[![GitHub](https://img.shields.io/badge/📦_Source-GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Nir-bitcoin/Sentinel-Drishti)

<br>

**SusDetect Team** — by **Niranjan Vishe**

Snapdragon AI Lab Build & Present Challenge 2026

</div>

---

# 30-Second Overview

> **The problem:** sensitive information can leave an enterprise laptop through ordinary actions such as `COPY → Clipboard → Gmail`.
>
> **The approach:** Sentinel Drishti combines data sensitivity, user behavior, destination and session context before making a DLP decision.
>
> **The key idea:** spend AI compute only when security context justifies it.

| Metric                    |          Result | Scope                                  |
| :------------------------ | --------------: | :------------------------------------- |
| **Automated tests**       |       **62/62** | 25 unit + 33 security + 4 end-to-end   |
| **Control-plane latency** | **8.03 ms P50** | Measured control path, no OCR          |
| **OCR → Entity macro F1** |        **1.00** | 540 controlled labeled images          |
| **Cold OCR**              |        **~9 s** | CPU, after ROI optimization            |

> **Metric scope matters:** 8.03 ms is the measured control plane, not full OCR latency. The 1.00 F1 result comes from a controlled 540-image regression evaluation and is not presented as general real-world accuracy.

<div align="center">

[🎥 **Demo Video**](#demo-video) · [💻 **Live Dashboard**](https://sentinel-drishti-kgxhnyuna9wmtswppmgmze.streamlit.app/) · [🌐 **Showcase**](https://huggingface.co/spaces/kuchvo/Sentinel-Drishti) · [📚 **Documentation**](#documentation)

</div>

---

# The Story

Enterprise laptops can contain sensitive information such as PAN numbers, salary records, phone numbers, confidential contracts and internal documents.

A data-loss event does not always look like a sophisticated cyberattack.

Sometimes it looks like normal work:

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
```

No malware is required.

No complicated exploit is required.

The individual actions can look ordinary. The security meaning appears when the system connects the **data**, **action**, **application**, **destination** and **session history**.

That is the problem Sentinel Drishti is designed to address.

---

# The Solution

Sentinel Drishti is a local-first DLP agent that evaluates **context before enforcement**.

It asks:

```
What data is involved?
        +
What is the user doing?
        +
Where is the data going?
        +
What happened earlier?
        ↓
DLP decision
```

The policy engine then produces:

```
ALLOW / WARN / BLOCK
```

The system connects AI-based perception with behavioral context and deterministic policy enforcement while keeping the core DLP processing on the endpoint.

---

# Demo

The central scenario is intentionally simple:

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

The important part is not just detecting salary information.

The system detects **how the information is moving**.

### Benign Flow

```
Team meeting notes
        ↓
       Word
        ↓
       READ
        ↓
      LOCAL
        ↓
   No external flow
        ↓
      ALLOW
```

### Example Policy Outcomes

| Situation                               |  Decision |
| :-------------------------------------- | :-------: |
| Sensitive data → local `COPY`           | **ALLOW** |
| Sensitive data → Gmail → `PASTE`        | **BLOCK** |
| Sensitive data → Google Drive → `PASTE` |  **WARN** |
| Confidential file → local `READ`        | **ALLOW** |

This is what makes Sentinel Drishti a **context-driven DLP system**, rather than a sensitive-text detector alone.

---

# Core Innovation

The project is built around three main ideas.

## 1. Context-Driven DLP ⭐

A sensitive value does not automatically mean a violation.

Sentinel Drishti combines:

```
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

This allows the policy engine to distinguish a local copy from a cross-application external transfer.

---

## 2. Event-Driven AI Compute ⭐

The system does not spend the same amount of compute on every frame.

```
L0
No relevant security event
        ↓
Skip OCR

L1
Suspicious event
        ↓
Fast OCR

L2
Critical event
        ↓
Precise ROI OCR
+
Coverage check
```

In the measured workload, **70% of frames take the L0 path**, avoiding unnecessary OCR work.

The design goal is simple:

> **Spend AI compute only when security context justifies it.**

---

## 3. Data Flow + Session Risk ⭐

Instead of treating every event independently, Sentinel Drishti connects related activity:

```
Excel
  ↓
Clipboard
  ↓
Gmail
```

A session-level risk engine then accumulates context across related actions.

For example:

```
COPY
  ↓
Gmail
  ↓
PASTE
```

has a different security context from a single local `COPY`.

### Additional security mechanisms

* **Two-stage ROI OCR** — fast recognition followed by precise re-recognition of selected low-confidence regions.
* **L2 coverage gate** — critical events can escalate when the initial pass does not provide sufficient sensitive-entity coverage.
* **Privacy-preserving audit** — sensitive content is masked before recording and audit entries use a SHA-256 hash chain.
* **Rule-based intent** — deterministic, auditable intent rules rather than a second black-box classifier.
* **Physical alerting** — Arduino UNO Q with LED/buzzer output and software fallback.

---

# Architecture

Sentinel Drishti is organized as a 12-stage pipeline:

```
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

## Compute Policy

### L0 — No Security Event

No relevant security activity is present.

OCR is skipped.

### L1 — Suspicious Event

Used for events such as:

```
COPY
PASTE
```

The faster recognition path is used.

### L2 — Critical Event

Used for higher-risk actions such as:

```
USB
UPLOAD
EMAIL
```

The system can use precise ROI recognition and the coverage check.

```
Critical event
      ↓
Precise ROI OCR
      ↓
Coverage check
      ↓
Stronger fallback when required
```

---

# Evidence

Everything in this section is tied to the project's listed test or evaluation setups.

## 62/62 Automated Tests

**62/62 means 62 automated tests passed:**

```
Unit tests ............... 25/25 passing
Security tests ........... 33/33 passing
End-to-end tests ......... 4/4 passing
-----------------------------------------
Total .................... 62/62 passing
```

## OCR → Entity Evaluation

**540 controlled labeled images**

```
PAN ................ Precision 1.00 · Recall 1.00 · F1 1.00
PHONE .............. Precision 1.00 · Recall 1.00 · F1 1.00
FINANCIAL .......... Precision 1.00 · Recall 1.00 · F1 1.00
CONFIDENTIAL ....... Precision 1.00 · Recall 1.00 · F1 1.00

Macro average ...... Precision 1.00 · Recall 1.00 · F1 1.00
False positives .... 0
False negatives .... 0
```

> **Scope:** controlled regression evaluation on 540 labeled images. This is not a claim of general real-world accuracy.

### Dataset Composition

| Category               | Count |
| :--------------------- | ----: |
| PAN patterns           |    90 |
| Phone patterns         |    90 |
| Financial patterns     |    90 |
| Confidential markings  |    72 |
| Benign (no PII)        |    90 |
| Mixed multi-entity     |   108 |
| **Total**              | **540** |

The dataset is generated deterministically through `evaluation/make_test_images.py` with ground-truth labels in `evaluation/dataset_manifest.csv`.

## CPU Performance

```
Unchanged screen .......... ~8 ms P50   (control plane, no OCR)
Cached screen ............. ~3 ms P50   (SHA-256 hash lookup)
Cold OCR .................. ~9 s        (after ROI optimization)
Final OCR confidence ...... 0.968
```

The measured cold OCR path was reduced from the earlier 15–16 second range after ROI optimization.

## Stage-Level Control Plane

Measured over 20 runs per stage:

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
-----------------------------------------
TOTAL control plane ....... 8.03 ms P50
```

Run the breakdown locally:

```powershell
python scripts\latency_breakdown.py
```

---

# Rule-Based Intent Engine

The intent layer is deliberately **rule-based**.

The AI-heavy part of the pipeline handles perception such as OCR and entity detection. Policy reasoning remains deterministic so that the final decision can be explained.

Example:

```
Intent: BENIGN
Matched rules: NONE
Evidence level: LOW
```

High-risk example:

```
Intent: EXFILTRATION
Matched rules: PII_001, FIN_001
Evidence level: HIGH
```

The evidence level is derived from the policy rules that fired.

No additional probabilistic intent score is fabricated.

---

# Privacy & Audit

The audit layer is designed to retain security evidence without storing raw sensitive values.

Example:

```
Original:
ABCD1234F

Audit summary:
ABCD****F
```

Audit entries are connected using a **SHA-256 hash chain** so modifications can be detected.

Core audit processing remains local.

---

# Snapdragon Validation

Sentinel Drishti targets:

**Snapdragon QNN / Hexagon HTP**

The Snapdragon evidence is intentionally separated into distinct tiers.

## Three-Tier Evidence Model

| Tier  | Evidence                                      | Environment                                   |
| :---- | :-------------------------------------------- | :-------------------------------------------- |
| **A** | QNN / Hexagon HTP target runtime              | Snapdragon target architecture                |
| **B** | EasyOCR detector and recognizer benchmarks    | Qualcomm AI Hub hosted Snapdragon X Elite NPU |
| **C** | Complete Sentinel Drishti end-to-end pipeline | Local CPU development environment             |

This avoids combining component-level NPU measurements with full-pipeline CPU timings.

## Tier B — Qualcomm AI Hub

Snapdragon-targeted EasyOCR components were compiled and benchmarked through Qualcomm AI Hub:

```
EasyOCR detector (w8a8) ...... 12.64 ms  · NPU
EasyOCR recognizer (w8a8) .... 10.55 ms  · NPU
```

These are **component-level Snapdragon measurements**, not end-to-end Sentinel Drishti latency.

## Cross-Platform Runtime

The runtime supports backend selection across environments:

```
Standard / development host
        ↓
    CPU backend

Snapdragon host
        ↓
QNN / Hexagon HTP backend
```

Automatic backend selection can use CPU fallback when the requested Snapdragon backend is unavailable.

## Backend Selection

```powershell
python sentinel.py --backend qnn     # Request QNN / HTP
python sentinel.py --backend cpu     # Force CPU
python sentinel.py --backend auto    # Auto-detect
```

Full validation notes:

[docs/snapdragon_validation.md](docs/snapdragon_validation.md)

## Reproduce the AI Hub Benchmark

```bash
pip install qai-hub qai-hub-models
qai-hub configure --api_token YOUR_TOKEN
qai-hub-models perf easyocr
```

---

# Evaluation Criteria

The challenge lists four evaluation areas. The README maps the implementation and evidence to each area without assigning unofficial weights.

| Criterion                             | Evidence in Sentinel Drishti                                                                                                                                                         | README evidence                                                                                                              |
| :------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------- |
| **Technical Implementation**          | 12-stage DLP pipeline, L0/L1/L2 policy, ROI OCR, entity detection, behavior tracking, data-flow graph, session risk, rule-based intent, DLP engine, audit chain and Arduino alerting | [Architecture](#architecture) · [Evidence](#evidence)                                                                        |
| **Application Use Case & Innovation** | Enterprise DLP scenario, context-driven decisions, cross-application data flow, session-level risk and event-driven compute                                                          | [The Story](#the-story) · [Demo](#demo) · [Core Innovation](#core-innovation)                                                |
| **Deployment & Accessibility**        | Local runtime, CPU execution, QNN/HTP target support, automatic backend selection, offline operation, Streamlit dashboard and Hugging Face showcase                                  | [Deployment & Accessibility](#deployment--accessibility) · [Snapdragon Validation](#snapdragon-validation) · [Setup](#setup) |
| **Presentation & Documentation**      | Reproducible tests, benchmark methodology, architecture documentation, security documentation, Snapdragon validation notes and visual showcase                                       | [Evidence](#evidence) · [Documentation](#documentation)                                                                      |

---

# Zero Cloud

The **core DLP pipeline** is designed to run without cloud processing of protected content.

```
Internet required ....... NO
Cloud API required ...... NO
OCR processing .......... LOCAL
Entity detection ........ LOCAL
Risk engine ............. LOCAL
DLP policy .............. LOCAL
Audit chain ............. LOCAL
```

Offline verification blocks socket calls before the full pipeline is executed:

```powershell
python tests/test_offline.py
```

Expected result:

```
Blocking all network calls...
Network block: ACTIVE

Full pipeline ran with ZERO network calls.

============================================================
  OFFLINE VERIFICATION: PASS
============================================================
```

---

# Deployment & Accessibility

Sentinel Drishti can be explored through several interfaces.

### Local Runtime

Run the pipeline directly with the unified launcher and verification scripts.

### Streamlit Dashboard

Interactive scenarios, decisions, entities, data flow and audit output:

https://sentinel-drishti-kgxhnyuna9wmtswppmgmze.streamlit.app/

### Hugging Face Showcase

Visual project overview, architecture and evidence:

https://huggingface.co/spaces/kuchvo/Sentinel-Drishti

### Backend Flexibility

The runtime can operate using the CPU development path and is structured for Snapdragon QNN/HTP execution when the appropriate environment is available.

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
* OCR/entity evaluation on 540 images
* Performance measurements

---

# Repository Structure

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
├── evaluation/        540-image OCR → entity evaluation
│                      (make_test_images.py, dataset_manifest.csv,
│                       run_ocr_entity_eval.py, ocr_entity_report.json)
├── demo_scenarios/    5 YAML scenarios
├── docs/              documentation
├── sentinel.py        unified launcher
├── setup.ps1
├── run.ps1
├── setup.sh
├── run.sh
└── app.py             Streamlit dashboard
```

The codebase is separated into modules so individual components can be tested or replaced independently.

---

# Roadmap

* Physical Snapdragon X Elite validation of the complete pipeline
* Direct QNN-compiled EasyOCR deployment on-device
* Native OS-level clipboard and USB interception
* Multi-language OCR beyond English
* MDM integration for enterprise fleet deployment

---

# Demo Video

The recommended demonstration flow is:

```
Problem
   ↓
Excel → Clipboard → Gmail
   ↓
BLOCK_AND_ALERT
   ↓
Streamlit dashboard
   ↓
Architecture / innovation
   ↓
Snapdragon validation
   ↓
GitHub tests and evidence
```

**Demo video:** add the final video link here after upload.

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
