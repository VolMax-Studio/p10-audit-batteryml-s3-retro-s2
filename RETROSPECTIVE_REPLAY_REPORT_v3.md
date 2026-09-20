# Retrospective Replay Report: BatteryML S3 under P10-Core S2 (Run-003 Evidence-Bound Conformance)

**Report Identifier:** `REPORT-P10-AUDIT-BATTERYML-S3-RETRO-S2-RUN-003`  
**Date:** 2026-09-20  
**Authority:** VolMax Studio Lab & Adjudication Working Group  
**Execution Status:** **EXECUTION COMPLETE / SPREMNO ZA HUMAN RATIFICATION**  
**Ratification Status:** **PENDING OPERATOR (IVAN NESTOROV [L3]) RATIFICATION**  
**Epistemic Category:** Retrospective Conformance Deployment over $C_{\text{P10\_RETRO}}$ (Field Demonstration)  
**Parent Framework:** P10-Core v0.3 — S2 Semantic Core  

---

> [!IMPORTANT]
> **FORMAL TRUST BOUNDARY DISCLOSURE**  
> The empirical ingestion, file parsing, and numerical metric computations over raw BatteryML evidence (1,402 files, including all 264 per-cell prediction CSVs) are performed exclusively by the Python domain adapter (`adapter/batteryml_s2_adapter.py` v0.3). The Lean 4 formalization (`p10-core@fa7878a...`) formally verifies and governs **only the deterministic precedence traversal and terminal adjudication** over the resulting normalized 6-field `DecisionView`. All empirical checks collapse into boolean `EvalStatus` indicators before the Lean kernel executes.

---

## 1. Executive Summary & Epistemic Demarcation ($C_{\text{P10\_RETRO}}$ vs S3 Native Adjudication)

$$\boxed{\textbf{RETROSPECTIVE CONFORMANCE DEPLOYMENT} \neq \textbf{NEW CONFIRMATORY BATTERY RESULT}}$$

