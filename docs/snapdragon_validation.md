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

hardware (not simulated), as reported by Qualcomm AI Hub Workbench.



\---



\## Component Evidence



\### 1. EasyOCR Detector — Perception Component



| Field | Value |

|---|---|

| Job ID | jpxlmx3jp |

| Compute Unit | NPU (Hexagon HTP) |

| Inference | \~39.5 ms |

| Target | Snapdragon X Elite CRD |

| Verify | https://aihub.qualcomm.com/jobs/jpxlmx3jp |



This job validates that the EasyOCR detector stage of Sentinel 

Drishti's perception pipeline can execute on Snapdragon X Elite NPU.



\### 2. EasyOCR Recognizer — Perception Component



| Field | Value |

|---|---|

| Job ID | jprl9wnvp |

| Compute Unit | NPU (Hexagon HTP) |

| Inference | \~19.3 ms |

| Target | Snapdragon X Elite CRD |

| Verify | https://aihub.qualcomm.com/jobs/jprl9wnvp |



This job validates that the EasyOCR recognizer stage of Sentinel 

Drishti's perception pipeline can execute on Snapdragon X Elite NPU.



\### 3. Optimized INT8 Model — NPU Capability Proof



| Field | Value |

|---|---|

| Job ID | jgnz1zdkg |

| Compute Unit | NPU (Hexagon HTP) |

| Inference | 0.7 ms |

| Peak Memory | 0.6 MB |

| Precision | INT8 |

| Target | Snapdragon X Elite CRD |

| Verify | https://workbench.aihub.qualcomm.com/jobs/jgnz1zdkg/ |



This job demonstrates NPU INT8 quantization capability on Snapdragon 

X Elite. Not part of the Sentinel OCR pipeline.



\### Related Jobs



| Job ID | Purpose |

|---|---|

| jp1nonk8g | INT8 QNN compilation |

| jp8eje3zp | INT8 quantization |

| j5qllld4p | FLOAT16 baseline profile |



\---



\## Evidence Matrix



| Component | Snapdragon Evidence | Status |

|---|---|---|

| EasyOCR detector | AI Hub X Elite NPU profile | ✅ |

| EasyOCR recognizer | AI Hub X Elite NPU profile | ✅ |

| Optimized INT8 model | AI Hub X Elite NPU profile | ✅ |

| Full OCR pipeline (end-to-end) | End-to-end X Elite measurement | ⏳ Pending |

| DLP engine | Local CPU | ✅ |

| Arduino action | Local hardware / demo | ✅ |

| Full app on HP Snapdragon PC | Physical target validation | ⏳ Pending |



\---



\## Scope Statement



These are \*\*Qualcomm AI Hub hosted-device component measurements\*\*. 

They are \*\*not\*\* presented as end-to-end Sentinel Drishti application 

latency.



\- Component benchmarks: measured on real Snapdragon X Elite via AI Hub

\- Local pipeline: measured on development PC (CPU)

\- Physical Snapdragon-powered HP PC validation: \*\*pending hardware access\*\*



\---



\## Latency Types



Qualcomm AI Hub distinguishes between:



| Type | Meaning |

|---|---|

| First App Load | Cold startup cost (\~2.7 s) |

| Subsequent App Load | Warm load (\~1.1 s) |

| Inference | Steady-state per-call latency (0.7 ms for INT8 model) |



This distinction matters for realistic deployment planning.



\---



\## What This Proves



1\. The Sentinel perception components (EasyOCR detector + recognizer) 

&#x20;  are compatible with Snapdragon X Elite NPU execution.

2\. The INT8 quantization workflow was completed on real Snapdragon 

&#x20;  X Elite hardware.

3\. The AI Hub compilation/profiling pipeline was successfully 

&#x20;  integrated into the project.



\## What This Does NOT Prove



1\. That the full Sentinel Drishti application ran end-to-end on 

&#x20;  Snapdragon hardware.

2\. That OS-level enforcement interception ran on Snapdragon.

3\. Physical Snapdragon-powered HP PC validation.

