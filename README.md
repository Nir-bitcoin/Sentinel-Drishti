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

1. Processes input (image / direct text)
2. Detects sensitive entities (PII, financial data, confidential markings)
3. Tracks user behavior across applications
4. Scores risk using content + behavior + destination + time
5. Decides via a deterministic DLP policy engine
6. Triggers physical alerts (Arduino buzzer + LED)
7. Logs every event with a local audit trail

The backend abstraction separates the local CPU implementation from the 
Snapdragon-target implementation path. Snapdragon execution is pending 
physical target validation.


Architecture
------------

Layer 1: INPUT
    Image (EasyOCR) / direct text

Layer 2: PERCEPTION
    EasyOCR detector + recognizer — text extraction
    Regex — entity detection (PII, financial, confidential)

Layer 3: BEHAVIOR TRACKING
    Destination awareness + time + action sequences

Layer 4: REASONING
    Rule engine — intent classification

Layer 5: DLP DECISION
    Policy engine + enforcement logic

Layer 6: ACTION
    Arduino UNO Q — buzzer + LED alert


Backend Abstraction
-------------------

The pipeline uses an abstract inference backend, allowing the same 
architecture to support CPU execution locally and Snapdragon-targeted 
inference when target hardware is available:

    Backend              Host                  Timing Source            Status
    -------------------  --------------------  -----------------------  ---------
    CPUBackend           Local development PC  Measured                 Working
    SnapdragonBackend    Snapdragon X Elite    Qualcomm AI Hub ref      Pending


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

    Component                  Local CPU            Snapdragon reference
    -------------------------  -------------------  ---------------------
    EasyOCR end-to-end         ~7.1-7.4 s           Not end-to-end
    EasyOCR detector           —                    ~39.5 ms [AI Hub]
    EasyOCR recognizer         —                    ~19.3 ms [AI Hub]
    PII regex                  ~0.1 ms              Local rule execution
    Risk / policy engine       ~0.1 ms              Local rule execution

Adaptive OCR behavior:
    Fast pass (800px)  -> confidence ~0.69
    Retry  (1000px)    -> confidence ~0.95
    If confidence < 0.85, system retries at 1000px.

No side-by-side speedup comparison between CPU end-to-end and NPU 
component references is claimed, because they measure different scopes.


Technical Implementation
------------------------

Test Coverage: 13/13 unit tests passing
    PII detection:         4 tests
    Behavior tracking:     3 tests
    Risk scoring:          1 test
    DLP policy:            2 tests
    Intent classification: 3 tests

Architecture: Modular design with separate layers
    Backend abstraction (CPU/Snapdragon)
    Vision (EasyOCR + regex)
    Behavior tracking
    Risk scoring
    DLP policy engine
    Multi-language alerts
    Audit logging

Run tests:
    python tests/test_pipeline.py


Qualcomm AI Hub Hosted-Device References
----------------------------------------

EasyOCR component jobs on hosted Snapdragon X Elite CRD (NPU):

    Job ID              Component        Compute      Reference
    ------------------  ---------------  -----------  -----------
    jpxlmx3jp           Detector         NPU (HTP)    ~39.5 ms
    jprl9wnvp           Recognizer       NPU (HTP)    ~19.3 ms

Verify online:
    https://aihub.qualcomm.com/jobs/jpxlmx3jp
    https://aihub.qualcomm.com/jobs/jprl9wnvp

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
    - Uploading an image
    - OCR extraction
    - PII detection
    - Behavior selection
    - Risk scoring
    - DLP decision
    - Audit result

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
    Audit logging                    Real event logging
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
    |   |-- vision/          Input + EasyOCR + perception
    |   |-- reasoning/       Intent classification + translator
    |   |-- policy/          DLP engine + behavior + risk
    |   +-- api/             FastAPI backend
    |-- simulation/          Arduino simulation
    |-- scripts/             Benchmark
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