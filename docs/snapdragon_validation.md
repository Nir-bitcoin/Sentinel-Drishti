\# Snapdragon Validation — Sentinel Drishti



\## Purpose



This document provides honest, verifiable evidence of the Snapdragon-side

execution path for Sentinel Drishti. It separates:



1\. Local development (CPU) — measured

2\. Snapdragon target (QNN/HTP) — architecture ready

3\. Qualcomm AI Hub component benchmarks — hosted reference



\*\*No fabricated on-device numbers.\*\*



\## 1. Local Development Backend



| Property | Value |

|----------|-------|

| Runtime | Windows AMD64 |

| Provider | `CPUBackend` |

| OCR engine | EasyOCR (CPU) |

| Purpose | functional correctness + real benchmarks |



Measured on this host:



\- L0 control plane: \~0.36 ms P50

\- Cache hit path: \~3-4 ms P50

\- Cold OCR (new screen): \~8-9 s P50

\- Final OCR confidence: \~0.968



Reproducible via:



```powershell

python scripts/benchmark\_continuous.py --cache

python scripts/benchmark\_continuous.py --mixed

python scripts/benchmark\_continuous.py --cold

```



\## 2. Snapdragon Target Backend (QNN/HTP)



| Property | Value |

|----------|-------|

| Provider | `QNNBackend` |

| Runtime | ONNX Runtime + QNN Execution Provider |

| Target | Hexagon Tensor Processor (HTP) |

| Hardware | Snapdragon X Elite (HP PC class) |

| Status | NOT hardware-validated in this environment |



Fallback architecture:

&#x20;    Sentinel Runtime

&#x20;           |

&#x20;   +-------+-------+

&#x20;   |               |

&#x20;QNN/HTP          CPU

&#x20;   |               |

Snapdragon target dev host





`get\_backend\_with\_fallback()` selects QNN when available, otherwise CPU.

The CPU path is what runs end-to-end in this submission.



\## 3. Qualcomm AI Hub Component Benchmarks (Hosted)



These are component-level benchmarks run on Qualcomm-hosted Snapdragon X Elite

devices via AI Hub. They are NOT end-to-end Sentinel timings and must not be

presented as such.



| Component | Job ID | Precision | Latency |

|-----------|--------|-----------|---------|

| EasyOCR text detector | `jgk4j29wp` | uint8 | \~13.5 ms |

| EasyOCR text recognizer | `jprl9wnvp` | uint8 | \~10.5 ms |



Verify:

\- https://aihub.qualcomm.com/jobs/jgk4j29wp

\- https://aihub.qualcomm.com/jobs/jprl9wnvp



\## 4. What Is Honestly NOT Claimed



\- On-device NPU execution of the full Sentinel pipeline

\- "22 s CPU -> 10 ms NPU" style speedup claims

\- 8.8x speedup numbers

\- Full end-to-end latency on Snapdragon hardware



\## 5. What IS Claimed



\- Backend abstraction supports QNN/HTP selection

\- Automatic fallback to CPU when QNN unavailable

\- CPU path validated end-to-end with real OCR + real DLP decisions

\- Component-level Snapdragon NPU benchmarks referenced from AI Hub

\- Runtime diagnostic visibly reports provider + fallback reason



\## 6. Runtime Diagnostic



```powershell

python scripts/check\_provider.py

```



Output shows:



\- Selected provider

\- QNN availability

\- Fallback reason

\- Snapdragon reference numbers (clearly labelled as hosted)



\## 7. Architecture Readiness for Snapdragon



When deployed on Snapdragon hardware with QNN EP available:

&#x20;             Sentinel Runtime

&#x20;                    |

&#x20;         get\_backend\_with\_fallback()

&#x20;                    |

&#x20;             QNN EP available?

&#x20;             +------+------+

&#x20;             |             |

&#x20;            Yes            No

&#x20;             |             |

&#x20;       QNNBackend      CPUBackend

&#x20;             |             |

&#x20;     +-------+-------+     |

&#x20;     |               |     |

&#x20; detect()        recognize()

&#x20; (QNN/HTP)        (QNN/HTP)

&#x20;     |               |

&#x20;     +-------+-------+

&#x20;             |

&#x20;    Same Entity Detection

&#x20;             |

&#x20;      Same Risk Engine

&#x20;             |

&#x20;      Same DLP Engine

&#x20;             |

&#x20;      Same Audit Chain





Only the perception layer swaps. Everything downstream is unchanged.



\## 8. Honest Statement



Full physical Snapdragon execution has not been measured.

The above are hosted component benchmarks from Qualcomm AI Hub.

The runtime architecture supports QNN fallback to CPU, which is what

this submission demonstrates end-to-end.

