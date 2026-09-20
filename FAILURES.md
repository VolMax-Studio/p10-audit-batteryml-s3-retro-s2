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

---

## 4. Run-002 Audit Findings (A-01 through A-08) & Resolutions for Run-003

Following independent gate review of `run-002-corrected-conformance`, the terminal outcome was reproduced (`NotVerified`), and process failures F-R01, F-R03 (in report), and F-R04 were settled. However, eight specific findings (A-01 to A-08) required resolution upstream of the Lean core:

### Blockers

- **`A-01` — Claim Demarcation ($C_{\text{P10\_RETRO}}$ vs S3 Native Adjudication):**
  - *Observation:* S3's native engine (`s3_adjudication.py` lines 188–199) evaluates a 4-category cascade under two-sided relative error shift $|D| \ge 0.10$. With only Ridge exceeding $0.50$ ($p_{\text{abs}} = 0.90625$), S3 outputs category `MODEL_SPECIFIC`. It does not make a universal conjunctive claim. In contrast, the P10 retrospective replay evaluates an auditor-constructed conjunctive claim ($C_{\text{P10\_RETRO}}$) requiring **all** models in `["xgb", "variance", "ridge"]` to satisfy positive degradation $D > 0.10$ with prevalence $\le 50\%$.
  - *Resolution:* Pre-registered explicitly in `REPLAY_PLAN_AMENDMENT_002.md` and `adapter/schema/claim_c_p10_retro.json`. The replay is clarified as a retrospective evaluation of $C_{\text{P10\_RETRO}}$, not an execution of S3's native adjudication cascade. The terminal verdict `NotVerified` refutes $C_{\text{P10\_RETRO}}$ without contradicting S3's `MODEL_SPECIFIC` classification.
- **`A-02` — Governance Recurrence in Amendment 001:**
  - *Observation:* `REPLAY_PLAN_AMENDMENT_001.md` was titled `ACTIVE / RATIFIED PRE-EXECUTION AMENDMENT`.
  - *Resolution:* Removed `RATIFIED`. Status set to `ACTIVE / PENDING OPERATOR RATIFICATION`.
- **`A-03` — Published Mutation Diff Scope:**
  - *Observation:* `ADAPTER_REVISION_DIFF_v0.1_to_v0.2.diff` covered v0.1.1 to v0.2 rather than the true post-run-001 mutation.
  - *Resolution:* Extracted exact commit diff `git diff 548ed89 c3f9349 -- adapter/batteryml_s2_adapter.py` and published as `adapter/POST_RUN_001_ADAPTER_MUTATION.diff`.
- **`A-04` — Undeclared Pass Criterion in Dummy Benchmark Separation:**
  - *Observation:* `O_DUMMY_BENCHMARK_SEPARATION` evaluated 191/192 without citing explicit margin and rate thresholds.
  - *Resolution:* Declared explicit parameters in $C_{\text{P10\_RETRO}}$ (`dummy_skill_margin = 0.0`, `required_separation_prevalence = 0.95`). Adapter v0.3 strictly verifies these parameters against raw split CSVs.

### Majors

- **`A-05` — Cryptographic Evidence Binding for Prediction Tables:**
  - *Observation:* `O_RECOMPUTE_PREDICTIONS` hashed only the verification script; `O_STATISTICAL_PREVALENCE` hashed target study summary JSONs while claiming to be a clean-room distribution table.
  - *Resolution:* Generated `PREDICTION_INPUT_MANIFEST.json` and `.sha256` hashing all 264 `per-cell-predictions.csv` files. Bound both obligations directly to this manifest. Evaluated degradation statistics directly from the 264 raw CSVs without ingesting target study JSONs.
- **`A-06` — Disclosed Checker Rewrite:**
  - *Observation:* Adapter v0.2 was a major revision, not a re-frozen v0.1.
  - *Resolution:* Fully disclosed in lineage: Adapter v0.1 (Run-001, invalidated), v0.2 (Run-002, blocked), v0.3 (Run-003, evidence-bound pre-execution freeze).
