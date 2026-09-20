# Retrospective Execution Plan: BatteryML S3 under P10 S2 Adjudication

**Document Identifier:** `PLAN-P10-AUDIT-BATTERYML-S3-RETRO-S2`  
**Date:** 2026-09-20  
**Status:** **ACTIVE / FROZEN FOR REPLAY**  
**Epistemic Category:** Retrospective Conformance Deployment (Non-Confirmatory Field Demonstration)  
**Parent Framework:** P10-Core v0.3 — S2 Semantic Core  

---

## 1. Demarcation & Epistemic Boundary

$$\boxed{\textbf{RETROSPECTIVE CONFORMANCE DEPLOYMENT} \neq \textbf{NEW CONFIRMATORY BATTERY RESULT}}$$

This execution plan governs the retrospective derivation of a formal S2 terminal verdict from historical execution artifacts of `batteryml-protocol-robustness-s3`.

Because the empirical performance data (including Ridge model degradation across protocol splits and dummy baseline properties) were historically established prior to authoring the S2 profile and adapter:
1. **Zero Confirmatory Scientific Weight:** This run does **NOT** constitute a new confirmatory finding or prospective preregistered validation.
2. **Strict Protocol Conformance Demonstration:** The sole objective is to demonstrate that the P10 S2 pipeline (comprising the frozen S2 Lean core, the frozen BatteryML profile, and the executable adapter) deterministically translates raw ML telemetry into an authoritative terminal verdict without post-hoc discretion.
3. **No Retrospective Re-tuning:** The adapter rules, thresholds, and profile definitions are frozen prior to execution. Any outcome produced by the adjudication automaton (`Verified`, `VerifiedWithLimitations`, `NotVerified`, `NotDemonstrated`, `Deferred`, or `ProtocolError`) is accepted as final.

---

## 2. Frozen Cryptographic Anchors

| Component | Repository / Location | Canonical Anchor |
|---|---|---|
| **Frozen S2 Core** | `p10-core` | Commit `fa7878a538f56ee9b3c8008ca71e93c04c69ecf4` (Tag: `v0.3.0-s2-freeze`) |
| **Frozen Domain Profile** | `p10-core` (`spec/profiles/P10-BatteryML-S2-Profile-v0.1.md`) | Commit `dd88e6222fc717b557b7b5c2ebf6b1d725b50891` (Tag: `batteryml-s2-profile-v0.1-retro-freeze`), Digest: `d120f64339cd4a5eac8dd8ff26a3501986cdd7a36ddaa5632747bc84b0468f49` |
| **Historical Target Study** | `batteryml-protocol-robustness-s3` | Commit `4bdf33e27f3c8e1e22583ae41c13b096a81e5e38` (Tag: `v1.0.0`), Preregistration Commit: `0958e89a0e994ed9923da26e04e1f4bfb956ab7f` |
| **Executable Adapter** | `p10-audit-batteryml-s3-retro-s2` (`adapter/`) | Sealed via SHA-256 manifest prior to run |

---

## 3. Replay Workflow Architecture

The retrospective execution pipeline proceeds through five non-interactive stages:

```
Historical S3 Artifacts
         │
         ▼
[1. Evidence Inventory] ──► SOURCE_MANIFEST.json + references.json
         │
         ▼
[2. Executable Adapter] ──► Stage 1: Protocol Fault Detection
         │              ──► Stage 2: Admissibility Gates
         │              ──► Stage 3: Substantive Classifiers vs. Checker Crash
         │              ──► Fail-Closed Aggregation into 10 Obligations
         ▼
[3. Output Normalization] ──► obligation_trace.json + decision_view.json
         │
         ▼
[4. Formal Lean Adjudication] ──► ReplayDecision.lean
         │                    ──► lake env lean (p10-core@fa7878a)
         ▼
[5. Final Closure & Report] ──► decision_trace.json + RETROSPECTIVE_REPLAY_REPORT.md
```

---

## 4. Evaluated Claim Definition

The audit evaluates the concrete claim instantiated from S3:

```text
ProtocolRobustnessClaim := {
  claim_id        : "CLAIM-BATTERYML-MATR1-PROTOCOL-ROBUSTNESS-S3",
  target_models   : ["xgb", "variance", "ridge"],
  split_type      : "Minimum-Cost Protocol-Disjoint Cell Partition (K=64)",
  cell_population : "Severson et al. (2019) LFP Commercial Cells (MATR1)",
  shift_threshold : 0.05,       -- Material error increase defined as ΔMAE / ΔRMSE > 5%
  prevalence_limit: 0.05,       -- Maximum tolerable fraction of splits showing material shift (5%)
  gating_controls : ["Split A Baseline (Gate 1)", "Reference Split B (Gate 2)"]
}
```

---

## 5. Ten Evaluated Obligations ($\mathcal{O}_{\text{BatteryML}}$)

1. `O_SEED_BINDING`: Runtime PRNG seed digest matches frozen pre-registration commitment.
2. `O_HASH_TEST_MEMBERSHIP`: Test cell split partition table matches pre-committed digest.
3. `O_CONTROL_DATASET_BINDING`: Control dataset archive and API receipt confirm custody without uncommitted files.
4. `O_RUN_EXIT`: Host runner completed with exit code 0 without external kill or unhandled crash.
5. `O_FIT_COUNT`: Complete execution of all 264 pre-registered fits ($66 \text{ splits} \times 4 \text{ models}$).
6. `O_CTRL_GATE1`: Split A baseline positive control satisfies pre-registered error tolerances.
7. `O_CTRL_GATE2`: Reference Split B baseline reproduces historical calibration bounds.
8. `O_RECOMPUTE_PREDICTIONS`: Clean-room recomputed RMSE/MAE from raw CSVs match reported receipts within $10^{-4}$.
9. `O_STATISTICAL_PREVALENCE`: Material shift prevalence $p \le 0.05$ across all target models in the claim.
10. `O_DUMMY_BENCHMARK_SEPARATION`: Candidate models significantly outperform zero-rule dummy regressor.

---

## 6. Execution and Reporting Guarantees

1. The adapter is implemented purely in Python 3.12 without human inputs during execution.
2. The final decision is rendered exclusively by the compiled Lean 4 core `adjudicate` function.
3. No intermediate output shall cause an adjustment to adapter code, thresholds, or evidence definitions.