This report records the clean execution of **Run-003**, conducted under the pre-execution freeze at commit `e952f00` and governed by [REPLAY_PLAN_AMENDMENT_002.md](file:///home/volmax-studio/volmax-projects/iot2/p10-audit-batteryml-s3-retro-s2/REPLAY_PLAN_AMENDMENT_002.md). Run-003 comprehensively addresses Gate Blockers A-01 through A-08 from Run-002.

### Epistemic Demarcation of Evaluated Claims
A central finding established during gate review is the distinction between two formal claims evaluated on the same historical data:

1. **Target Study Native Claim ($C_{\text{S3}}$):**
   The historical study `batteryml-protocol-robustness-s3` pre-registered a 4-category adjudication cascade implemented in `s3_adjudication.py` (lines 188–199) using two-sided metric shift $p^{\text{abs}} = \Pr(|D| \ge 0.10)$. In S3, because exactly one model (Ridge) was materially prevalent ($58/64 = 90.63\% \ge 50\%$) while XGBoost ($28/64 = 43.75\%$) and Variance ($20/64 = 31.25\%$) remained below the limit, the study's native logic yielded:
   $$\boxed{\text{Native S3 Adjudication} \longrightarrow \textbf{MODEL\_SPECIFIC}}$$
   The target study did not formulate or assert a universal conjunctive claim across all models.

2. **Auditor-Constructed P10 Retrospective Claim ($C_{\text{P10\_RETRO}}$):**
   The P10 retrospective replay evaluates a strictly conjunctive robustness assertion over the historical split data:
   $$C_{\text{P10\_RETRO}} := \bigwedge_{m \in \{\text{xgb}, \text{variance}, \text{ridge}\}} \left( \Pr\left(D_{m,s} > 0.10\right) \le 0.50 \right)$$
   Where $D_{m,s} = \frac{\text{RMSE}_{m,s} - \text{RMSE}_{m,\text{base}}}{\text{RMSE}_{m,\text{base}}}$ represents **positive relative error degradation** relative to the Split A baseline.
   Under $C_{\text{P10\_RETRO}}$, Ridge exhibits positive degradation on 55 out of 64 splits ($85.94\% > 50\%$). Under P10 conjunctive profile semantics, this single model failure evaluates `O_STATISTICAL_PREVALENCE` to `violated`.

$$\boxed{\text{Terminal Outcome under } C_{\text{P10\_RETRO}} \longrightarrow \textbf{NotVerified}}$$

**Demarcation Conclusion:** $C_{\text{P10\_RETRO}}$ does not replace, invalidate, or contradict S3's native `MODEL_SPECIFIC` classification. The two engines answer distinct formal claims over the identical cryptographically bound dataset. Ridge's failure refutes the conjunctive claim $C_{\text{P10\_RETRO}}$, not S3's categorical adjudication.

---

## 2. Provenance Hexa-Pinning

All components of Run-003 are cryptographically bound prior to execution:

| Provenance Anchor | Component | Cryptographic Identity |
|---|---|---|
| **Frozen S2 Core** | Lean 4 Adjudication Core | Commit `fa7878a538f56ee9b3c8008ca71e93c04c69ecf4` (Tag: `v0.3.0-s2-freeze`) |
| **Frozen Domain Profile** | BatteryML S2 Profile Specification v0.1 | Commit `dd88e6222fc717b557b7b5c2ebf6b1d725b50891` (Tag: `batteryml-s2-profile-v0.1-retro-freeze`), Digest `d120f64339cd4a5eac8dd8ff26a3501986cdd7a36ddaa5632747bc84b0468f49` |
| **Historical Target Study** | `batteryml-protocol-robustness-s3` | Commit `4bdf33e27f3c8e1e22583ae41c13b096a81e5e38` (Tag: `v1.0.0`), Preregistration Commit: `0958e89a0e994ed9923da26e04e1f4bfb956ab7f` |
| **Prediction Input Manifest** | Catalog of all 264 prediction CSVs | `PREDICTION_INPUT_MANIFEST.json` (Digest: `57c55989de3545254d42b9fb801e3dd20155a78cfb1126266aa44f5a1ce298c8`) |
| **Replay Adapter Pre-Freeze** | `adapter/batteryml_s2_adapter.py` (v0.3) | Commit `e952f0025b22a14ae9f7ff93d8c4202afbdbc3c0` (Adapter Digest: `1c0ef1766d17aa09ae013fa0b1fdd6c43d5c4bf58430967d84a9b863b3bc2841`) |
| **Governing Plan Amendment** | `REPLAY_PLAN_AMENDMENT_002.md` | Pre-execution binding of $C_{\text{P10\_RETRO}}$, dummy parameters, and prediction manifest |

---

## 3. Evaluated Claim Specification ($C_{\text{P10\_RETRO}}$)

Declared in `adapter/schema/claim_c_p10_retro.json` prior to execution:

```json
{
  "claim_id": "CLAIM-C-P10-RETRO-CONJUNCTIVE-ROBUSTNESS",
  "provenance_note": "Auditor-constructed P10 retrospective conjunctive claim over historical S3 evidence asserting simultaneous robustness across ['xgb', 'variance', 'ridge'] under positive degradation (D > 0.10). Distinct from S3's native 4-category logic (s3_adjudication.py), which evaluated to MODEL_SPECIFIC under two-sided |D| >= 0.10.",
  "target_models": ["xgb", "variance", "ridge"],
  "split_type": "Minimum-Cost Protocol-Disjoint Cell Partition (K=64)",
  "cell_population": "Severson et al. (2019) LFP Commercial Cells (MATR1)",
  "shift_threshold": 0.10,
  "shift_direction": "positive_degradation_only",
  "prevalence_limit": 0.50,
  "gating_controls": [
    "Split A Baseline (Gate 1)",
    "Reference Split B (Gate 2)"
  ],
  "dummy_parameters": {
    "dummy_skill_margin": 0.0,
    "required_separation_prevalence": 0.95
  }
}
```

---

## 4. Obligation-Level Evaluation Trace (All 10 Obligations)

Every obligation was evaluated directly by Adapter v0.3 against admissible evidence without referencing target summary JSONs:

| # | Obligation ID | Required Evidence | Admissible | Witness Class | EvalStatus | Failure Tag | Reason Code |
|---|---|---|---|---|---|---|---|
| 1 | `O_SEED_BINDING` | `s3-sampler-ranks.json`, `execution-closure.json` | True | `satisfied` | **`satisfied`** | None | `PRNG_SEED_AND_STREAM_VERIFIED` |
| 2 | `O_HASH_TEST_MEMBERSHIP` | `s3-test-membership-commitment.csv`, `s3-split-manifest.csv` | True | `satisfied` | **`satisfied`** | None | `MEMBERSHIP_HASH_VERIFIED` |
| 3 | `O_CONTROL_DATASET_BINDING`| `post-run-binding-receipt.json`, `control-dataset-files.sha256` | True | `satisfied` | **`satisfied`** | None | `CONTROL_DATASET_CUSTODY_VERIFIED` |
| 4 | `O_RUN_EXIT` | `batteryml-protocol-robustness-s3-run.log`, `completion-receipt.json` | True | `satisfied` | **`satisfied`** | None | `DRIVER_CLEAN_COMPLETION` |
| 5 | `O_FIT_COUNT` | `execution-closure.json` (264 fits) | True | `satisfied` | **`satisfied`** | None | `ALL_FITS_PRESENT` |
| 6 | `O_CTRL_GATE1` | `gate-1-positive-control-a.json` | True | `satisfied` | **`satisfied`** | None | `GATE1_BASELINE_REPRODUCED` |
| 7 | `O_CTRL_GATE2` | `gate-2-reference-split-b.json` | True | `satisfied` | **`satisfied`** | None | `GATE2_REFERENCE_REPRODUCED` |
| 8 | `O_RECOMPUTE_PREDICTIONS` | `PREDICTION_INPUT_MANIFEST.json`, `verify_s3_recomputation.py` | True | `satisfied` | **`satisfied`** | None | `ALL_264_FITS_RECOMPUTED_MATCH` |
| 9 | `O_STATISTICAL_PREVALENCE`| `PREDICTION_INPUT_MANIFEST.json`, `CLAIM_C_P10_RETRO_SPEC` | True | `violated` | **`violated`** | `F_THRESHOLD_EXCEEDED` | `THRESHOLD_EXCEEDED_FOR_RIDGE` |
| 10| `O_DUMMY_BENCHMARK_SEPARATION`| `PREDICTION_INPUT_MANIFEST.json` (192 comparisons) | True | `satisfied` | **`satisfied`** | None | `DUMMY_BENCHMARK_SEPARATION_VERIFIED` |

### 4.1 Direct CSV Empirical Analysis (`O_STATISTICAL_PREVALENCE`)
*(Evaluated directly from all 264 raw prediction CSVs cataloged in `PREDICTION_INPUT_MANIFEST.json`)*:

The adapter computed both the positive degradation metric ($D > 0.10$) specified by $C_{\text{P10\_RETRO}}$ and the two-sided absolute shift ($|D| \ge 0.10$) from S3's native logic:

| Model Architecture | Positive Degradation Splits ($D > 0.10$) | $p_{\text{pos}}$ | Two-Sided Absolute Splits ($|D| \ge 0.10$) | $p_{\text{abs}}$ | Threshold Exceeded? |
|---|---|---|---|---|---|
| **XGBoost (`xgb`)** | 18 / 64 | 28.125% | 28 / 64 | 43.750% | False ($\le 50\%$) |
| **Variance (`variance`)** | 19 / 64 | 29.688% | 20 / 64 | 31.250% | False ($\le 50\%$) |
| **Ridge Regression (`ridge`)** | **55 / 64** | **85.938%** | **58 / 64** | **90.625%** | **True ($> 50\%$)** |

Because $C_{\text{P10\_RETRO}}$ is strictly conjunctive across `target_models`, Ridge's breach of the $50\%$ prevalence ceiling evaluates `O_STATISTICAL_PREVALENCE` to `violated`.

### 4.2 Explicit Dummy Separation Verification (`O_DUMMY_BENCHMARK_SEPARATION`)
Evaluated under explicit parameters declared in Amendment 002:
- `dummy_skill_margin = 0.0` ($\text{RMSE}_{\text{dummy}} - \text{RMSE}_{\text{model}} > 0.0$)
- `required_separation_prevalence = 0.95`
- Total comparisons: 192 (64 splits $\times$ 3 candidate models)
- Inversions observed: 1 (Ridge on Split 32 had $\text{RMSE}_{\text{ridge}} \ge \text{RMSE}_{\text{dummy}}$)
- Achieved separation rate: $191 / 192 = 99.479\% \ge 95.000\%$
- Evaluated status: **`satisfied`**.

---

## 5. Formal Adjudication & Precedence Execution

The generated `DecisionView` was rendered into `run-003-evidence-bound-conformance/ReplayDecision.lean`.

### Verbatim Executed Lean Harness (Run-003)
*(Exact byte-for-byte representation of the executed Lean harness)*:

```lean
import P10Core.Model.AdjudicationAutomaton

open P10Core.Model.AdjudicationAutomaton

def replayDecisionView : DecisionView := {
  protocolFault := none,
  falsifiable := true,
  obligations := [
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.satisfied,
    EvalStatus.violated,
    EvalStatus.satisfied
  ],
  hasBlockingLimitation := false,
  hasNonBlockingLimitation := true,
  admissibleNovelFinding := false
}

def main : IO Unit := do
  let outcome := adjudicate replayDecisionView
  match outcome with
  | TerminalOutcome.protocolError err =>
    IO.println s!"TERMINAL_OUTCOME: PROTOCOL_ERROR ({repr err})"
  | TerminalOutcome.verdict v =>
    IO.println s!"TERMINAL_OUTCOME: VERDICT ({repr v})"
```

### Execution Output
Executed against `p10-core@fa7878a538f56ee9b3c8008ca71e93c04c69ecf4` via `lake env lean --run`:

```text
TERMINAL_OUTCOME: VERDICT (P10Core.Model.AdjudicationAutomaton.S2Verdict.notVerified)
```

### Adjudication Precedence:
1. **Step 1:** `protocolFault == none` and no `checkerError`.
2. **Step 2:** `obligations.contains violated == true` (index 8: `O_STATISTICAL_PREVALENCE`).
   $$\boxed{\operatorname{adjudicate}(\text{replayDecisionView}) = \operatorname{TerminalOutcome}.\operatorname{verdict}(\operatorname{S2Verdict}.\text{notVerified})}$$

### Enforcement of Strict Non-Softening:
Step 2 terminated immediately upon encountering `violated`. Even though `hasNonBlockingLimitation := true` (derived from `L_CHEMISTRY_LFP`), Step 6 was completely bypassed. Counterfactual testing confirms that if all obligations were satisfied, Step 6 would have granted `VerifiedWithLimitations`. Thus, the preemption was live and non-vacuous.

---

## 6. Audit Lineage & Blocker Resolution Matrix

| Issue ID | Classification | Identified Defect | Resolution in Run-003 | Status |
|---|---|---|---|---|
| **A-01** | Theorem Boundary / Claim Provenance | Auditor conjunctive claim confused with S3 native 4-category cascade. | Formalized $C_{\text{P10\_RETRO}}$ in Amendment 002; clarified that S3 native is `MODEL_SPECIFIC` while $C_{\text{P10\_RETRO}}$ is `NotVerified`. | **RESOLVED** |
| **A-02** | Governance Regression | Self-assigned `RATIFIED` status in Amendment 001. | Removed unauthorized keyword; status updated to `PENDING OPERATOR RATIFICATION`. | **RESOLVED** |
| **A-03** | Reproducibility / Audit Trace | Published adapter diff omitted the true post-run-001 mutation. | Extracted and published `adapter/POST_RUN_001_ADAPTER_MUTATION.diff` covering `548ed89` $\to$ `c3f9349`. | **RESOLVED** |
| **A-04** | Undeclared Evaluator Discretion | `O_DUMMY_BENCHMARK_SEPARATION` had no explicit parameters. | Bound to explicit `dummy_skill_margin = 0.0` and `required_separation_prevalence = 0.95`. | **RESOLVED** |
| **A-05** | Cryptographic Evidence Binding | Recompute & prevalence obligations did not hash raw CSVs. | Generated `PREDICTION_INPUT_MANIFEST.json` (264 CSVs) and bound both obligations directly to its digest. | **RESOLVED** |
| **A-06** | Disclosed Checker Rewrite | Adapter revisions not documented as new checkers. | Full adapter lineage declared: v0.1 (Run-001), v0.2 (Run-002), v0.3 (Run-003). | **RESOLVED** |
| **A-07** | Transcription vs Generation | Report v2 displayed decorated Lean harness. | Report v3 renders the exact verbatim bytes of the executed `ReplayDecision.lean`. | **RESOLVED** |
| **A-08** | Quotation Attribution | Logic block cited to `PREREGISTRATION.md` instead of `s3_adjudication.py`. | Corrected attribution across all governance documents. | **RESOLVED** |

---

## 7. Audit Governance Sign-Off State

- **Pre-Execution Freeze Commit:** `e952f0025b22a14ae9f7ff93d8c4202afbdbc3c0`
- **Adapter Execution Status:** Completed without post-freeze mutation or in-place edits.
- **Kernel Reproducibility:** Verified independently on `p10-core@fa7878a...`.
- **Final Report State:** `EXECUTION COMPLETE / SPREMNO ZA HUMAN RATIFICATION`.
- **Human Authority:** Awaiting formal review and ratification decision by Ivan Nestorov, Operator [L3].
