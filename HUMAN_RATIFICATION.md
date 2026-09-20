# Human Ratification Instrument: BatteryML S3 Retro S2 (Run-003)

**Document Identifier:** `RATIFICATION-P10-AUDIT-BATTERYML-S3-RETRO-S2-RUN-003`  
**Date:** 2026-09-20  
**Authority:** Ivan Nestorov (Operator [L3])  
**ORCID:** `0009-0006-7940-9539`  
**Target Execution:** `run-003-evidence-bound-conformance`  
**Status:** **ISSUED / RATIFIED**  
**Gate Review Disposition:** **PASS WITH LIMITATIONS**  
**P10 Terminal Outcome:** **`NotVerified`**  
**Claim Scope:** `C_P10_RETRO` (Conjunctive Robustness Assertion)  
**Native S3 Target Adjudication:** **`MODEL_SPECIFIC` (Unchanged)**  

---

## 1. Ratification Declaration

I, Ivan Nestorov, acting as Operator [L3] and final ratifier, formally ratify `run-003-evidence-bound-conformance` as a retrospective P10 S2 conformance deployment.

1. **Terminal Outcome Acceptance:**
   I accept the terminal outcome **`NotVerified`** for the explicitly instantiated retrospective claim $C_{\text{P10\_RETRO}}$, evaluated under the frozen BatteryML S2 domain profile (`spec/profiles/P10-BatteryML-S2-Profile-v0.1.md` @ `dd88e62...`) and frozen adapter v0.3 (`e952f00...`).

2. **Claim Demarcation & Native S3 Invariance:**
   The evaluated claim $C_{\text{P10\_RETRO}}$ is an auditor-instantiated conjunctive claim over historical evidence. This adjudication does **not** replace, revise, or contradict the target study's native pre-registered adjudication category **`MODEL_SPECIFIC`**. The two adjudication engines answer distinct formally specified questions over the same historical data.

3. **Independent Empirical Corroboration:**
   Independent clean-room recomputation directly from the 264 raw prediction CSV tables corroborated 100% of the empirical values evaluated by the adapter, including Ridge positive material degradation in 55 of 64 protocol-disjoint splits ($85.94\% > 50.00\%$) and dummy benchmark separation across 191 of 192 comparisons ($99.48\% \ge 95.00\%$).

4. **Retrospective Scope & Epistemic Limitations:**
   This deployment is retrospective and non-confirmatory. It does not establish prospective falsifiability, absence of post-hoc claim selection, or a new finding in battery materials science. It demonstrates deterministic precedence traversal, live non-softening preemption, and cryptographic evidence binding under the P10 S2 framework.

5. **Formalization Boundary:**
   The frozen external adapter governs empirical evidence ingestion, metric calculation, and normalization into the 6-field `DecisionView`. The Lean-verified S2 core (`p10-core@fa7878a...`) formally verifies and governs only the deterministic precedence traversal and terminal adjudication of that normalized `DecisionView`.

---

## 2. Cryptographic Evidence Anchors

| Component | Identifier / Digest |
|---|---|
| **Frozen S2 Core Commit** | `fa7878a538f56ee9b3c8008ca71e93c04c69ecf4` (Tag: `v0.3.0-s2-freeze`) |
| **Frozen BatteryML Profile Commit** | `dd88e6222fc717b557b7b5c2ebf6b1d725b50891` (Tag: `batteryml-s2-profile-v0.1-retro-freeze`) |
| **Target Study Commit** | `4bdf33e27f3c8e1e22583ae41c13b096a81e5e38` (Tag: `v1.0.0`, Preregistration: `0958e89...`) |
| **Prediction Input Manifest Digest** | `57c55989de3545254d42b9fb801e3dd20155a78cfb1126266aa44f5a1ce298c8` |
| **Pre-Execution Freeze Commit** | `e952f0025b22a14ae9f7ff93d8c4202afbdbc3c0` |
| **Execution Record Commit** | `d49764a78465fe3db1e988622f676be8b693245f` |
| **Report v3 SHA-256** | `0e3edb7cd831b3ff2cedd58572d3100ad95ef4855bc734dd74f7b5d018cbf8e9` |
| **Decision Trace SHA-256** | `33975c3b5197d875d8f2f60d9e63b28a104c9dbcc92c370733130f9bc484fc93` |

---

## 3. Ratifier Execution

**Ratified by:** Ivan Nestorov  
**Role:** Research Lead & Final Operator [L3]  
**ORCID:** `0009-0006-7940-9539`  
**Timestamp:** 2026-09-20T17:45:00+02:00  
**Signature Status:** **EXECUTED / RATIFIED**
