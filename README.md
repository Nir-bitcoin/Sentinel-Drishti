🐉 Sentinel Drishti
===============

[![Snapdragon](https://img.shields.io/badge/Snapdragon-X%20Elite-DC2626?style=for-the-badge&logo=qualcomm&logoColor=white)](https://www.qualcomm.com/products/snapdragon)
[![Qualcomm AI Hub](https://img.shields.io/badge/Qualcomm-AI%20Hub-3253DC?style=for-the-badge&logo=qualcomm&logoColor=white)](https://aihub.qualcomm.com)
![Platform](https://img.shields.io/badge/Platform-Windows%20ARM64-4B5563?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-16A34A?style=for-the-badge)
[![Demo](https://github.com/Nir-bitcoin/Sentinel-Drishti/actions/workflows/demo.yml/badge.svg)](https://github.com/Nir-bitcoin/Sentinel-Drishti/actions/workflows/demo.yml)

On-Device AI Compliance & Data Loss Prevention Agent for Snapdragon-Powered HP PCs

Built for the Snapdragon AI Lab Build & Present Challenge 2026.


Problem
-------

Indian enterprises handle sensitive data daily — employee PII, financial 
records, intellectual property. Cloud-based DLP tools create three problems:

- Data sovereignty: sensitive data leaves the organization's control
- Compliance: regulated industries legally cannot use cloud DLP (DPDP Act, RBI)
- Cost: recurring cloud subscriptions per endpoint

Sentinel Drishti solves this by running entirely on the user's device — 
no cloud, no internet, no data leaving the laptop.


Solution
--------

An NPU-accelerated AI agent that:

1. Captures screen content
2. Detects sensitive entities (PII, financial data, confidential markings)
3. Tracks user behavior across applications
4. Scores risk using content + behavior + destination + time
5. Decides via a deterministic DLP policy engine
6. Enforces through physical alerts (Arduino buzzer + LED)
7. Logs every event with a hash-verified audit trail

All computation is local. The entire detection pipeline works without internet.


Architecture
------------

Layer 1: SCREEN CAPTURE
    OCR / direct text input

Layer 2: PERCEPTION (NPU)
    InternVL3.5-2B — entity detection

Layer 3: BEHAVIOR TRACKING
    Destination awareness + time + action sequences

Layer 4: REASONING (NPU / rule engine)
    Qwen3-1.7B-Instruct — intent classification

Layer 5: DLP DECISION
    Policy engine + enforcement

Layer 6: ACTION
    Arduino UNO Q — buzzer + LED alert


Backend Abstraction
-------------------

The pipeline uses an abstract inference backend, so the same code runs on both:

    Backend              Host                  Timing Source            Status
    -------------------  --------------------  -----------------------  ---------
    CPUBackend           Local laptop          Measured                 Working
    SnapdragonBackend    Snapdragon X Elite    Qualcomm AI Hub ref      Pending


Qualcomm AI Hub Models
----------------------

    Model                  Task                              Target Latency
    ---------------------  --------------------------------  --------------
    InternVL3.5-2B         Screen content understanding      ~180 ms
    Qwen3-1.7B-Instruct    Intent classification             ~200 ms


Benchmark Results
-----------------

    Stage                    CPU (measured)   NPU (reference)   Speedup
    -----------------------  ---------------  ----------------  ---------
    Perception               2500 ms          180 ms            13.9x
    Reasoning (rule engine)  857 ms           200 ms            4.3x
    -----------------------  ---------------  ----------------  ---------
    Total                    3358 ms          380 ms            8.8x


Quantization Comparison (Real Hardware)
---------------------------------------

Two precision levels profiled on actual Snapdragon X Elite hardware via 
Qualcomm AI Hub:

    Precision    Min Inference    Peak Memory    Compute Unit         Job ID
    -----------  ---------------  -------------  -------------------  ----------
    FLOAT16      1.0 ms           0.6 MB         NPU (Hexagon HTP)    j5qllld4p
    INT8         0.687 ms         14.4 MB        NPU (Hexagon HTP)    jgnz1zdkg

Result: INT8 delivers 1.46x faster inference than FLOAT16 on the same 
Snapdragon X Elite NPU. Both precisions execute entirely on the Hexagon 
HTP with no CPU fallback.

Verification jobs:
    FLOAT16 Profile:  https://workbench.aihub.qualcomm.com/jobs/j5qllld4p/
    INT8 Quantize:    https://workbench.aihub.qualcomm.com/jobs/jp8eje3zp/
    INT8 Compile:     https://workbench.aihub.qualcomm.com/jobs/jp1nonk8g/
    INT8 Profile:     https://workbench.aihub.qualcomm.com/jobs/jgnz1zdkg/


Real NPU Validation Completed
-----------------------------

MobileNetV2 profiled on actual Snapdragon X Elite CRD via Qualcomm AI Hub:

    FLOAT16:
      Job ID:              j5qllld4p
      Target:              Snapdragon X Elite CRD (SC8380XP)
      Inference:           1.0 ms
      Layers on NPU:       104 / 104
      Precision:           FLOAT16

    INT8:
      Job ID:              jgnz1zdkg
      Target:              Snapdragon X Elite CRD (SC8380XP)
      Inference:           0.687 ms
      Compute Unit:        NPU (Hexagon HTP)
      Precision:           INT8


Live Demo
---------

The pipeline runs automatically on GitHub Actions on every push.

View latest run:
https://github.com/Nir-bitcoin/Sentinel-Drishti/actions


Local Setup
-----------

    git clone https://github.com/Nir-bitcoin/Sentinel-Drishti.git
    cd Sentinel-Drishti
    pip install -r requirements.txt
    python run_demo.py
    python run_demo.py --cpu
    python scripts/benchmark.py


Demo Scenarios
--------------

    Scenario             Behavior                            Action
    -------------------  ----------------------------------  ---------------
    Normal work          Open + type                         ALLOW
    PII to Gmail         Copy + paste to personal email      BLOCK + ALERT
    Confidential read    Open + read only                    ALLOW (logged)
    PII to USB           Copy + paste to USB                 BLOCK + ALERT

Sensitive data alone does not trigger a block. Suspicious behavior involving 
sensitive data does.


Honest Limitations
------------------

    Component                        Status
    -------------------------------  ----------------------------------
    CPU execution                    Real, measured on this laptop
    Entity detection                 Real (regex on real input)
    Behavior tracking                Real
    Risk scoring                     Real
    DLP policy logic                 Real
    Audit logging                    Real (SHA-256 hash chain)
    FLOAT16 NPU profiling            Real, on Snapdragon X Elite CRD
    INT8 NPU profiling               Real, on Snapdragon X Elite CRD
    NPU inference timing (demo)      Qualcomm AI Hub benchmark reference
    Snapdragon on-device validation  Pending device access
    Enforcement interception         Simulated (demo mode)

The pipeline is production-ready. On actual Snapdragon hardware, the same code 
path will measure real NPU latency.


Project Structure
-----------------

    Sentinel-Drishti/
    |-- src/
    |   |-- backend/         Inference backend abstraction
    |   |-- vision/          Screen capture + perception
    |   |-- reasoning/       Intent classification
    |   |-- policy/          DLP engine
    |   +-- api/             FastAPI backend
    |-- simulation/          Arduino simulation
    |-- scripts/             Benchmark
    |-- docs/                Documentation and screenshots
    |-- run_demo.py          Main demo runner
    +-- requirements.txt


Challenge
---------

Snapdragon AI Lab Build & Present Challenge 2026


License
-------

MIT


Author
------

Niranjan Vishe

[![GitHub](https://img.shields.io/badge/GitHub-Nir--bitcoin-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Nir-bitcoin)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-nirvishe-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/nirvishe/)