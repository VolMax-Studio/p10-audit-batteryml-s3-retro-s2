# Replay Plan Amendment 002: Claim Demarcation, Dummy Parameters, and Prediction Manifest Binding

**Document Identifier:** `AMENDMENT-002-P10-AUDIT-BATTERYML-S3-RETRO-S2`  
**Date:** 2026-09-20  
**Authority:** VolMax Studio Lab & Adjudication Working Group  
**Target Document:** `REPLAY_PLAN.md` (§4 Evaluated Claim & §5 Obligations)  
**Status:** **ACTIVE / PENDING OPERATOR RATIFICATION**  

---

## 1. Claim Demarcation & Provenance ($C_{\text{P10\_RETRO}}$)

Run-003 formally evaluates the auditor-constructed P10 retrospective conjunctive claim:

```text
C_P10_RETRO := "All candidate architectures ['xgb', 'variance', 'ridge'] simultaneously 
                maintain protocol-disjoint cycle-life prediction robustness under 
                positive error degradation D > 0.10 with prevalence <= 50% on MATR1 LFP cells."
```

### Critical Epistemic Distinction
- **Target Study Native Logic:** The target study's native evaluation code (`s3_adjudication.py` @ `0958e89...`) evaluates a 4-category cascade (`NO_MATERIAL_SIGNAL`, `ROBUST_SYSTEMATIC_EFFECT`, `MODEL_SPECIFIC`, `HETEROGENEOUS_SPLIT_DEPENDENT`) using two-sided metric shift $p^{\text{abs}} = \Pr(|D| \ge 0.10)$. In S3, because exactly one model (Ridge) was materially prevalent, the native logic yielded **`MODEL_SPECIFIC`**.
- **P10 Retrospective Claim:** Under P10-BatteryML-S2-Profile-v0.1, the claim is strictly conjunctive across `target_models`. A failure of any single candidate architecture evaluates obligation `O_STATISTICAL_PREVALENCE` to `violated`.
- **Demarcation Statement:** $C_{\text{P10\_RETRO}}$ does not replace, invalidate, or contradict the target study's native `MODEL_SPECIFIC` categorization. The two protocols answer fundamentally different questions over the same underlying evidence.

---

## 2. Shift Degradation Metric Definition

The operational shift metric for $C_{\text{P10\_RETRO}}$ is strictly fixed to **positive relative error degradation**:

$$D_{m,s} = \frac{\text{RMSE}_{m,s} - \text{RMSE}_{m,\text{base}}}{\text{RMSE}_{m,\text{base}}} > 0.10$$

Where $\text{RMSE}_{m,\text{base}}$ is the benchmark performance of model $m$ on Split A (positive control Gate 1). A split $s$ exhibits material degradation if and only if $D_{m,s} > 0.10$.

---

## 3. Explicit Dummy Separation Parameters

To eliminate any undeclared evaluator discretion, `O_DUMMY_BENCHMARK_SEPARATION` is bound to explicit parameters:
- **`dummy_skill_margin`:** $0.0$ (demands $\text{RMSE}_{\text{model}} < \text{RMSE}_{\text{dummy}}$, equivalent to $\text{Skill} > 0$);
- **`required_separation_prevalence`:** $0.95$ (candidate models must outperform the zero-rule dummy in $\ge 95\%$ of all model-split comparisons).

---

## 4. Cryptographic Binding to Prediction Input Manifest

To ensure that recalculation and prevalence metrics derive directly and verifiably from raw tables rather than target adjudication summaries:
- All 264 per-cell prediction CSVs are cataloged in `PREDICTION_INPUT_MANIFEST.json`;
- Canonical Manifest Digest:
  `57c55989de3545254d42b9fb801e3dd20155a78cfb1126266aa44f5a1ce298c8`
- Obligations `O_RECOMPUTE_PREDICTIONS`, `O_STATISTICAL_PREVALENCE`, and `O_DUMMY_BENCHMARK_SEPARATION` bind this manifest digest as their primary evidence source. Target adjudication JSONs are treated strictly as external comparison references.
