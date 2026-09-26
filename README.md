🐉 Sentinel Drishti
===============

[![Snapdragon](https://img.shields.io/badge/Snapdragon-X%20Elite-DC2626?style=for-the-badge&logo=qualcomm&logoColor=white)](https://www.qualcomm.com/products/snapdragon)
[![Qualcomm AI Hub](https://img.shields.io/badge/Qualcomm-AI%20Hub-3253DC?style=for-the-badge&logo=qualcomm&logoColor=white)](https://aihub.qualcomm.com)
![Target](https://img.shields.io/badge/Target-Windows%20on%20Snapdragon-4B5563?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-16A34A?style=for-the-badge)
[![Demo](https://github.com/Nir-bitcoin/Sentinel-Drishti/actions/workflows/demo.yml/badge.svg)](https://github.com/Nir-bitcoin/Sentinel-Drishti/actions/workflows/demo.yml)

On-Device AI Compliance & Data Loss Prevention Agent designed for 
Snapdragon-Powered HP PCs.

Built for the Snapdragon AI Lab Build & Present Challenge 2026.


Problem
-------

Indian enterprises handle sensitive data daily — employee PII, financial 
records, intellectual property. Cloud-based DLP tools can create additional 
data-residency, privacy, outsourcing, and compliance requirements for 
regulated organizations.

Sentinel Drishti addresses this by keeping the detection pipeline on the 
endpoint — reducing cloud dependency and keeping sensitive content local 
to the device.

In local deployment, inference and policy processing run on the user's 
device without sending sensitive content to a cloud service. Internet 
access is only required for initial dependency/model setup and for viewing 
external Qualcomm AI Hub benchmark references.


Solution
--------

A Snapdragon-targeted, AI-assisted DLP agent that:

1. Processes input (image via EasyOCR / direct text)
2. Detects sensitive entities (PII, financial data, confidential markings)
3. Tracks user behavior across applications
4. Scores risk using content + behavior + destination + time
5. Decides via a deterministic DLP policy engine
6. Triggers physical alerts (Arduino buzzer + LED)
7. Logs every event with a tamper-evident audit hash chain

The backend abstraction separates the local CPU implementation from the 
Snapdragon-target implementation path. Snapdragon execution is pending 
physical target validation.


Architecture
------------

Layer 1: INPUT
    Image (EasyOCR) / direct text

Layer 2: PERCEPTION
    EasyOCR detector + recognizer — text extraction
    TextPerception — regex entity detection (PII, financial, confidential)

Layer 3: BEHAVIOR TRACKING
    Destination awareness + time + action sequences

Layer 4: REASONING
    RuleBasedIntentClassifier — rule-based intent classification

Layer 5: DLP DECISION
    Policy engine + enforcement logic

Layer 6: ACTION
    Arduino UNO Q — buzzer + LED alert


Provider Routing
----------------

The system detects available inference backends at runtime:

    Auto-detect
         |
    QNN EP available?
         |
      +--+--+
      |     |
     YES    NO
      |     |
   QNN/HTP  CPU
   (NPU)   fallback
      |     |
      +--+--+
         |
    Same DLP pipeline

Run diagnostic:
    python scripts/check_provider.py

On current development PC (no Snapdragon NPU):
    Selected provider: CPU
    Status:            FALLBACK

On Snapdragon X Elite (target):
    Selected provider: QNN / HTP
    Status:            NPU ACTIVE


Implementation Notes
--------------------

The pipeline is honest about what is real vs reference:

    Component              Status
    ---------------------  ------------------------------------
    EasyOCR (CPU)          Real, measured locally (~7.1-7.4 s)
    TextPerception         Real, regex-based
    BehaviorTracker        Real
    RiskScorer             Real
    DLPEngine              Real
    AuditChain (SHA-256)   Real, verifiable
    Snapdragon NPU         Reference only (AI Hub hosted jobs)

No time.sleep() simulation is used in the backend. Snapdragon reference
values come from Qualcomm AI Hub hosted-device jobs and are clearly
marked as reference, not measured.


Backend Abstraction
-------------------

    Backend              Host                  Timing Source            Status
    -------------------  --------------------  -----------------------  ---------
    CPUBackend           Local development PC  Measured                 Working
    SnapdragonBackend    Snapdragon X Elite    Qualcomm AI Hub ref      Pending

The Snapdragon backend is a target implementation path — it returns 
reference markers, not simulated values. When physical Snapdragon 
hardware is available, the same interface can be wired to QNN/HTP.


Qualcomm AI Hub References
--------------------------

Component jobs profiled on hosted Snapdragon X Elite CRD:

    Model/Component        Task                              Reference
    ---------------------  --------------------------------  --------------
    EasyOCR detector       Text region detection             ~39.5 ms NPU
    EasyOCR recognizer     Text recognition                  ~19.3 ms NPU

    Job IDs:  jpxlmx3jp (detector), jprl9wnvp (recognizer)

Note: These are separate component benchmarks, not an end-to-end 
pipeline measurement. The full OCR pipeline running on Snapdragon 
X Elite would require additional orchestration measurements.


Benchmark Results
-----------------

Pipeline-only benchmark (regex + rule engine + DLP, no OCR):

    Run 1..5: sub-millisecond per iteration

    Statistics:
      Min:     0.1 ms
      Median:  0.2 ms
      Max:     0.4 ms

EasyOCR end-to-end (local CPU):

    ~7.1-7.4 s  (5-run median, development laptop)

Snapdragon reference (component benchmarks, AI Hub hosted):

    EasyOCR detector    ~39.5 ms  [job jpxlmx3jp]
    EasyOCR recognizer  ~19.3 ms  [job jprl9wnvp]

Adaptive OCR behavior:
    Fast pass (800px)  -> confidence ~0.69
    Retry  (1000px)    -> confidence ~0.95
    If confidence < 0.85, system retries at 1000px.

No side-by-side speedup comparison between CPU end-to-end and NPU 
component references is claimed, because they measure different scopes.


Optimization: ROI Cache
-----------------------

Repeated OCR of unchanged screens is skipped via content-hash cache.
Same screen -> cached result. Different screen -> run OCR.

This models how a real endpoint agent would avoid redundant inference
during continuous monitoring.


Technical Implementation
------------------------

Test Coverage: 15/15 unit tests passing
    PII detection:          4 tests
    Behavior tracking:      3 tests
    Risk scoring:           1 test
    DLP policy:             2 tests
    Intent classification:  3 tests
    Audit hash chain:       1 test
    Provider diagnostic:    1 test

Architecture: Modular design with separate layers
    Backend abstraction (CPU/Snapdragon)
    Vision (EasyOCR + TextPerception)
    Behavior tracking
    Risk scoring
    DLP policy engine
    Multi-language alerts
    Tamper-evident audit chain (SHA-256)
    ROI cache for repeated screens

Run tests:
    python tests/test_pipeline.py


Security Features
-----------------

    Tamper-evident audit log (SHA-256 hash chain)
    Each event links to previous event's hash
    verify_chain() detects any modification
    Fail-safe: low OCR confidence + risky behavior -> WARN_AND_ALERT


Snapdragon Validation Evidence
------------------------------

    Component                 Snapdragon evidence            Status
    ------------------------  -----------------------------  ------
    EasyOCR detector          AI Hub X Elite NPU profile     OK
    EasyOCR recognizer        AI Hub X Elite NPU profile     OK
    Optimized INT8 model      AI Hub X Elite NPU profile     OK
    Full OCR pipeline         End-to-end X Elite measurement Pending
    DLP engine                Local CPU                      OK
    Arduino action            Local hardware / demo          OK
    Full app on HP Snapdragon Physical target validation     Pending

Details: docs/snapdragon_validation.md


Qualcomm AI Hub Hosted-Device References
----------------------------------------

EasyOCR component jobs on hosted Snapdragon X Elite CRD (NPU):

    Job ID              Component        Compute      Reference
    ------------------  ---------------  -----------  -----------
    jpxlmx3jp           Detector         NPU (HTP)    ~39.5 ms
    jprl9wnvp           Recognizer       NPU (HTP)    ~19.3 ms
    jgnz1zdkg           INT8 optimized   NPU (HTP)    0.7 ms

Verify online:
    https://aihub.qualcomm.com/jobs/jpxlmx3jp
    https://aihub.qualcomm.com/jobs/jprl9wnvp
    https://workbench.aihub.qualcomm.com/jobs/jgnz1zdkg/

These are hosted Qualcomm device results, not measurements on the 
developer's laptop. They are component references, not a validation 
of Sentinel Drishti itself on Snapdragon hardware.


Automated CI Demo
-----------------

The pipeline runs automatically on GitHub Actions on every push 
(reproducible test run, not a live cloud deployment).

View latest run:
https://github.com/Nir-bitcoin/Sentinel-Drishti/actions


Browser Demo
------------

A browser-based Streamlit interface is provided for demonstration.

Demo mode supports:
    - Image upload (EasyOCR on local deployments)
    - PII detection
    - Behavior selection
    - Risk scoring
    - DLP decision
    - Audit result
    - JSON audit download

Note: The browser demo does not access the user's local screen, 
clipboard, USB devices, or Snapdragon NPU.


Local Setup
-----------

    git clone https://github.com/Nir-bitcoin/Sentinel-Drishti.git
    cd Sentinel-Drishti
    pip install -r requirements.txt
    python run_demo.py
    python run_demo.py --cpu
    python scripts/benchmark.py
    python scripts/check_provider.py
    python tests/test_pipeline.py


Demo Scenarios
--------------

    Scenario             Behavior                            Action
    -------------------  ----------------------------------  ---------------
    Normal work          Open + type                         ALLOW
    Image OCR (EasyOCR)  Real image -> PII detect -> COPY    BLOCK + ALERT
    PII to Gmail         Copy + paste to personal email      BLOCK + ALERT
    Confidential read    Open + read only                    ALLOW (logged)
    PII to USB           Copy + paste to USB                 BLOCK + ALERT

Sensitive data alone does not trigger a block. Suspicious behavior 
involving sensitive data does.

When OCR confidence is low AND behavior is risky, the system triggers 
WARN_AND_ALERT (fail-safe) instead of silent ALLOW.


Honest Limitations
------------------

    Component                        Status
    -------------------------------  ----------------------------------
    CPU execution                    Real, measured on development PC
    EasyOCR integration              Real (CPU execution, adaptive)
    Entity detection                 Real (regex on real input)
    Behavior tracking                Real
    Risk scoring                     Real
    DLP policy logic                 Real
    Audit logging                    Real (SHA-256 hash chain)
    EasyOCR NPU profiling            Hosted Qualcomm X Elite CRD
    NPU inference timing (demo)      Qualcomm AI Hub benchmark reference
    Snapdragon on-device validation  Pending device access
    Enforcement interception         Simulated (demo mode)

The prototype is designed for deployment on Snapdragon-powered PCs. 
On physical Snapdragon hardware, the Snapdragon backend can be 
validated with real NPU inference measurements.


Project Structure
-----------------

    Sentinel-Drishti/
    |-- src/
    |   |-- backend/         Inference backend abstraction
    |   |-- vision/          EasyOCR + TextPerception + ROI cache
    |   |-- reasoning/       RuleBasedIntentClassifier + translator
    |   |-- policy/          DLP engine + behavior + risk + audit chain
    |   +-- api/             FastAPI backend
    |-- simulation/          Arduino simulation
    |-- scripts/             Benchmark + provider diagnostic
    |-- tests/               Unit tests
    |-- docs/                Documentation and screenshots
    |-- run_demo.py          Main demo runner
    |-- app.py               Streamlit browser demo
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