- **`A-07` — Verbatim Lean Harness Display:**
  - *Observation:* Report v2 displayed decorated code with comments not present in the executed file.
  - *Resolution:* Report v3 renders the exact verbatim bytes of the executed `ReplayDecision.lean`.
- **`A-08` — Quotation Attribution:**
  - *Observation:* Formula attributed to `PREREGISTRATION.md` actually resided in `s3_adjudication.py`.
  - *Resolution:* Attribution corrected in `REPLAY_PLAN_AMENDMENT_001.md` and Report v3.

---

## 5. Run-003 Gate Review Findings (B-01 through B-05) & Closure

Following independent gate review of `run-003-evidence-bound-conformance`, the gate reviewer performed an end-to-end clean-room recomputation directly from the 264 raw prediction CSV tables of `batteryml-protocol-robustness-s3@v1.0.0`. All figures were independently verified to 100% precision:
- XGBoost: $18/64$ ($p_{\text{pos}} = 28.125\%$), $28/64$ ($p_{\text{abs}} = 43.75\%$)
- Variance: $19/64$ ($p_{\text{pos}} = 29.688\%$), $20/64$ ($p_{\text{abs}} = 31.25\%$)
- Ridge: $55/64$ ($p_{\text{pos}} = 85.938\%$), $58/64$ ($p_{\text{abs}} = 90.625\%$)
- Dummy benchmark separation: $191/192 = 99.4792\%$ ($\ge 95\%$, 1 inversion).

### Itemized Findings & Resolutions:

- **`B-01` — Submission of Artifact Trail (Downgraded to Records Closure):**
  - *Status:* **CLOSED.** All Run-003 artifacts (`obligation_trace.json`, `decision_view.json`, `ReplayDecision.lean`, `adjudication_stdout.log`, `PREDICTION_INPUT_MANIFEST.json`, adapter v0.3, and `POST_RUN_001_ADAPTER_MUTATION.diff`) are committed and tracked in the repository.
- **`B-02` — Citation Line Bounds in Amendment 001:**
  - *Status:* **CLOSED.** Citation corrected to `s3_adjudication.py` lines 141–145 where `p_abs`, `p_pos`, and `mat_prev` are evaluated, extracted verbatim from source bytes.
- **`B-03` — Provenance of Dummy Parameters (Withdrawn / Narrowed):**
  - *Status:* **CLOSED.** The gate reviewer retracted B-03 upon verifying line 176 of `spec/profiles/P10-BatteryML-S2-Profile-v0.1.md` (@ `dd88e62...`), which explicitly pre-registers the $\ge 95\%$ separation threshold. Only `dummy_skill_margin = 0.0` ($\delta_{\text{dummy}} = 0$) represents an auditor-chosen retrospective instantiation.
- **`B-04` — Inequality Comparator ($D > 0.10$ vs $D \ge 0.10$):**
  - *Status:* **CLOSED (Outcome-Invariant Documentation Defect).** Independent recomputation across all $64 \times 3 = 192$ model-split evaluations revealed zero cases where $D = 0.10$ exactly (nearest split was $2.8 \times 10^{-4}$ away). Thus $\operatorname{count}(D > 0.10) = \operatorname{count}(D \ge 0.10)$ identically. Amendment 002 is documented as $D \ge 0.10$ to match `s3_adjudication.py:142`. No execution rerun required.
- **`B-05` — Epistemic Framing of Retrospective Claim:**
  - *Status:* **CLOSED.** Phrasing claiming absence of post-hoc discretion in claim selection is removed. Framing is formally declared as *deterministic adjudication of an explicitly retrospective, post-hoc-instantiated claim over cryptographically bound evidence*.

$$\boxed{\textbf{FINAL GATE REVIEW DISPOSITION: PASS WITH LIMITATIONS}}$$
