\# Sentinel Drishti — Architecture



\## Pipeline



Screen / Event -> Change Detector -> Event Policy (L0/L1/L2) -> OCR (two-stage ROI) -> OCR Cache -> Entity Detection -> Behavior Tracker -> Risk Scorer -> Intent Classifier -> DLP Policy Engine -> Audit Chain + Arduino Alert



\## Compute Levels



\- \*\*L0\*\* — no security event -> skip OCR

\- \*\*L1\*\* — suspicious event -> fast OCR

\- \*\*L2\*\* — critical event -> ROI precise OCR



\## Backends



\- `CPUBackend` — development / fallback (EasyOCR)

\- `QNNBackend` — Snapdragon HTP target (requires hardware)

