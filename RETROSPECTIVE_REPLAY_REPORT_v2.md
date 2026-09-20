# Retrospective Replay Report: BatteryML S3 under P10-Core S2 (Run-002 Conformance)

**Report Identifier:** `REPORT-P10-AUDIT-BATTERYML-S3-RETRO-S2-RUN-002`  
**Date:** 2026-09-20  
**Authority:** VolMax Studio Lab & Adjudication Working Group  
**Execution Status:** **EXECUTION COMPLETE / SPREMNO ZA HUMAN RATIFICATION**  
**Ratification Status:** **PENDING OPERATOR (IVAN NESTOROV [L3]) RATIFICATION**  
**Epistemic Category:** Retrospective Conformance Deployment (Non-Confirmatory Field Demonstration)  
**Parent Framework:** P10-Core v0.3 — S2 Semantic Core  

---

> [!IMPORTANT]
> **FORMAL TRUST BOUNDARY DISCLOSURE**  
> The empirical ingestion, file parsing, and numerical metric computations over raw BatteryML evidence (1,402 files, 264 per-cell prediction CSVs) are performed exclusively by the Python domain adapter. The Lean 4 formalization (`p10-core@fa7878a...`) formally verifies and governs **only the deterministic precedence traversal and terminal adjudication** over the resulting normalized 6-field `DecisionView`.

---

## 1. Executive Summary & Epistemic Demarcation

$$\boxed{\textbf{RETROSPECTIVE CONFORMANCE DEPLOYMENT} \neq \textbf{NEW CONFIRMATORY BATTERY RESULT}}$$

