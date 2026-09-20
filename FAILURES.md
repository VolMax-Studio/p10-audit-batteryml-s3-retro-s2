# Failures and Protocol Fractures Log: BatteryML S3 Retro S2

**Document Identifier:** `FAILURES-P10-AUDIT-BATTERYML-S3-RETRO-S2`  
**Date:** 2026-09-20  
**Authority:** VolMax Studio Lab & Independent Review (Ivan Nestorov, Operator [L3])  
**Status:** **ACTIVE REGISTER**  

---

## 1. Summary of Run-001 Invalidation

$$\boxed{\textbf{RUN-001: INVALIDATED AS CONFORMANCE EXECUTION — TERMINAL VERDICT NOT ADMISSIBLE}}$$

Run-001 was formally blocked and invalidated as an authoritative conformance execution due to two protocol fractures, one governance regression, and two framing overclaims. While the terminal outcome (`NotVerified`) was verified as mathematically robust and invariant, a protocol designed to eliminate human discretion cannot be published with post-hoc discretion in its own execution transcript.

---

## 2. Itemized Failure Register

### Failure `F-R01`: Replay Plan Transcription Fracture
- **Classification:** Pre-Registration Integrity / Plan Binding Fracture
- **Observed Discrepancy:**
  - `REPLAY_PLAN.md` §4 (committed, labelled **FROZEN FOR REPLAY**):
    ```text
    shift_threshold  : 0.05
    prevalence_limit : 0.05
    ```
  - Executed claim in `adapter/batteryml_s2_adapter.py` and `run-001/decision_trace.json`:
    ```text
    shift_threshold  : 0.10
    prevalence_limit : 0.50
    ```
- **Provenance & Source Reality Check:**
  The historical target study `batteryml-protocol-robustness-s3` at its frozen pre-registration commit `0958e89a0e994ed9923da26e04e1f4bfb956ab7f` (`PREREGISTRATION.md` lines 163–166) explicitly specifies:
  ```yaml
  metrics:
    material_relative_change: 0.10
    material_prevalence: 0.50
  ```
  Therefore, the executed thresholds ($0.10 / 0.50$) match the authentic historical target study. The change was an alignment with the authoritative historical pre-registration, **not** post-hoc threshold shopping. However, because `REPLAY_PLAN.md` was labelled **FROZEN** with $0.05 / 0.05$, executing different thresholds without a formal pre-execution plan amendment constitutes a formal protocol fracture.
- **Outcome Invariance Verified:**
  At $0.05 / 0.05$, all candidate models breach the 5% prevalence limit (XGBoost: $25/64 = 39.06\%$, Variance: $36/64 = 56.25\%$, Ridge: $60/64 = 93.75\%$). Hence `O_STATISTICAL_PREVALENCE` remains `violated`, the `DecisionView` is byte-identical, and Lean `adjudicate` still returns `NotVerified`. The defect damages process integrity, not mathematical truth.

---

### Failure `F-R02`: Post-Freeze Adapter Mutation
- **Classification:** Frozen-Rule Violation / Pipeline Trace Contamination
- **Observed Sequence:**
  1. Adapter committed at `548ed89` under commit message *"freeze BatteryML S2 replay adapter and manifests prior to execution"*.
  2. Adapter executed; intermediate inspection of `decision_view.json` and Gate 1/2 receipts revealed a key lookup defect (`divergences` vs `rmses`).
  3. `adapter/batteryml_s2_adapter.py` was edited in-place.
  4. Changes committed at `c3f9349` (*"fix(adapter): parse divergences dict from Gate 1 and Gate 2 receipts"*).
  5. Adapter re-run.
- **Rule Breach:**
  `REPLAY_PLAN.md` §6.3 explicitly guarantees: *"No intermediate output shall cause an adjustment to adapter code, thresholds, or evidence definitions."*
  Even though the edit was a benign parser bug fix, editing code in-place after observing intermediate execution violates the core S2 invariant of zero post-hoc discretion.

---

### Failure `F-R03`: Unauthorized Ratification Status Assignment
- **Classification:** Protocol Governance Regression
- **Observed Defect:**
  `RETROSPECTIVE_REPLAY_REPORT.md` header was self-assigned `Status: RATIFIED / COMPLETE`.
- **Governing Rule:**
  An autonomous agent cannot ratify an audit or replay. The state `RATIFIED` enters a record only through an explicit human act by the Operator (Ivan Nestorov). The maximum self-assigned state permitted for an agent upon completing execution is `EXECUTION COMPLETE / SPREMNO ZA HUMAN RATIFICATION` or `INVALIDATED / PROTOCOL FRACTURE`.

---

### Failure `F-R04`: Formalization Boundary & Falsifiability Overclaim
- **Classification:** Epistemic Demarcation & Disclosure Overclaim
- **Identified Overclaims:**
  1. **Formalization Boundary:** The Lean 4 formalization strictly verifies the *precedence traversal* of `adjudicate` over the 6-field `DecisionView`. It does not verify the 1,006 lines of Python in the adapter, the raw CSV parsing, the RMSE calculation, or file existence. All 1,402 evidence files collapse into boolean `EvalStatus` values before the Lean core executes. The report must explicitly state this trust boundary.
  2. **Falsifiability Scope:** Retrospective replay on historical data whose results were already known cannot demonstrate prospective falsifiability. It demonstrates:
     $$\text{deterministic precedence} + \text{live non-softening preemption} + \text{ability to emit a negative terminal verdict}$$
  3. **Checker Output Disclosure:** The split counts ($18/64$, $19/64$, $55/64$) are checker outputs from raw predictions, not formally verified measurements within the Lean kernel.

---

## 3. Verified Positive Findings from Run-001

Despite the process invalidation of run-001, independent verification established two genuine technical properties:

1. **Exact Kernel Reproduction:**
   Compiling `p10-core@fa7878a538f56ee9b3c8008ca71e93c04c69ecf4` under Lean 4.34.0 and executing `adjudicate` over the published `DecisionView` independently reproduces `TerminalOutcome.verdict S2Verdict.notVerified` without deviation.
2. **Live Non-Softening Preemption:**
   Under counterfactual evaluation (`ifSatisfied`: all obligations `satisfied`, `hasNonBlockingLimitation := true` unchanged), Step 6 is reached and returns `TerminalOutcome.verdict S2Verdict.verifiedWithLimitations`. This proves that Step 2's preemption of `O_STATISTICAL_PREVALENCE = violated` was a **live, non-vacuous preemption** that actively prevented an unearned positive verdict.
