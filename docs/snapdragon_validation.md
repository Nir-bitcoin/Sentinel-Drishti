\# Snapdragon Validation Evidence



This document records the actual Qualcomm AI Hub hosted-device 

measurements tied to Sentinel Drishti's perception components.



\---



\## Target Device



\- \*\*Device\*\*: Snapdragon X Elite CRD

\- \*\*Platform\*\*: Windows 11

\- \*\*SOC\*\*: SC8380XP

\- \*\*Runtime\*\*: QNN / QAIRT



These jobs were executed on physical Qualcomm-hosted Snapdragon 

hardware (not simulated).



\---



\## EasyOCR Component Evidence



\### Optimized uint8 (Latest)



| Component | Job ID | Precision | Inference | Compute |

|---|---|---|---|---|

| Detector | jgk4j29wp | uint8 | \*\*13.5 ms\*\* | NPU |

| Recognizer | jp1n3jw7g | uint8 | \*\*10.5 ms\*\* | NPU |



These represent quantized uint8 optimization on Snapdragon X Elite.



\### Baseline FLOAT16 (Earlier)



| Component | Job ID | Precision | Inference | Compute |

|---|---|---|---|---|

| Detector | jpxlmx3jp | FLOAT16 | \~39.5 ms | NPU |

| Recognizer | jprl9wnvp | FLOAT16 | \~19.3 ms | NPU |



\### Optimization Summary



| Component | FLOAT16 | uint8 | Speedup |

|---|---|---|---|

| Detector | 39.5 ms | 13.5 ms | \*\*2.9×\*\* |

| Recognizer | 19.3 ms | 10.5 ms | \*\*1.8×\*\* |



\---



\## Optimized INT8 Model (NPU Capability Proof)



| Field | Value |

|---|---|

| Job ID | jgnz1zdkg |

| Compute Unit | NPU (Hexagon HTP) |

| Inference | 0.7 ms |

| Peak Memory | 0.6 MB |

| Precision | INT8 |

| Target | Snapdragon X Elite CRD |



This job demonstrates NPU INT8 quantization capability on Snapdragon 

X Elite.



\---



\## Evidence Matrix



| Component | Snapdragon Evidence | Status |

|---|---|---|

| EasyOCR detector (uint8) | AI Hub X Elite NPU | OK |

| EasyOCR recognizer (uint8) | AI Hub X Elite NPU | OK |

| EasyOCR detector (FLOAT16) | AI Hub X Elite NPU | OK |

| EasyOCR recognizer (FLOAT16) | AI Hub X Elite NPU | OK |

| Optimized INT8 model | AI Hub X Elite NPU | OK |

| Full OCR pipeline (end-to-end) | Pending | Pending |

| DLP engine | Local CPU | OK |

| Arduino action | Local | OK |

| Full app on HP Snapdragon | Physical validation | Pending |



\---



\## Scope Statement



These are \*\*Qualcomm AI Hub hosted-device component measurements\*\*. 

They are \*\*not\*\* presented as end-to-end Sentinel Drishti latency.



\- Component benchmarks: measured on real Snapdragon X Elite via AI Hub

\- Local pipeline: measured on development PC (CPU)

\- Physical HP Snapdragon validation: \*\*pending hardware access\*\*



\---



\## Latency Types



Qualcomm AI Hub distinguishes:



| Type | Meaning |

|---|---|

| First App Load | Cold startup (\~2.7 s) |

| Subsequent App Load | Warm load (\~1.1 s) |

| Inference | Steady-state per-call latency |



\---



\## What This Proves



1\. EasyOCR perception components are compatible with Snapdragon 

&#x20;  X Elite NPU execution (both FLOAT16 and uint8).

2\. uint8 quantization reduces NPU latency 1.8-2.9× vs FLOAT16.

3\. INT8 quantization workflow completed on real Snapdragon hardware.



\## What This Does NOT Prove



1\. Full Sentinel Drishti end-to-end on Snapdragon.

2\. OS-level enforcement on Snapdragon.

3\. Physical HP Snapdragon PC validation.

