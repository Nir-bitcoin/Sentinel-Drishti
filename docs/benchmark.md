\# Sentinel Drishti — Benchmarks



\## Modes

\- `--cache` — all OCR from LRU cache

\- `--mixed` — realistic (70% skip, 30% events)

\- `--cold` — cache cleared per OCR call



\## Measured

| Metric | Result |

|---|---|

| L0 control P50 | \~0.36 ms |

| Cache hit P50 | \~3-4 ms |

| Cold OCR P50 | \~9 s (CPU) |

| OCR final confidence | \~0.968 |

| Snapdragon AI Hub (component) | 13.5 ms detector + 10.5 ms recognizer |

