\# Hardware Validation Status



\## Current Environment



Development done on a standard Windows laptop (no Snapdragon NPU).



\## What This Means



| Component | Status |

|---|---|

| OCR (Tesseract) | Real |

| Entity detection (regex) | Real |

| Behavior tracking | Real |

| Risk scoring | Real |

| DLP enforcement logic | Real |

| Audit logging | Real |

| Qualcomm AI Hub profile | Real (job j5qllld4p on real Snapdragon X Elite CRD) |

| NPU inference timing | \*\*SIMULATED\*\* (benchmark-based) |



\## Backend Architecture



The pipeline uses an abstract backend so the same code runs on both:



```text

InferenceBackend

&#x20;├── CPUBackend          ← runs on any laptop, real CPU execution

&#x20;└── SnapdragonBackend   ← target for Snapdragon X Elite NPU

&#x20;                         (currently stub, falls back to benchmark timing)

