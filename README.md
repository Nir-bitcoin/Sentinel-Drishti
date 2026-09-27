<div align="center">

<img src="https://img.shields.io/badge/-SNAPDRAGON%20AI%20LAB%202026-e2231a?style=for-the-badge&logo=qualcomm&logoColor=white" alt="Snapdragon AI Lab 2026" />

# 🛡️ Sentinel Drishti

### On-Device AI Data Loss Prevention Agent for Snapdragon-Powered PCs

**Target Runtime:** Snapdragon QNN / Hexagon NPU · **Validation:** Local CPU · **Core:** 100% Offline

<br>

[![Clone](https://img.shields.io/badge/⚡_Clone_%26_Run-One_Command-22c55e?style=for-the-badge&logo=git&logoColor=white)](#-one-command-setup)
[![Demo](https://img.shields.io/badge/🎬_Watch-Demo_Video-e2231a?style=for-the-badge&logo=youtube&logoColor=white)](#)
[![Showcase](https://img.shields.io/badge/🌐_View-Showcase_Site-3b82f6?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/spaces/kuchvo/Sentinel-Drishti)

<br>

[![CI](https://img.shields.io/github/actions/workflow/status/Nir-bitcoin/Sentinel-Drishti/demo.yml?style=flat-square&label=CI&logo=github)](https://github.com/Nir-bitcoin/Sentinel-Drishti/actions)
[![Tests](https://img.shields.io/badge/tests-62%2F62_passing-22c55e?style=flat-square&logo=pytest&logoColor=white)](tests/)
[![F1](https://img.shields.io/badge/OCR→Entity_F1-1.00-22c55e?style=flat-square)](#-measured-evidence)
[![Offline](https://img.shields.io/badge/core-100%25_offline-22c55e?style=flat-square&logo=windows&logoColor=white)](#-zero-cloud-core)
[![Python](https://img.shields.io/badge/python-3.10+-3b82f6?style=flat-square&logo=python&logoColor=white)](#-quick-start)
[![License](https://img.shields.io/badge/license-MIT-64748b?style=flat-square)](LICENSE)

</div>

---

## ⚡ In 30 Seconds

- ✅ **All core workloads run entirely on the edge device** — zero cloud calls, zero API keys
- ✅ **Heterogeneous compute** — CPU + QNN/Hexagon NPU dispatch via `get_backend_with_fallback()`
- ✅ **Three-tier compute policy** — L0 skip · L1 fast OCR · L2 precise OCR
- ✅ **Event-driven** — 70% of frames skip OCR at **3.93 ms P50** control plane
- ✅ **Two-stage ROI OCR** — 40% faster cold path (15 s → 9 s CPU)
- ✅ **Data flow graph** — tracks Excel → Clipboard → Gmail patterns across apps
- ✅ **Session risk engine** — accumulates insider-threat signals
- ✅ **Privacy-preserving audit** — SHA-256 chain, raw PII never stored
- ✅ **EasyOCR components validated on Snapdragon X Elite NPU** — 12.64 ms detector, 10.55 ms recognizer (w8a8)
- ✅ **62/62 tests passing** · OCR → Entity F1 = **1.00**

---

## ✨ Key Features

- **🎯 Event-Driven OCR** — OCR runs only on COPY / PASTE / USB events, not every frame. 70% of frames skip OCR entirely at 3.93 ms P50 overhead.
- **🔬 Two-Stage ROI OCR** — Fast pass on full image, precise re-recognition only on low-confidence regions. **40% faster cold path.**
- **🛡️ Coverage Gate (L2)** — On critical events, if OCR misses sensitive entities, escalates to full precise OCR. Safety net.
- **🔀 Data Flow Graph** — Tracks Excel → Clipboard → Gmail patterns across apps. Exfiltration reasoning, not just event detection.
- **📈 Session Risk Engine** — Accumulates weighted risk across a session. Catches insider-threat patterns single events miss.
- **🔒 Privacy-Preserving Audit** — SHA-256 hash chain, raw PII never stored — only masked summary (`ABCD****F`).
- **🚨 Physical Alerting** — Arduino UNO Q LED + buzzer, with software fallback when hardware absent.
- **⚡ Snapdragon QNN Ready** — Auto-selects Hexagon NPU when available. **EasyOCR components benchmarked** on hosted Snapdragon X Elite (12.64 ms detector · 10.55 ms recognizer · w8a8).
- **🧪 62/62 Tests Passing** — 25 unit · 33 security · 4 end-to-end.
- **📊 OCR → Entity F1 = 1.00** — 30 labeled images, zero FP, zero FN.

---

<div align="center">

### Three-tier evidence model

| Tier | Evidence | Source | Status |
|:---:|:---|:---|:---:|
| **A** | Snapdragon QNN/HTP target architecture | QNN backend | 🎯 Target |
| **B** | EasyOCR component benchmarks on Snapdragon X Elite NPU | Qualcomm AI Hub (hosted) | ✅ Validated |
| **C** | End-to-end pipeline validation | Local CPU | ✅ Measured |

*Tiers are never merged into a single number.*

</div>

---

## 📖 Table of Contents

- [In 30 Seconds](#-in-30-seconds)
- [Key Features](#-key-features)
- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [Heterogeneous Compute Design](#-heterogeneous-compute-design)
- [Built with Qualcomm AI Hub](#-built-with-qualcomm-ai-hub)
- [Target Platform](#-target-platform)
- [Team](#-team)
- [Why This Is Novel](#-why-this-is-novel)
- [Measured Evidence](#-measured-evidence)
- [Development Flow](#-development-flow)
- [Tech Stack](#-tech-stack)
- [Social Impact](#-social-impact)
- [One-Command Setup](#-one-command-setup)
- [Deployment Modes](#-deployment-modes)
- [Architecture](#-architecture)
- [Verifying the Setup](#-verifying-the-setup)
- [Environment Variables](#-environment-variables)
- [Target Users](#-target-users)
- [Regulatory Context](#-regulatory-context)
- [Zero-Cloud Core](#-zero-cloud-core)
- [Compatibility Matrix](#-compatibility-matrix)
- [Known Issues](#-known-issues)
- [Notes](#-notes)
- [Future Work](#-future-work)
- [Documentation](#-documentation)
- [References](#-references)
- [Challenge](#-challenge)

---

## 🎯 The Problem

Employees on enterprise PCs handle **PAN numbers, salaries, phone numbers, and confidential documents** every day. Most data leaks are not sophisticated attacks — they are a single copy-paste to Gmail, a USB drive plugged in at 5 PM, or an upload to Google Drive.

Existing DLP tools fail on three fronts:

| # | Failure mode | Impact |
|:-:|:---|:---|
| 1 | **Cloud-based** | Data leaves the device to be scanned. Privacy violation. |
| 2 | **Server-heavy** | Enterprises pay per-endpoint, per-month, per-GB. |
| 3 | **Frame-blind** | Watch nothing, or watch everything — draining battery on all-day-use laptops. |

---

## 💡 The Solution

**Sentinel Drishti runs entirely on-device.** It watches only when security context justifies the compute, and produces tamper-evident audit decisions with physical alerting.

<div align="center">

> ### *"Spend AI compute only when security context justifies it."*
>
> — Central engineering principle

</div>

---

## 🖥️ Heterogeneous Compute Design

Sentinel Drishti distributes workloads across available compute units using the
Snapdragon heterogeneous computing model — **CPU for orchestration and policy,
NPU for perception inference**.

| Compute unit | Workload | Target |
|:---|:---|:---|
| **NPU (Hexagon HTP)** | EasyOCR detector + recognizer inference | Snapdragon X Elite |
| **CPU** | Event policy · DLP engine · risk scorer · audit chain · session risk · data flow graph | Any host |
| **GPU** | (Available for future CV preprocessing) | Snapdragon X Elite |

**Backend selection logic:**

```
        Sentinel Runtime
               │
      get_backend_with_fallback()
               │
       ┌───────┴───────┐
       │               │
  QNN available?    Not available
       │               │
   QNNBackend      CPUBackend
       │               │
  Hexagon NPU    Local CPU
```

**Manual override:**

```powershell
python sentinel.py --backend qnn     # Target Snapdragon runtime
python sentinel.py --backend cpu     # Development / validation
python sentinel.py --backend auto    # Default — auto-detect
```

When QNN is unavailable (e.g., on the development laptop), the runtime falls
back to CPU automatically with a **visible reason** — never silently.

---

## 🏭 Built with Qualcomm AI Hub

Sentinel Drishti uses **EasyOCR** as its primary perception engine.
The EasyOCR detector and recognizer were compiled and benchmarked on
hosted **Snapdragon X Elite** devices via Qualcomm AI Hub.

### EasyOCR — Snapdragon X Elite NPU Benchmarks

Source: Qualcomm AI Hub · `qai-hub-models perf easyocr` · QAIRT 2.50.0 · Hexagon v73.

| Precision | Runtime | Component | Latency | Peak Mem | Compute |
|:---:|:---|:---|:---:|:---:|:---:|
| float | ONNX Runtime | Detector | 35.75 ms | 36 MB | NPU |
| float | QAIRT DLC | Detector | 39.49 ms | 6 MB | NPU |
| float | ONNX Runtime | Recognizer | 18.84 ms | 11 MB | NPU |
| float | QAIRT DLC | Recognizer | 19.34 ms | 0 MB | NPU |
| **w8a8** | ONNX Runtime | **Detector** | **12.64 ms** | 20 MB | **NPU** |
| **w8a8** | ONNX Runtime | **Recognizer** | **10.55 ms** | 10 MB | **NPU** |

> **Best-case total: ~23 ms** for full EasyOCR pipeline (w8a8 quantized) on
> the Hexagon NPU. This is the deployment target for the QNN backend.
> Not an end-to-end Sentinel timing.

### Reproducing These Benchmarks

```bash
pip install qai-hub qai-hub-models
qai-hub configure --api_token YOUR_TOKEN
qai-hub-models perf easyocr
```

### Extended AI Hub Catalog — Future Pipeline Extensions

The following models were benchmarked to document the AI Hub catalog
for **potential future extensions** of Sentinel Drishti. They are **not**
currently part of the Sentinel pipeline.

| Model | Precision | Latency | Compute | Potential Future Role |
|:---|:---:|:---:|:---:|:---|
| YOLOv8-Detection | w8a8 | 1.58 ms | NPU | Scene understanding |
| YOLOv11-Detection | float | 6.30 ms | NPU | Alternative detector |
| MobileNetV3-Large | w8a8 | 0.53 ms | NPU | Lightweight classification |
| ResNet18 | w8a8 | 0.50 ms | NPU | Baseline vision |
| Whisper-Small (decoder) | w8a16 | 7.17 ms | NPU | Audio DLP |
| Whisper-Small (encoder) | w8a16 | 60.24 ms | NPU | Audio encoding |
| Qwen3-1.7B | q4_0 | 11.9 tok/s | NPU | LLM intent classification |
| Qwen3-4B-Instruct | q4_0 | 6.1 tok/s | NPU | Advanced reasoning |

**These are catalog benchmarks — ecosystem evidence, not Sentinel execution proof.**

---

## 🐉 Target Platform

Sentinel Drishti is designed for **Snapdragon QNN / Hexagon HTP** — the
target production runtime for Snapdragon-powered HP PCs.

```
        Sentinel Runtime
               │
      QNN Execution Provider
               │
   Hexagon Tensor Processor (NPU)
```

When QNN is unavailable (e.g., on a development laptop), the runtime falls
back to CPU with a **visible reason**. Every published number is clearly
labelled by tier.

---

## 👥 Team

| Member | Role | Contact |
|:---|:---|:---|
| **[Niranjan vishe]** | Solo developer · full pipeline: perception, DLP engine, audit chain, backend routing, UI, tests | **[niranjanvishe62@email.com]** |

---

## ✨ Why This Is Novel

| Feature | Why it matters |
|:---|:---|
| **🎯 Event-driven OCR** | OCR runs on COPY/PASTE/USB events, not every frame. **70% of frames skip OCR** at 3.93 ms P50 overhead. |
| **🔬 Two-stage ROI OCR** | Fast pass on full image, precise re-recognition only on low-confidence regions. **40% faster cold path.** |
| **🛡️ Coverage gate (L2)** | On critical events, if OCR misses sensitive entities, escalates to full precise OCR. Safety net. |
| **🔀 Data flow graph** | Tracks Excel → Clipboard → Gmail patterns across apps. **Exfiltration reasoning**, not just event detection. |
| **📈 Session risk engine** | Accumulates weighted risk across a session. Catches insider-threat patterns single events miss. |
| **🔒 Privacy-preserving audit** | SHA-256 hash chain. Raw PII **never** stored — only masked summary (`ABCD****F`). |
| **🚨 Physical alerting** | Arduino UNO Q: LED + buzzer. Software fallback when hardware absent. |
| **⚡ Honest Snapdragon story** | QNN backend ready. EasyOCR components validated on hosted Snapdragon X Elite. Three-tier evidence. **No fake NPU numbers.** |

---

## 📊 Measured Evidence

### Test Suite

| Type | Count | Status |
|:---|:---:|:---:|
| Unit tests | 25 | ✅ |
| Security tests | 33 | ✅ |
| End-to-end tests | 4 | ✅ |
| **Total** | **62** | **✅ 62/62** |

### OCR → Entity Evaluation (30 labeled images)

| Entity | Precision | Recall | F1 | TP | FP | FN |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| PAN | 1.00 | 1.00 | **1.00** | 10 | 0 | 0 |
| PHONE | 1.00 | 1.00 | **1.00** | 8 | 0 | 0 |
| EMPLOYEE_FINANCIAL_DATA | 1.00 | 1.00 | **1.00** | 9 | 0 | 0 |
| CONFIDENTIAL_MARKING | 1.00 | 1.00 | **1.00** | 7 | 0 | 0 |
| **Macro average** | **1.00** | **1.00** | **1.00** | 34 | **0** | **0** |

### Performance

| Metric | Value | Tier |
|:---|:---:|:---:|
| L0 control plane | 3.93 ms P50 | C |
| Cache hit | ~3 ms P50 | C |
| Cold OCR (CPU) | ~9 s (was 15–16 s before ROI) | C |
| Final OCR confidence | 0.968 | C |
| EasyOCR detector (NPU w8a8) | 12.64 ms | B |
| EasyOCR recognizer (NPU w8a8) | 10.55 ms | B |

> Tier B numbers are **hosted Snapdragon X Elite NPU benchmarks** from Qualcomm AI Hub — not end-to-end Sentinel timings on physical hardware.

### Stage-Level Latency Breakdown (Control Plane)

Measured on development host (Windows AMD64, CPU). 20 runs per stage.
These timings apply to the **70% of frames where OCR is skipped** (L0 path).

| Stage | P50 | P95 | P99 |
|:---|---:|---:|---:|
| Change Detection | 0.15 ms | 1.92 ms | 1.92 ms |
| Event Policy (L0/L1/L2) | 0.002 ms | 0.009 ms | 0.009 ms |
| Entity Detection (regex) | 0.008 ms | 0.27 ms | 0.27 ms |
| Behavior Tracking | 0.011 ms | 0.05 ms | 0.05 ms |
| Risk Scoring | 0.001 ms | 0.008 ms | 0.008 ms |
| Data Flow Graph | 0.016 ms | 0.056 ms | 0.056 ms |
| Session Risk Engine | 0.009 ms | 0.028 ms | 0.028 ms |
| Intent Classification | 0.001 ms | 0.005 ms | 0.005 ms |
| DLP Decision | 1.06 ms | 3.68 ms | 3.68 ms |
| Privacy Masking | 0.007 ms | 0.36 ms | 0.36 ms |
| Audit Chain Write | 2.66 ms | 3.24 ms | 3.24 ms |
| **TOTAL (control plane)** | **3.93 ms** | **9.64 ms** | **9.64 ms** |

> Full report: `latency_report.json` (generated by `scripts/latency_breakdown.py`).
> This is the *control plane* — the path taken by 70% of frames where the
> screen is unchanged or no security event fires. OCR is skipped entirely.

---

## 🛠️ Development Flow

1. **Defined the problem** — enterprise data leaks via copy-paste, USB, cloud
2. **Designed event-driven architecture** — L0/L1/L2 compute policy
3. **Selected EasyOCR** — bundled model, no cloud inference
4. **Optimized perception** — two-stage ROI OCR, content-hash cache
5. **Built reasoning layer** — data flow graph + session risk engine
6. **Enforced DLP policy** — three-tier ALLOW/WARN/BLOCK + tamper-evident audit
7. **Validated component performance** — Qualcomm AI Hub hosted benchmarks
8. **Tested end-to-end** — 62 tests, 30-image F1=1.00 evaluation
9. **Documented honestly** — three-tier evidence model, no fake NPU numbers

---

## 💻 Tech Stack

| Component | Technology | Why |
|:---|:---|:---|
| **Target runtime** | Snapdragon QNN / Hexagon NPU | On-device acceleration |
| **Dev runtime** | CPU (PyTorch) | Validation + fallback |
| **OCR engine** | EasyOCR | Bundled model, no cloud |
| **OCR pipeline** | Two-stage ROI | 40% faster cold path |
| **Cache** | Content-hash LRU | ~3 ms hits |
| **DLP engine** | Rule-based + YAML policy | Configurable, auditable |
| **Audit** | SHA-256 hash chain | Tamper-evident |
| **Alerts** | Arduino UNO Q (LED + buzzer) | Physical feedback |
| **Dashboard** | Streamlit | Local interactive UI |
| **Showcase** | Hugging Face Static | Public landing page |
| **Launcher** | Python CLI (`sentinel.py`) | One-command unified entry |
| **Model toolchain** | Qualcomm AI Hub | NPU compilation + benchmarking |

---

## 🌍 Social Impact

**For enterprises:** Prevent regulatory breaches (DPDP Act, GDPR, HIPAA)
without sending a single byte to the cloud.

**For employees:** Protects them from accidental leaks without invasive
surveillance — masked audit, no raw content retention.

**For India:** With 5.8M+ developers and a strict data-residency policy,
on-device DLP is a national priority for BFSI, healthcare, and government.

**For the ecosystem:** Demonstrates that a production-grade security
workload can run on Snapdragon NPUs without any cloud dependency.

---

## ⚡ One-Command Setup

<div align="center">

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

### Or use the launcher directly

```bash
python sentinel.py
```

</div>

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

## 🚀 Deployment Modes

Sentinel Drishti is designed for **Snapdragon QNN / Hexagon HTP**. The runtime auto-selects the best available backend.

### 🎯 1. Snapdragon QNN/HTP — Primary Target

```powershell
python sentinel.py --backend qnn
```

The QNN backend selects automatically when the Snapdragon QNN Execution Provider is available. This is the **target production runtime** for Snapdragon-powered HP PCs.

### 🏭 2. Qualcomm AI Hub — EasyOCR Component Benchmarks

| Component | Precision | Latency | Compute |
|:---|:---:|:---:|:---:|
| EasyOCR detector | w8a8 | **12.64 ms** | NPU |
| EasyOCR recognizer | w8a8 | **10.55 ms** | NPU |

These are **hosted component benchmarks** for the EasyOCR models used in
the Sentinel pipeline — not end-to-end Sentinel timings on physical hardware.

### 💻 3. CPU Fallback — Development & Validation

```powershell
python sentinel.py --backend cpu
```

When QNN is unavailable, the runtime falls back to CPU automatically with a visible reason. This is how the pipeline is **validated end-to-end** on the development machine.

---

## 🏗️ Architecture

See [docs/architecture.md](docs/architecture.md) for the full pipeline.

```
                        SENTINEL DRISHTI
                               │
                        Screen / Event
                               │
                       Change Detector
                        +------+------+
                        |             |
                    Unchanged      Changed
                        |             |
                      SKIP      Event Policy
                                       │
                        +--------------+--------------+
                        |              |              |
                       L0             L1             L2
                     Skip OCR      Fast OCR      Precise ROI OCR
                                       |              |
                                       +------+-------+
                                              │
                                   Two-Stage ROI OCR
                                              │
                                     OCR Cache (LRU)
                                       content-hash
                                              │
                                     Entity Detection
                             (PAN · Phone · Aadhaar · Financial · Confidential)
                                              │
                             Behavior Tracker + Data Flow Graph
                                              │
                               Risk Engine + Session Risk
                                              │
                                     Intent Classifier
                        (BENIGN / CONFIDENTIAL_ACCESS / EXFILTRATION)
                                              │
                                   DLP Policy Engine
                        +--------------+--------------+
                        |              |              |
                      ALLOW          WARN           BLOCK
                        |              |              |
                        ▼              ▼              ▼
                      Audit      User Confirm    Audit + Arduino
```

### Component Breakdown

| Component | Purpose |
|:---|:---|
| **Change Detector** | Skip everything if screen unchanged |
| **Event Policy** | Decide L0 (skip) / L1 (fast OCR) / L2 (precise OCR) |
| **Two-Stage ROI OCR** | Fast pass + precise re-crop on low-confidence regions |
| **LRU Cache** | Content-hash, 100 entries, ~3 ms hits |
| **Entity Detection** | PAN · Phone · Aadhaar · Financial · Confidential |
| **Behavior Tracker** | COPY/PASTE/USB sequences |
| **Data Flow Graph** | Cross-app tracking (Excel → Gmail) |
| **Risk Engine** | 0-100 policy score |
| **Session Risk** | Accumulates weighted risk over session |
| **Intent Classifier** | BENIGN / CONFIDENTIAL_ACCESS / EXFILTRATION |
| **DLP Policy Engine** | YAML-configurable (`config/policy.yaml`) |
| **Audit Chain** | SHA-256 tamper-evident, masked PII |
| **Arduino Alert** | LED + buzzer with software fallback |

---

## 🧪 Verifying the Setup

Run each layer independently — cheapest first.

```powershell
# 1. Unit tests (25 tests)
python tests/test_pipeline.py

# 2. Security tests (33 tests)
python tests/test_security_deep.py

# 3. End-to-end tests (4 tests)
python tests/test_e2e.py

# 4. Offline verification (blocks all sockets)
python tests/test_offline.py

# 5. Health check (12 components)
python scripts/health_check.py

# 6. Deployment check (13 validations)
python scripts/deployment_check.py

# 7. Scenario runner (5 deterministic scenarios)
python scripts/run_scenario.py --all

# 8. OCR → Entity evaluation (30 images)
python evaluation/run_ocr_entity_eval.py

# 9. Stage-level latency breakdown
python scripts/latency_breakdown.py
```

**Expected results:**

| Check | Expected |
|:---|:---|
| Unit tests | `25/25 passing` |
| Security tests | `33/33 passing` |
| E2E tests | `4/4 passing` |
| Offline verification | `PASS` (zero network calls) |
| Health check | `12/12 PASS` |
| Deployment check | `13/13 READY` |
| Scenarios | `5/5 passed` |
| OCR → Entity F1 | `1.00` (0 FP, 0 FN) |
| Control plane P50 | `3.93 ms` |

---

## ⚙️ Environment Variables

All optional — the pipeline runs with sensible defaults.

| Variable | Purpose | Default |
|:---|:---|:---|
| `SENTINEL_BACKEND` | `qnn` / `cpu` / `auto` | `auto` |
| `SENTINEL_POLICY_PATH` | Custom policy YAML | `config/policy.yaml` |
| `SENTINEL_AUDIT_DIR` | Audit log directory | `audit_logs` |
| `SENTINEL_ARDUINO_PORT` | Arduino serial port | `COM3` |
| `SENTINEL_DEMO_MODE` | Skip heavy OCR (cloud demo) | `0` |

---

## 👥 Target Users

| User | Why |
|:---|:---|
| **Enterprise IT / security teams** | Protect HR, finance, legal departments |
| **Compliance officers** | GDPR, DPDP Act (India), HIPAA, SOX |
| **Snapdragon PC OEMs** | HP, Lenovo, Dell shipping ARM laptops |
| **Regulated industries** | BFSI, healthcare, defence contractors |

---

## 📋 Regulatory Context

| Regulation | Requirement | How Sentinel Drishti helps |
|:---|:---|:---|
| **DPDP Act (India)** | Data minimisation, breach reporting | Raw PII never stored, hash-chained audit |
| **GDPR (EU)** | Article 32 — security of processing | On-device, no cloud egress |
| **HIPAA (US)** | PHI protection | Confidential marking detection |
| **SOX** | Financial record integrity | Employee financial data rules |

---

## 🔒 Zero-Cloud Core

The core DLP pipeline never leaves the device:

```
CORE PIPELINE
─────────────────────────
Internet required:    ❌ NO
Cloud API required:   ❌ NO
OCR processing:       🏠 LOCAL
Entity detection:     🏠 LOCAL
Risk engine:          🏠 LOCAL
DLP policy:           🏠 LOCAL
Audit chain:          🏠 LOCAL
```

**Verified by an automated test that blocks all socket calls:**

```powershell
python tests/test_offline.py
```

Optional network features (Streamlit public demo, GitHub CI) are development tools only. The production runtime is fully on-device.

---

## ✅ Compatibility Matrix

| Environment | OCR | DLP | Backend |
|:---|:---:|:---:|:---|
| **Snapdragon Windows** | Target | ✅ | QNN/HTP |
| Windows x64 CPU | ✅ | ✅ | CPU |
| Linux / macOS | ✅ | ✅ | CPU |
| Arduino connected | ✅ | ✅ | Hardware alert |
| Arduino absent | ✅ | ✅ | Software alert |
| Internet unavailable | ✅ | ✅ | Local |

*"Target" = architecture ready; on-device validation pending hardware.*

---

## ⚠️ Known Issues

| Symptom | Likely cause |
|:---|:---|
| `QNN/HTP: NOT AVAILABLE` | No Snapdragon QNN EP on this host — CPU fallback is expected |
| Cold OCR on CPU takes ~9 s | No NPU available; target is ~23 ms on Hexagon (Tier B) |
| Enforcement is simulated | OS-level hooks not implemented in this prototype |
| Streamlit Cloud memory crash | Free tier RAM limit; use `SENTINEL_DEMO_MODE=1` |
| Script execution blocked (Windows) | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once |

---

## 📝 Notes

**Why event-driven OCR, not frame-driven:** Continuous full-frame OCR drains
battery on all-day-use Snapdragon laptops. Event policy spends compute only
when security context justifies it.

**Why three-tier evidence (A/B/C):** Hardware separation. Tier A is the QNN
target. Tier B is hosted AI Hub component benchmarks. Tier C is local CPU
validation. Never merged into a single number.

**Why data flow graph, not just events:** A single COPY is low-risk.
COPY → Gmail → PASTE becomes exfiltration only when tracked across apps.

**Why masked audit, not raw PII:** The audit log should prove *that* a block
happened, not store *what* was blocked. `ABCD****F`, not `ABCDE1234F`.

**Why SHA-256 hash chain:** `verify_chain()` detects any modification to a
historical event. Tamper-evident, not tamper-proof.

---

## 🔮 Future Work

- Physical Snapdragon X Elite validation of the full pipeline (not just components)
- OS-level clipboard and USB interception (currently simulated)
- QNN-compiled EasyOCR model deployed on-device (compilation pipeline scripted, hardware validation pending)
- Extended model integration (scene detection, audio DLP) once on-device NPU validation completes
- Multi-language OCR beyond English
- MDM integration for enterprise fleet rollout

---

## 📚 Documentation

| File | Purpose |
|:---|:---|
| [docs/architecture.md](docs/architecture.md) | Full pipeline + design principles |
| [docs/benchmark.md](docs/benchmark.md) | Benchmark methodology + results |
| [docs/benchmark_comparison.md](docs/benchmark_comparison.md) | Tier A/B/C comparison |
| [docs/security.md](docs/security.md) | Threat model + security depth |
| [docs/use_cases.md](docs/use_cases.md) | Concrete enterprise scenarios |
| [docs/innovation.md](docs/innovation.md) | What is genuinely novel |
| [docs/snapdragon_validation.md](docs/snapdragon_validation.md) | Honest Snapdragon evidence |

---

## 🔗 References

- [Qualcomm AI Hub](https://aihub.qualcomm.com/) — model benchmarking + compilation
- [QNN SDK](https://www.qualcomm.com/developer/software/qualcomm-ai-engine-direct-sdk) — QAIRT runtime
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) — OCR engine
- [Streamlit](https://streamlit.io/) — dashboard
- [Snapdragon X Elite](https://www.qualcomm.com/products/mobile/snapdragon/pcs) — target hardware

---

<div align="center">

## 🏆 Challenge

**Snapdragon AI Lab Build & Present Challenge 2026**

Presented at Qualcomm's flagship developer competition.

<br>

<img src="https://img.shields.io/badge/-Powered_by-Snapdragon-e2231a?style=for-the-badge&logo=qualcomm&logoColor=white" alt="Powered by Snapdragon" />

<br><br>

**Built with ❤️ for on-device privacy.**

<br>

[![GitHub stars](https://img.shields.io/github/stars/Nir-bitcoin/Sentinel-Drishti?style=social)](https://github.com/Nir-bitcoin/Sentinel-Drishti)
[![GitHub forks](https://img.shields.io/github/forks/Nir-bitcoin/Sentinel-Drishti?style=social)](https://github.com/Nir-bitcoin/Sentinel-Drishti)

</div>