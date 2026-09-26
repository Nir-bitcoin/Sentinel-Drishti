\# Sentinel Drishti — Architecture



\## Overview



Sentinel Drishti is an on-device AI compliance and Data Loss Prevention (DLP)

agent for Snapdragon-powered HP PCs. It monitors screen content and user

behavior, runs OCR only when security context justifies the compute, and

produces tamper-evident audit decisions with physical alerting.



\## Full Pipeline

&#x20;               SENTINEL DRISHTI

&#x20;                      |

&#x20;               Screen / Event

&#x20;                      |

&#x20;               Change Detector

&#x20;                +-----+-----+

&#x20;                |           |

&#x20;              Same       Changed

&#x20;                |           |

&#x20;              SKIP      Event Policy

&#x20;                           |

&#x20;               +-----------+-----------+

&#x20;               |           |           |

&#x20;              L0          L1          L2

&#x20;             Skip      Fast OCR    Precise OCR

&#x20;                           |           |

&#x20;                           +-----+-----+

&#x20;                                 |

&#x20;                           ROI Refinement

&#x20;                                 |

&#x20;                             OCR Cache (LRU)

&#x20;                                 |

&#x20;                          Entity Detector

&#x20;                                 |

&#x20;                         Behavior + Context

&#x20;                                 |

&#x20;                           Intent Engine

&#x20;                                 |

&#x20;                            Risk Engine

&#x20;                                 |

&#x20;                          DLP Policy Engine

&#x20;                           +-----+-----+

&#x20;                         ALLOW       BLOCK

&#x20;                           |            |

&#x20;                         Audit      Alert / Arduino



\## Compute Levels (Event Policy)



| Level | Trigger | Action |

|-------|---------|--------|

| \*\*L0\*\* | No security-relevant event | Skip OCR |

| \*\*L1\*\* | Suspicious event (COPY, PASTE, SAVE\_AS) | Fast OCR |

| \*\*L2\*\* | Critical event (USB\_INSERT, UPLOAD, EMAIL\_OPEN) | Precise ROI OCR |



Central engineering principle:



> \*\*Spend AI compute only when security context justifies it.\*\*



\## OCR Pipeline (Two-Stage ROI)



1\. \*\*Fast pass\*\* — downscale to 800px, detect + recognize all text regions

2\. \*\*Confidence split\*\* — boxes >= 0.85 kept as-is; boxes < 0.85 marked low-confidence

3\. \*\*ROI refinement\*\* — low-confidence boxes are cropped (30px padding), upscaled 2x, and re-recognized

4\. \*\*Hybrid fallback\*\* — if ROI confidence is still below threshold, a full-image high-res pass runs

5\. \*\*Cache\*\* — content-hash LRU (max 100 entries) serves repeated screens in \~3 ms



\## Backends



| Backend | Purpose | Status |

|---------|---------|--------|

| `CPUBackend` | Development / fallback | Active, measured |

| `QNNBackend` | Snapdragon HTP target | Architecture ready, no hardware |

| `SnapdragonBackend` | Reference only | Diagnostic |



Selection logic (`get\_backend\_with\_fallback()`):

if QNN EP available:

return QNNBackend()

else:

return CPUBackend() # with visible fallback reason



\## Audit Chain



\- SHA-256 hash chain in `src/policy/audit\_chain.py`

\- Each entry stores `previous\_hash` + `current\_hash`

\- `verify\_chain()` detects tampering

\- Raw PII is \*\*never\*\* stored — only content hash + redaction flag



\## Physical Alerting



\- Arduino UNO Q simulation: LED (GREEN / RED) + buzzer

\- GREEN + OFF -> ALLOW

\- RED + ON -> BLOCK\_AND\_ALERT

\- Failure-safe: if Arduino unavailable, software alert still fires and audit is recorded



\## Module Layout

src/

backend/ CPUBackend, QNNBackend, fallback selector

vision/ EasyOCR two-stage ROI, change detector, cache

policy/ DLP engine, event policy, audit chain, policy loader

reasoning/ Intent classifier

policy/ Behavior tracker, risk scorer

action/ Arduino simulation



config/

policy.yaml Risk weights, thresholds, destinations



tests/

test\_pipeline.py 25 unit tests

test\_security\_deep.py 33 deep security tests

test\_e2e.py 4 end-to-end tests



scripts/

benchmark\_continuous.py 3-mode benchmark (cache/mixed/cold)

benchmark\_ocr.py 10-run OCR P50/P95

memory\_profile.py RAM profiling

check\_provider.py Backend diagnostic

healthcheck.py 7-component health check



evaluation/

ground\_truth.csv Labelled samples

run\_evaluation.py Precision / Recall / F1



docs/

architecture.md (this file)

benchmark.md Benchmark methodology + results

security.md Threat model + security depth

snapdragon\_validation.md Snapdragon evidence



sentinel.py Unified launcher

run\_demo.py Terminal demo

app.py Streamlit dashboard





\## Data Flow Example: PII -> Gmail Exfiltration

\## Data Flow Example: PII -> Gmail Exfiltration



```

1\. User opens Excel (HR\_salaries.xlsx)

2\. Screen shows "Employee salary record: PAN ABCDE1234F"

3\. Change detector: screen changed -> proceed

4\. Event policy: no trigger yet -> L0 (skip OCR)

5\. User presses Ctrl+C in Excel

&#x20;  -> event policy: COPY -> L1

&#x20;  -> fast OCR runs -> PII detected

6\. User opens Gmail

&#x20;  -> event policy: EMAIL\_OPEN -> L2

&#x20;  -> ROI OCR -> high-confidence text with PAN

7\. Behavior tracker: COPY + EMAIL\_OPEN + PASTE -> CRITICAL\_RISK

8\. Risk scorer: 100/100 (capped from raw 120)

9\. Intent classifier: EXFILTRATION

10\. DLP engine: BLOCK\_AND\_ALERT

11\. Audit chain: hash-chained event with content\_hash

12\. Arduino: LED RED + buzzer ON





\## Design Principles



1\. Event-driven, not frame-driven\*\* — OCR cost is bounded by user actions

2\. Cache-first — repeated screens cost \~3 ms, not seconds

3\. ROI-first — precise OCR only on uncertain regions

4\. Evidence, not confidence\*\* — matched rules + evidence level, not fabricated probabilities

5\. Fail-safe — every external component (QNN, Arduino, OCR) has a safe fallback

6\. Tamper-evident — every decision enters a SHA-256 chain

7\. Honest about hardware\*\* — no fake NPU numbers

