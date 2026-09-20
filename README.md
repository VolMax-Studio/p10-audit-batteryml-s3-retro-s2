# p10-audit-batteryml-s3-retro-s2

**Retrospective P10 S2 Conformance Deployment (Qualification Artifact)**

$$\boxed{\textbf{Status: ISSUED / RATIFIED} \quad|\quad \textbf{Gate: PASS WITH LIMITATIONS} \quad|\quad \textbf{Verdict: NotVerified}}$$

---

## Overview

This repository contains the authoritative record of the first real-world domain qualification deployment of **P10-Core v0.3 (S2 Semantic Core)** over historical machine learning telemetry from [`batteryml-protocol-robustness-s3`](https://github.com/VolMax-Studio/batteryml-protocol-robustness-s3) (v1.0.0).

This deployment serves strictly as an **engineering qualification artifact**, demonstrating the behavior of the P10 S2 adjudication engine under real-world evidence constraints. It carries **no new prospective scientific or battery materials claim**.

---

## Core Findings & Epistemic Boundaries

1. **Evaluated Claim Demarcation (`C_P10_RETRO` vs Native S3):**
   - **Auditor-Instantiated Claim (`C_P10_RETRO`):** A conjunctive robustness claim asserting that all three candidate architectures (`xgb`, `variance`, `ridge`) simultaneously maintain positive degradation $D \ge 0.10$ with prevalence $\le 50\%$.
   - **Native S3 Cascade:** The target study evaluated a 4-category priority cascade under two-sided shift $|D| \ge 0.10$, yielding **`MODEL_SPECIFIC`** (since only Ridge breached prevalence).
   - **Outcome:** Ridge's failure ($55/64 = 85.94\% > 50\%$) refutes the conjunctive claim `C_P10_RETRO` $\to$ **`NotVerified`**. S3's native `MODEL_SPECIFIC` category remains intact. The two engines evaluate different formal questions over the identical evidence base.

2. **Strict Non-Softening Enforcement:**
   The formal Lean 4 kernel (`p10-core@fa7878a...`) enforced that a `DecisionView` containing a violated obligation (`O_STATISTICAL_PREVALENCE`) terminated at Step 2 with `NotVerified`, strictly preempting Step 6 and preventing non-blocking limitation `L_CHEMISTRY_LFP` from softening the outcome to `VerifiedWithLimitations`.

3. **Cryptographic Evidence Binding:**
   All 264 raw prediction CSV tables are cataloged and bound via `PREDICTION_INPUT_MANIFEST.json` (Digest: `57c55989...`). Recomputation was independently corroborated against target study source data down to the exact split counts.

4. **Trust Boundary Disclosure:**
   Empirical evidence ingestion, table parsing, and metric derivation are performed by the external domain adapter (`adapter/batteryml_s2_adapter.py` v0.3). The Lean 4 formalization verifies only the deterministic precedence traversal and terminal outcome of the normalized `DecisionView`.

---

## Primary Governance Artifacts

- **Final Audit Report:** [`RETROSPECTIVE_REPLAY_REPORT_v3.md`](RETROSPECTIVE_REPLAY_REPORT_v3.md)
- **Human Ratification Instrument:** [`HUMAN_RATIFICATION.md`](HUMAN_RATIFICATION.md) — Ratified by Ivan Nestorov [L3]
- **Prediction Manifest:** [`PREDICTION_INPUT_MANIFEST.json`](PREDICTION_INPUT_MANIFEST.json) / [`.sha256`](PREDICTION_INPUT_MANIFEST.sha256)
- **Execution Traces:** [`run-003-evidence-bound-conformance/`](run-003-evidence-bound-conformance/)
- **Protocol Failures & Lineage:** [`FAILURES.md`](FAILURES.md) (Records runs 001, 002, and 003 gate review closure)
- **Canonical Release Tag:** `v1.0.0-run003-ratified`
