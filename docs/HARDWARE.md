Hardware Validation Status
==========================

Current Environment
-------------------

Development done on a standard Windows laptop (no Snapdragon NPU).

What This Means
---------------

    Component                        Status
    -------------------------------  ---------------------------------
    OCR (Tesseract)                  Real
    Entity detection (regex)         Real
    Behavior tracking                Real
    Risk scoring                     Real
    DLP enforcement logic            Real
    Audit logging                    Real
    Qualcomm AI Hub profiling        Real (4 jobs completed)
    NPU inference timing (demo)      SIMULATED (benchmark-based)


Quantization Results (Real Hardware)
------------------------------------

Four jobs completed on actual Snapdragon X Elite CRD via Qualcomm AI Hub.

FLOAT16
    Min Inference:   1.0 ms
    Peak Memory:     0.6 MB
    Compute Unit:    NPU (Hexagon HTP)
    Job ID:          j5qllld4p

INT8
    Min Inference:   0.687 ms
    Peak Memory:     14.4 MB
    Compute Unit:    NPU (Hexagon HTP)
    Job ID:          jgnz1zdkg

Speedup
    INT8 is 1.46x faster than FLOAT16 on the same Snapdragon X Elite NPU.

Job Links
    FLOAT16 Profile:  https://workbench.aihub.qualcomm.com/jobs/j5qllld4p/
    INT8 Quantize:    https://workbench.aihub.qualcomm.com/jobs/jp8eje3zp/
    INT8 Compile:     https://workbench.aihub.qualcomm.com/jobs/jp1nonk8g/
    INT8 Profile:     https://workbench.aihub.qualcomm.com/jobs/jgnz1zdkg/


Backend Architecture
--------------------

The pipeline uses an abstract backend so the same code runs on both:

    InferenceBackend
     |-- CPUBackend          <- runs on any laptop
     |-- SnapdragonBackend   <- target for Snapdragon X Elite NPU


How to Test on Snapdragon Hardware (Future)
-------------------------------------------

When a Snapdragon X Elite device is available:

1. Install qai_appbuilder and Qualcomm AI Hub SDK
2. Set env var: SNAPDRAGON_REAL=1
3. Run: python run_demo.py


Honest Position
---------------

The pipeline logic is production-ready. INT8 and FLOAT16 quantization 
were validated on real Snapdragon X Elite hardware via Qualcomm AI Hub. 
On-device demo timing uses benchmark values until hardware is available.