\# Sentinel Drishti — Benchmarks



\## Purpose



This document defines the benchmark methodology and reports measured results.

All numbers are from real runs on the development host (Windows AMD64, CPU).

Snapdragon NPU numbers are clearly labelled as AI Hub hosted component

benchmarks, not end-to-end Sentinel timings.



\## Three Benchmark Modes



| Mode | Flag | What It Measures |

|------|------|------------------|

| \*\*CACHE\*\* | `--cache` | Hot-path: all OCR served from LRU cache |

| \*\*MIXED\*\* | `--mixed` | Realistic: 70% frames skipped, 30% events |

| \*\*COLD\*\* | `--cold` | Worst case: cache cleared before every OCR call |



Run them:



```powershell

python scripts/benchmark\_continuous.py --cache

python scripts/benchmark\_continuous.py --mixed

python scripts/benchmark\_continuous.py --cold

```



Or all three at once:



```powershell

python scripts/benchmark\_all\_modes.py

```



\## Workload Mix (100 frames)



| Frames | Event | Expected Level |

|--------|-------|----------------|

| 1-70 | No security event | L0 (skip OCR) |

| 71-85 | COPY -> Gmail -> PASTE | L1 (fast OCR) |

| 86-100 | COPY -> USB\_INSERT | L2 (precise OCR) |



\## Metrics Reported



| Metric | Meaning |

|--------|---------|

| L0 control P50/P95 | Monitoring overhead per frame |

| L1 fast OCR P50/P95 | Perception cost on suspicious event |

| L2 precise OCR P50/P95 | Perception cost on critical event |

| Event -> DLP decision P50/P95 | Full security response |

| OCR skip % | Compute saved |

| Cache hit % | Repeated-screen efficiency |

| ROI recovery % | Low-confidence regions recovered |

| Final OCR confidence | Recognition quality |



\## Measured Results (Current)



\### Control Plane (L0)



| Metric | Value |

|--------|-------|

| P50 | \~0.36 ms |

| P95 | \~0.48 ms |



Monitoring overhead is effectively free — no OCR, only change detection

\+ event policy + cache lookup.



\### Cache Hit Path



| Metric | Value |

|--------|-------|

| P50 | \~3-4 ms |

| P95 | \~10 ms |



Serving a previously seen screen requires only a SHA-256 lookup.



\### Cold OCR Path (New Sensitive Screen)



| Metric | Before ROI | After ROI |

|--------|-----------|-----------|

| L1 P50 | \~12.94 s | \~8-9 s |

| L2 P50 | \~22.83 s | \~8-9 s |

| Final confidence | 0.95 | 0.968 |



The ROI optimization replaced full-image retry with cropped re-recognition

of low-confidence regions only.



\### ROI Recovery



On the HR screenshot fixture:



| Metric | Value |

|--------|-------|

| High-confidence boxes | 2 |

| Low-confidence boxes | 4 |

| ROI attempts | 4 |

| ROI recovered | 4 |

| Recovery rate | 100% |

| Final confidence | 0.968 |

| Fallback used | No |



\## Snapdragon AI Hub Reference (Hosted)



| Component | Job ID | Precision | Latency |

|-----------|--------|-----------|---------|

| EasyOCR detector | `jgk4j29wp` | uint8 | \~13.5 ms |

| EasyOCR recognizer | `jprl9wnvp` | uint8 | \~10.5 ms |



\*\*These are component benchmarks, not end-to-end Sentinel latencies.\*\*

They must never be presented as a CPU -> NPU speedup for the whole pipeline.



\## Memory Profile



`scripts/memory\_profile.py` reports:



\- Startup RAM

\- RAM after OCR model load

\- Steady-state RAM

\- Peak RAM after repeated cache fills



Run:



```powershell

python scripts/memory\_profile.py

```



\## Reproducing the Results



```powershell

git clone https://github.com/Nir-bitcoin/Sentinel-Drishti

cd Sentinel-Drishti

pip install -r requirements.txt

pip install psutil pyyaml

python tests/test\_pipeline.py

python tests/test\_security\_deep.py

python tests/test\_e2e.py

python scripts/benchmark\_continuous.py --mixed

```



\## Honest Limitations



\- Cold OCR on CPU is \~8-9 s; target on NPU is \~20 ms per component, but

&#x20; full-pipeline NPU timing has not been measured on physical hardware.

\- CPU measurements include Python GIL effects and I/O.

\- P95 outliers exist (occasional \~700 ms) due to GC and disk I/O.