This report records the clean execution of **Run-002**, conducted following the formal invalidation of Run-001 (documented in [FAILURES.md](file:///home/volmax-studio/volmax-projects/iot2/p10-audit-batteryml-s3-retro-s2/FAILURES.md)) and the pre-execution adoption of [REPLAY_PLAN_AMENDMENT_001.md](file:///home/volmax-studio/volmax-projects/iot2/p10-audit-batteryml-s3-retro-s2/REPLAY_PLAN_AMENDMENT_001.md).

Because the empirical performance data of the target study `batteryml-protocol-robustness-s3` were established prior to profile authoring, this retrospective replay does **not** test prospective falsifiability. It demonstrates:
1. **Deterministic Precedence:** Raw ML experiment telemetry is translated into a normalized `DecisionView` and adjudicated by an immutable Lean 4 automaton without human intervention;
2. **Live Non-Softening Preemption:** Step 2 actively preempts an otherwise live Step 6 limitation branch;
3. **Negative Verdict Integrity:** The system issues `NotVerified` deterministically when substantive obligations are breached, without post-hoc rule softening.

### Formal Adjudication Result
- **Terminal Outcome:** $\boxed{\mathcal{V}^* = \textbf{NotVerified}}$
- **Lean Kernel Output:** `TERMINAL_OUTCOME: VERDICT (P10Core.Model.AdjudicationAutomaton.S2Verdict.notVerified)`
- **Adjudication Path:** S2 Step 2 (Violated Obligation Precedence)
- **Primary Refuting Obligation:** `O_STATISTICAL_PREVALENCE`
- **Primary Failure Tag:** `F_THRESHOLD_EXCEEDED`
- **Protocol Faults:** None (`protocolFault := none`)
- **Admissibility Failures:** None (All 1,402 evidence files admissible)

---

## 2. Provenance Quadruple-Pinning

| Provenance Anchor | Component | Cryptographic Identity |
|---|---|---|
| **Frozen S2 Core** | Lean 4 Adjudication Core | Commit `fa7878a538f56ee9b3c8008ca71e93c04c69ecf4` (Tag: `v0.3.0-s2-freeze`) |
| **Frozen Domain Profile** | BatteryML S2 Profile Specification v0.1 | Commit `dd88e6222fc717b557b7b5c2ebf6b1d725b50891` (Tag: `batteryml-s2-profile-v0.1-retro-freeze`), Digest `d120f64339cd4a5eac8dd8ff26a3501986cdd7a36ddaa5632747bc84b0468f49` |
| **Historical Target Study** | `batteryml-protocol-robustness-s3` | Commit `4bdf33e27f3c8e1e22583ae41c13b096a81e5e38` (Tag: `v1.0.0`), Preregistration Commit: `0958e89a0e994ed9923da26e04e1f4bfb956ab7f` |
| **Replay Adapter Implementation** | `adapter/batteryml_s2_adapter.py` (v0.2) | Commit `5977a192c730e84b8686f3459c39433430159d3e` (Manifest Digest: `569b8d52dfbc676bc6a0e00870dcb23479e7665f0776719eecbaa31d5d9e58af`) |
| **Governing Plan Amendment** | `REPLAY_PLAN_AMENDMENT_001.md` | Formal adoption of historical $0.10 / 0.50$ thresholds from S3 preregistration |

---

## 3. Evaluated Claim

Pursuant to [REPLAY_PLAN_AMENDMENT_001.md](file:///home/volmax-studio/volmax-projects/iot2/p10-audit-batteryml-s3-retro-s2/REPLAY_PLAN_AMENDMENT_001.md), the replay evaluated the general robustness claim under the authoritative historical thresholds:

```text
ProtocolRobustnessClaim := {
  claim_id        : "CLAIM-BATTERYML-MATR1-PROTOCOL-ROBUSTNESS-S3",
  target_models   : ["xgb", "variance", "ridge"],
  split_type      : "Minimum-Cost Protocol-Disjoint Cell Partition (K=64)",
  cell_population : "Severson et al. (2019) LFP Commercial Cells (MATR1)",
  shift_threshold : 0.10,   -- Material error increase defined as ΔRMSE >= 10%
  prevalence_limit: 0.50,   -- Maximum tolerable fraction of splits showing material shift (50%)
  gating_controls : ["Split A Baseline (Gate 1)", "Reference Split B (Gate 2)"]
}
```

---

## 4. Obligation-Level Evaluation Trace (All 10 Obligations)

| # | Obligation ID | Required Evidence | Admissible | Witness Class | EvalStatus | Failure Tag | Reason Code |
|---|---|---|---|---|---|---|---|
| 1 | `O_SEED_BINDING` | `s3-sampler-ranks.json`, `execution-closure.json` | True | `satisfied` | **`satisfied`** | None | `PRNG_SEED_AND_STREAM_VERIFIED` |
| 2 | `O_HASH_TEST_MEMBERSHIP` | `s3-test-membership-commitment.csv`, `s3-split-manifest.csv` | True | `satisfied` | **`satisfied`** | None | `MEMBERSHIP_HASH_VERIFIED` |
| 3 | `O_CONTROL_DATASET_BINDING`| `post-run-binding-receipt.json`, `control-dataset-files.sha256` | True | `satisfied` | **`satisfied`** | None | `CONTROL_DATASET_CUSTODY_VERIFIED` |
| 4 | `O_RUN_EXIT` | `batteryml-protocol-robustness-s3-run.log`, `completion-receipt.json` | True | `satisfied` | **`satisfied`** | None | `DRIVER_CLEAN_COMPLETION` |
| 5 | `O_FIT_COUNT` | `execution-closure.json`, 264 prediction CSVs | True | `satisfied` | **`satisfied`** | None | `ALL_FITS_PRESENT` (264/264) |
| 6 | `O_CTRL_GATE1` | `gate-1-positive-control-a.json` | True | `satisfied` | **`satisfied`** | None | `GATE1_BASELINE_REPRODUCED` |
| 7 | `O_CTRL_GATE2` | `gate-2-reference-split-b.json` | True | `satisfied` | **`satisfied`** | None | `GATE2_REFERENCE_REPRODUCED` |
| 8 | `O_RECOMPUTE_PREDICTIONS` | `verify_s3_recomputation.py`, 264 raw CSVs | True | `satisfied` | **`satisfied`** | None | `ALL_264_FITS_RECOMPUTED_MATCH` |
| 9 | `O_STATISTICAL_PREVALENCE`| 64 sampled prediction splits $\times$ 4 models | True | `violated` | **`violated`** | `F_THRESHOLD_EXCEEDED` | `THRESHOLD_EXCEEDED_FOR_RIDGE` |
| 10| `O_DUMMY_BENCHMARK_SEPARATION`| Prediction CSVs vs Dummy baseline | True | `satisfied` | **`satisfied`** | None | `DUMMY_BENCHMARK_SEPARATION_VERIFIED` |

### 4.1 Substantive Refutation Analysis (`O_STATISTICAL_PREVALENCE`)
*(Note: Split counts below are checker outputs derived from raw per-cell prediction tables).*

Out of 64 protocol-disjoint test splits under the 10% shift threshold ($\Delta\text{RMSE} \ge 0.10$):
- **XGBoost (`xgb`):** 18/64 splits exhibited material shift ($p = 0.2812 \le 0.50$).
- **Variance Model (`variance`):** 19/64 splits exhibited material shift ($p = 0.2969 \le 0.50$).
- **Ridge Regression (`ridge`):** **55/64 splits exhibited material shift ($p = 0.8594 > 0.50$)**.

Because the claim asserted protocol robustness across all three models `["xgb", "variance", "ridge"]`, the failure of Ridge regression ($85.94\% > 50.00\%$) mathematically refutes the general claim of protocol robustness, triggering failure tag `F_THRESHOLD_EXCEEDED` and evaluating `O_STATISTICAL_PREVALENCE` to `violated`.

---

## 5. Formal Adjudication & Precedence Execution

The generated `DecisionView` was passed to the frozen Lean 4 core:

```lean
def replayDecisionView : DecisionView := {
  protocolFault := none,
  falsifiable := true,
  obligations := [
    EvalStatus.satisfied,  -- O_SEED_BINDING
    EvalStatus.satisfied,  -- O_HASH_TEST_MEMBERSHIP
    EvalStatus.satisfied,  -- O_CONTROL_DATASET_BINDING
    EvalStatus.satisfied,  -- O_RUN_EXIT
    EvalStatus.satisfied,  -- O_FIT_COUNT
    EvalStatus.satisfied,  -- O_CTRL_GATE1
    EvalStatus.satisfied,  -- O_CTRL_GATE2
    EvalStatus.satisfied,  -- O_RECOMPUTE_PREDICTIONS
    EvalStatus.violated,   -- O_STATISTICAL_PREVALENCE
    EvalStatus.satisfied   -- O_DUMMY_BENCHMARK_SEPARATION
  ],
  hasBlockingLimitation := false,
  hasNonBlockingLimitation := true,
  admissibleNovelFinding := false
}
```

### Precedence Traversal:
1. **Step 1 (Protocol Faults & Checker Errors):** `protocolFault == none` and `obligations.contains checkerError == false`. Passes to Step 2.
2. **Step 2 (Violated Obligations Precedence):** `obligations.contains violated == true` (due to `O_STATISTICAL_PREVALENCE`).
   $$\boxed{\operatorname{adjudicate}(\text{replayDecisionView}) = \operatorname{TerminalOutcome}.\operatorname{verdict}(\operatorname{S2Verdict}.\text{notVerified})}$$

### Live Non-Softening Invariant Enforced:
Independent counterfactual verification confirmed that under an all-satisfied obligation vector with `hasNonBlockingLimitation := true`, Step 6 is reached and returns `VerifiedWithLimitations`. In the actual execution, Step 2 **actively preempted** this live branch, issuing `NotVerified`. The formal core strictly prevented the non-blocking limitation from softening the empirical refutation.

---

## 6. Audit Governance & Readiness

- **Run-001 Record:** Preserved as invalidated evidence in `run-001/` and `FAILURES.md`.
- **Run-002 Record:** Clean execution from pre-execution freeze `5977a19...` without intermediate code modifications.
- **Current State:** `EXECUTION COMPLETE / SPREMNO ZA HUMAN RATIFICATION`.
- **Next Action:** Pending final human authorization by Ivan Nestorov, Operator [L3].
