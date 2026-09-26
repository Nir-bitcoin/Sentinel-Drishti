\# Sentinel Drishti — Security



\## 1. DLP Policy Rules



| Rule ID | Description | Severity | Default Action |

|---------|-------------|----------|----------------|

| PII\_001 | PAN, phone, Aadhaar, account numbers | HIGH | BLOCK\_AND\_ALERT |

| FIN\_001 | Salary, CTC, payroll, bonus | HIGH | BLOCK\_AND\_ALERT |

| CONF\_001 | Confidential / internal-only markings | MEDIUM | ALERT\_ONLY |



Rules live in `src/policy/dlp\_engine.py`.

Weights and thresholds live in `config/policy.yaml`.



\## 2. Evidence Chain



Every DLP decision produces a defensible, non-probabilistic evidence trail:

Matched Rules -> rule IDs that fired (PII\_001, FIN\_001, ...)

Behavior Verdict -> NORMAL / HIGH\_RISK / CRITICAL\_RISK

Destination -> LOCAL / PERSONAL\_EMAIL / EXTERNAL\_DEVICE / CLOUD\_STORAGE / MESSAGING

Risk Score -> 0-100 policy score (not a probability)

Evidence Level -> HIGH / MEDIUM / LOW

Policy Decision -> BLOCK\_AND\_ALERT / ALERT\_ONLY / ALLOW





We deliberately avoid presenting a "rule match 0.97" as model confidence.

The score is a \*\*Policy Risk Score\*\* derived from configured weights.



\## 3. Audit Chain



\- SHA-256 hash chain in `src/policy/audit\_chain.py`

\- Each entry stores:

&#x20; - `previous\_hash`

&#x20; - `current\_hash`

&#x20; - event payload (redacted)

&#x20; - timestamp

\- `verify\_chain()` recomputes and compares — detects tampering

\- \*\*Raw PII is never written to logs\*\*



Audit log entry shape:



```json

{

&#x20; "event": {

&#x20;   "severity": "HIGH",

&#x20;   "action": "BLOCK\_AND\_ALERT",

&#x20;   "matches": \["PII\_001", "FIN\_001"],

&#x20;   "risk\_score": 100,

&#x20;   "content\_hash": "a1b2c3d4e5f6...",

&#x20;   "content\_redacted": true

&#x20; },

&#x20; "previous\_hash": "...",

&#x20; "hash": "..."

}

```



\## 4. Tamper Detection



Demonstrated in `tests/test\_security\_deep.py::t\_audit\_tamper\_detected`:

Original chain -> VALID

Modify one event -> verify\_chain() returns False

Final chain -> INVALID



This is an automated test, not a claim.



\## 5. Fail-safe Behaviour



| Failure | Behaviour |

|---------|-----------|

| OCR fails | Decision still logged, safe fallback |

| QNN unavailable | CPU fallback (visible in diagnostic) |

| Arduino missing | Software alert only, audit recorded |

| Invalid image | Rejected safely, no crash |

| Malformed text | Regex does not match, ALLOW + log |



\## 6. Security Test Coverage



\- `tests/test\_pipeline.py` — 25 unit tests

\- `tests/test\_security\_deep.py` — 33 deep security tests

\- `tests/test\_e2e.py` — 4 end-to-end pipeline tests



Categories covered:



\- PII detection (PAN, phone, Aadhaar, financial)

\- Benign text (no false positives)

\- Empty / whitespace / unicode / very long input

\- Behavior sequences (USB, Gmail, cloud, work email)

\- Duplicate events, event ordering

\- Risk cap (0-100)

\- After-hours boost

\- DLP block / allow per destination

\- Intent classification (EXFILTRATION / BENIGN / UNVERIFIED)

\- Audit integrity + redaction + tamper detection

\- Cache correctness (put / get / clear / eviction)

\- Provider fallback



\## 7. Known Limitations (Honest)



\- Enforcement is \*\*simulated\*\* — no OS-level interception on this host

\- Audit chain is local-file based, not remote-attested

\- No physical Snapdragon hardware in this environment

\- No formal threat model against a root-level adversary

\- OCR confidence thresholds are empirically tuned, not calibrated

