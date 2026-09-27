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

<div align="center">

### Three-tier evidence model

| Tier | Evidence | Source | Status |
|:---:|:---|:---|:---:|
| **A** | Snapdragon QNN/HTP target architecture | QNN backend | 🎯 Target |
| **B** | Snapdragon NPU component benchmarks | Qualcomm AI Hub (hosted) | ✅ Validated |
| **C** | End-to-end pipeline validation | Local CPU | ✅ Measured |

*Tiers are never merged into a single number.*

</div>

---

## 📖 Table of Contents

- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [Target Platform](#-target-platform)
- [Why This Is Novel](#-why-this-is-novel)
- [Measured Evidence](#-measured-evidence)
- [One-Command Setup](#-one-command-setup)
- [Deployment Modes](#-deployment-modes)
- [Architecture](#-architecture)
- [Target Users](#-target-users)
- [Regulatory Context](#-regulatory-context)
- [Zero-Cloud Core](#-zero-cloud-core)
- [Compatibility Matrix](#-compatibility-matrix)
- [Documentation](#-documentation)
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

## 🐉 Target Platform

Sentinel Drishti is designed for **Snapdragon QNN / Hexagon HTP** — the target production runtime for Snapdragon-powered HP PCs.

```
        Sentinel Runtime
               │
      QNN Execution Provider
               │
   Hexagon Tensor Processor (NPU)
```

When QNN is unavailable (e.g., on a development laptop), the runtime falls back to CPU with a **visible reason**. Every published number is clearly labelled by tier.

---

## ✨ Why This Is Novel

| Feature | Why it matters |
|:---|:---|
| **🎯 Event-driven OCR** | OCR runs on COPY/PASTE/USB events, not every frame. **70% of frames skip OCR** at 0.36 ms overhead. |
| **🔬 Two-stage ROI OCR** | Fast pass on full image, precise re-recognition only on low-confidence regions. **40% faster cold path.** |
| **🛡️ Coverage gate (L2)** | On critical events, if OCR misses sensitive entities, escalates to full precise OCR. Safety net. |
| **🔀 Data flow graph** | Tracks Excel → Clipboard → Gmail patterns across apps. **Exfiltration reasoning**, not just event detection. |
| **📈 Session risk engine** | Accumulates weighted risk across a session. Catches insider-threat patterns single events miss. |
| **🔒 Privacy-preserving audit** | SHA-256 hash chain. Raw PII **never** stored — only masked summary (`ABCD****F`). |
| **🚨 Physical alerting** | Arduino UNO Q: LED + buzzer. Software fallback when hardware absent. |
| **⚡ Honest Snapdragon story** | QNN backend ready. CPU fallback visible. Three-tier evidence. **No fake NPU numbers.** |

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
| L0 control plane | 0.36 ms P50 | C |
| Cache hit | ~3 ms P50 | C |
| Cold OCR (CPU) | ~9 s (was 15–16 s before ROI) | C |
| Final OCR confidence | 0.968 | C |
| EasyOCR detector (NPU) | 13.5 ms | B |
| EasyOCR recognizer (NPU) | 10.5 ms | B |

> Tier B numbers are **hosted Snapdragon NPU component benchmarks** from Qualcomm AI Hub — not end-to-end Sentinel timings on physical hardware.

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

### 🏭 2. Qualcomm AI Hub — Component Benchmarks

| Component | Precision | Latency |
|:---|:---:|:---:|
| EasyOCR detector | uint8 | **13.5 ms** |
| EasyOCR recognizer | uint8 | **10.5 ms** |

Hosted Snapdragon NPU measurements for **model components** — not end-to-end Sentinel timings.

### 💻 3. CPU Fallback — Development & Validation

```powershell
python sentinel.py --backend cpu
```

When QNN is unavailable, the runtime falls back to CPU automatically with a visible reason. This is how the pipeline is **validated end-to-end** on the development machine.

### Auto-selection logic

```
python sentinel.py --backend auto    # default
       │
get_backend_with_fallback()
       │
┌──────┴──────┐
│             │
QNN available? CPU only
│             │
QNNBackend  CPUBackend
│             │
Hexagon NPU  Local CPU
```

---

## 🏗️ Architecture

See [docs/architecture.md](docs/architecture.md) for the full pipeline.

```
Screen / Event
    │
    ▼
Change Detector ────────► SKIP (no change)
    │
    ▼
Event Policy (L0 / L1 / L2)
    │
    ├── L0 ──► Skip OCR
    ├── L1 ──► Fast OCR
    └── L2 ──► Precise ROI OCR
                │
                ▼
        Two-Stage ROI OCR ────► LRU Cache (content-hash)
                │
                ▼
        Entity Detection (PAN · Phone · Aadhaar · Financial · Confidential)
                │
                ▼
        Behavior Tracker + Data Flow Graph
                │
                ▼
        Risk Engine + Session Risk
                │
                ▼
        Intent Classifier (BENIGN / CONFIDENTIAL_ACCESS / EXFILTRATION)
                │
                ▼
        DLP Policy Engine
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
  ALLOW       WARN        BLOCK
    │           │           │
    ▼           ▼           ▼
  Audit    User Confirm  Audit + Arduino
```

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

## 📚 Documentation

| File | Purpose |
|:---|:---|
| [docs/architecture.md](docs/architecture.md) | Full pipeline + design principles |
| [docs/benchmark.md](docs/benchmark.md) | Benchmark methodology + results |
| [docs/security.md](docs/security.md) | Threat model + security depth |
| [docs/use_cases.md](docs/use_cases.md) | Concrete enterprise scenarios |
| [docs/innovation.md](docs/innovation.md) | What is genuinely novel |
| [docs/snapdragon_validation.md](docs/snapdragon_validation.md) | Honest Snapdragon evidence |

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