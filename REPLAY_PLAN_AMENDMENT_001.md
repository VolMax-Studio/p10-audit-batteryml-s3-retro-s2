# Replay Plan Amendment 001: Historical Threshold Alignment

**Document Identifier:** `AMENDMENT-001-P10-AUDIT-BATTERYML-S3-RETRO-S2`  
**Date:** 2026-09-20  
**Authority:** VolMax Studio Lab & Adjudication Working Group  
**Target Document:** `REPLAY_PLAN.md` (§4 Evaluated Claim Definition)  
**Status:** **ACTIVE / PENDING OPERATOR RATIFICATION**  

---

## 1. Description of Transcription Error

In `REPLAY_PLAN.md` §4, the evaluated claim parameters were transcribed as:
```text
shift_threshold  : 0.05       -- (Error: transcribed 5% error margin)
prevalence_limit : 0.05       -- (Error: transcribed 5% prevalence limit)
```

This transcription error deviated from the actual historical pre-registration of the target study.

---

## 2. Authoritative Historical Pre-Registration Source

The canonical historical parameters for `batteryml-protocol-robustness-s3` are permanently fixed at the governing pre-registration freeze commit `0958e89a0e994ed9923da26e04e1f4bfb956ab7f` (`PREREGISTRATION.md` lines 163–166):

```yaml
metrics:
  primary: rmse
  secondary: mae
  material_relative_change: 0.10
  material_prevalence: 0.50
```

and implemented in the study's execution script `s3_adjudication.py` (lines 188–199):

```python
# Evaluates material prevalence using threshold 0.10 and prevalence limit 0.50
p_abs_m = fraction(|D_RMSE| >= 0.10)
material_prevalent_m := (p_abs_m >= 0.50)
```

---

## 3. Amended Evaluated Claim Definition (v0.2 / Run-002)

To faithfully execute retrospective conformance against the authoritative historical target without rewriting `REPLAY_PLAN.md`, §4 is formally amended as follows:

```text
ProtocolRobustnessClaim := {
  claim_id        : "CLAIM-BATTERYML-MATR1-PROTOCOL-ROBUSTNESS-S3",
  target_models   : ["xgb", "variance", "ridge"],
  split_type      : "Minimum-Cost Protocol-Disjoint Cell Partition (K=64)",
  cell_population : "Severson et al. (2019) LFP Commercial Cells (MATR1)",
  shift_threshold : 0.10,       -- Material error increase defined as ΔRMSE >= 10%
  prevalence_limit: 0.50,       -- Maximum tolerable fraction of splits showing material shift (50%)
  gating_controls : ["Split A Baseline (Gate 1)", "Reference Split B (Gate 2)"]
}
```

---

## 4. Invariance & Preservation Note

The original `REPLAY_PLAN.md` remains unchanged in the Git repository as historical record. This amendment explicitly seals the claim specification prior to the execution of `run-002-corrected-conformance`.
