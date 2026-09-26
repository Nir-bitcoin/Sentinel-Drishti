\# Sentinel Drishti — Security



\## DLP Rules

\- PII (PAN, phone, Aadhaar, account numbers)

\- Financial data (salary, CTC, payroll)

\- Confidential markings



\## Evidence Chain

\- Matched rules (IDs)

\- Evidence Level (HIGH / MEDIUM / LOW)

\- Policy Decision (BLOCK / WARN / ALLOW)



\## Audit Chain

\- SHA-256 hash chain

\- `verify\_chain()` detects tampering

\- Raw PII NOT stored — only content hash + redaction flag

