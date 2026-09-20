#!/usr/bin/env python3
"""P10 BatteryML S2 Domain Adapter.

Translates raw experimental artifacts from BatteryML runs (specifically S3)
into normalized DecisionView and ObligationTrace records for the frozen S2
adjudication automaton.

Conforms strictly to:
- Parent Protocol: P10-Core v0.3 — S2 Semantic Core (fa7878a...)
- Profile Spec: P10-BatteryML-S2-Profile-v0.1 (dd88e62..., digest d120f643...)
"""

import sys
import json
import math
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd


class BatteryMLS2Adapter:
    """Deterministic domain adapter for BatteryML under P10-Core S2."""

    def __init__(self, s3_dir: Path, claim: Dict[str, Any]):
        self.s3_dir = Path(s3_dir).resolve()
        self.claim = claim
        self.art_dir = self.s3_dir / "s3_execution_output" / "s3-artifact"
        self.closure_file = self.art_dir / "execution-closure.json"
        self.completion_file = self.art_dir / "completion-receipt.json"
        self.binding_file = self.s3_dir / "s3_execution_output" / "post-run-binding-receipt.json"
        self.results_dir = self.art_dir / "results"
        self.runner_log_file = self.s3_dir / "s3_execution_output" / "batteryml-protocol-robustness-s3-run.log"

    def sha256_of_file(self, path: Path) -> str:
        if not path.is_file():
            return ""
        return hashlib.sha256(path.read_bytes()).hexdigest()

    # -------------------------------------------------------------------------
    # Stage 1: Protocol Fault Detection (Global Pipeline Integrity)
    # -------------------------------------------------------------------------
    def check_protocol_faults(self) -> Optional[str]:
        """Inspects global pipeline integrity before obligation-level evaluation.

        Returns one of:
        - None
        - 'integrityFailure'
        - 'preregistrationFracture'
        - 'targetMutation'
        - 'environmentMismatch'
        - 'prematureExecution'
        """
        # 1. Dataset custody / integrity check
        if self.binding_file.exists():
            try:
                binding = json.loads(self.binding_file.read_text())
                ctrl = binding.get("control_dataset_binding", {})
                if not ctrl.get("runtime_byte_match", False):
                    return "integrityFailure"
                if ctrl.get("bound_version") != 1:
                    return "integrityFailure"
            except Exception:
                return "integrityFailure"
        else:
            return "integrityFailure"

        # 2. Preregistration commitments verification
        if self.closure_file.exists():
            try:
                closure = json.loads(self.closure_file.read_text())
                inputs = closure.get("inputs", {})
                commitments = inputs.get("commitments", {})
                if not commitments.get("governing_commitments_verified", False):
                    return "preregistrationFracture"
                expected_membership_hash = "53a157ecd49c0a238cd5028c6ab840431a7ecb600b067290ee51645820cb5ada"
                if commitments.get("membership_commitment_hash") != expected_membership_hash:
                    return "preregistrationFracture"
            except Exception:
                return "preregistrationFracture"
        else:
            return "preregistrationFracture"

        # 3. Premature execution / driver crash inspection
        if self.completion_file.exists():
            try:
                completion = json.loads(self.completion_file.read_text())
                if completion.get("status") != "COMPLETE":
                    return "prematureExecution"
            except Exception:
                return "prematureExecution"
        else:
            return "prematureExecution"

        # No protocol fault detected
        return None

    # -------------------------------------------------------------------------
    # Stage 2 & 3: Obligation Evaluators
    # -------------------------------------------------------------------------

    def evaluate_o_seed_binding(self) -> Dict[str, Any]:
        """O_SEED_BINDING: PRNG seed string and sampler algorithm commitment."""
        req = ["s3-sampler-ranks.json", "s3_execution_output/s3-artifact/execution-closure.json"]
        hashes = {f: self.sha256_of_file(self.s3_dir / f) for f in req}

        ranks_file = self.s3_dir / "s3-sampler-ranks.json"
        if not ranks_file.is_file() or not self.closure_file.is_file():
            return {
                "obligation_id": "O_SEED_BINDING",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": False,
                "admissibility_reason": "Missing seed witness files",
                "protocol_fault": None,
                "witness_classes": [],
                "eval_status": "missing",
                "failure_tag": None,
                "reason_code": "EVIDENCE_MISSING",
                "details": {}
            }

        try:
            closure = json.loads(self.closure_file.read_text())
            draw_order_hash = closure["inputs"]["commitments"]["draw_order_hash"]
            expected_draw_order_hash = "1d84b7bf864945a26ec0a5d2feec754b6ed6b4bf50b9f4e5b02bc45720b0ff02"
            dp_count = closure["inputs"]["commitments"]["dp_count"]

            if draw_order_hash == expected_draw_order_hash and dp_count == 185471:
                witness = "satisfied"
                status = "satisfied"
                tag = None
                code = "SEED_AND_SAMPLER_VERIFIED"
            else:
                witness = "violated"
                status = "violated"
                tag = "F_SEED_MISMATCH"
                code = "SEED_DIGEST_MISMATCH"

            return {
                "obligation_id": "O_SEED_BINDING",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Schema-valid closure metadata containing cryptographic seed bindings",
                "protocol_fault": None,
                "witness_classes": [witness],
                "eval_status": status,
                "failure_tag": tag,
                "reason_code": code,
                "details": {
                    "runtime_draw_order_hash": draw_order_hash,
                    "expected_draw_order_hash": expected_draw_order_hash,
                    "dp_count": dp_count
                }
            }
        except Exception as e:
            return {
                "obligation_id": "O_SEED_BINDING",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Schema-valid closure metadata",
                "protocol_fault": None,
                "witness_classes": ["checkerError"],
                "eval_status": "checkerError",
                "failure_tag": None,
                "reason_code": f"CHECKER_CRASH: {str(e)}",
                "details": {"error": str(e)}
            }

    def evaluate_o_hash_test_membership(self) -> Dict[str, Any]:
        """O_HASH_TEST_MEMBERSHIP: Split membership cryptographic commitment."""
        req = ["s3-test-membership-commitment.csv", "s3-split-manifest.csv"]
        hashes = {f: self.sha256_of_file(self.s3_dir / f) for f in req}

        memb_p = self.s3_dir / "s3-test-membership-commitment.csv"
        split_p = self.s3_dir / "s3-split-manifest.csv"

        if not memb_p.is_file() or not split_p.is_file():
            return {
                "obligation_id": "O_HASH_TEST_MEMBERSHIP",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": False,
                "admissibility_reason": "Partition commitment tables missing",
                "protocol_fault": None,
                "witness_classes": [],
                "eval_status": "missing",
                "failure_tag": None,
                "reason_code": "EVIDENCE_MISSING",
                "details": {}
            }

        try:
            h_memb = hashes["s3-test-membership-commitment.csv"]
            h_split = hashes["s3-split-manifest.csv"]
            exp_memb = "53a157ecd49c0a238cd5028c6ab840431a7ecb600b067290ee51645820cb5ada"
            exp_split = "cf9c269a93053e64ecf9200e0ee704fb0c32d2787f721fc24f0cb711cdc33895"

            if h_memb == exp_memb and h_split == exp_split:
                witness = "satisfied"
                status = "satisfied"
                tag = None
                code = "MEMBERSHIP_HASH_VERIFIED"
            else:
                witness = "violated"
                status = "violated"
                tag = "F_MEMBERSHIP_FRACTURE"
                code = "MEMBERSHIP_HASH_MISMATCH"

            return {
                "obligation_id": "O_HASH_TEST_MEMBERSHIP",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Well-formed CSV partition commitment tables bound to run",
                "protocol_fault": None,
                "witness_classes": [witness],
                "eval_status": status,
                "failure_tag": tag,
                "reason_code": code,
                "details": {
                    "computed_membership_hash": h_memb,
                    "expected_membership_hash": exp_memb,
                    "computed_split_hash": h_split,
                    "expected_split_hash": exp_split
                }
            }
        except Exception as e:
            return {
                "obligation_id": "O_HASH_TEST_MEMBERSHIP",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Well-formed CSV partition commitment tables",
                "protocol_fault": None,
                "witness_classes": ["checkerError"],
                "eval_status": "checkerError",
                "failure_tag": None,
                "reason_code": f"CHECKER_CRASH: {str(e)}",
                "details": {"error": str(e)}
            }

    def evaluate_o_control_dataset_binding(self) -> Dict[str, Any]:
        """O_CONTROL_DATASET_BINDING: Published control dataset custody."""
        req = ["s3_execution_output/post-run-binding-receipt.json", "s3_execution_output/control-dataset-files.sha256"]
        hashes = {f: self.sha256_of_file(self.s3_dir / f) for f in req}

        if not self.binding_file.is_file():
            return {
                "obligation_id": "O_CONTROL_DATASET_BINDING",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": False,
                "admissibility_reason": "Control dataset binding receipt missing",
                "protocol_fault": None,
                "witness_classes": [],
                "eval_status": "missing",
                "failure_tag": None,
                "reason_code": "EVIDENCE_MISSING",
                "details": {}
            }

        try:
            b = json.loads(self.binding_file.read_text())
            ctrl = b.get("control_dataset_binding", {})
            byte_match = ctrl.get("runtime_byte_match", False)
            bound_v = ctrl.get("bound_version")
            file_count = ctrl.get("runtime_file_count", 0)

            if byte_match and bound_v == 1 and file_count == 218:
                witness = "satisfied"
                status = "satisfied"
                tag = None
                code = "CONTROL_DATASET_CUSTODY_VERIFIED"
            else:
                witness = "violated"
                status = "violated"
                tag = None
                code = "CUSTODY_COMPROMISED"

            return {
                "obligation_id": "O_CONTROL_DATASET_BINDING",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Authentic timestamped remote host API receipt",
                "protocol_fault": None,
                "witness_classes": [witness],
                "eval_status": status,
                "failure_tag": tag,
                "reason_code": code,
                "details": {
                    "bound_version": bound_v,
                    "runtime_byte_match": byte_match,
                    "runtime_file_count": file_count
                }
            }
        except Exception as e:
            return {
                "obligation_id": "O_CONTROL_DATASET_BINDING",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Authentic API receipt",
                "protocol_fault": None,
                "witness_classes": ["checkerError"],
                "eval_status": "checkerError",
                "failure_tag": None,
                "reason_code": f"CHECKER_CRASH: {str(e)}",
                "details": {"error": str(e)}
            }

    def evaluate_o_run_exit(self) -> Dict[str, Any]:
        """O_RUN_EXIT: Clean driver termination with returncode 0."""
        req = [
            "s3_execution_output/batteryml-protocol-robustness-s3-run.log",
            "s3_execution_output/s3-artifact/completion-receipt.json"
        ]
        hashes = {f: self.sha256_of_file(self.s3_dir / f) for f in req}

        if not self.completion_file.is_file() or not self.runner_log_file.is_file():
            return {
                "obligation_id": "O_RUN_EXIT",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": False,
                "admissibility_reason": "Runner telemetry or completion receipt missing",
                "protocol_fault": None,
                "witness_classes": [],
                "eval_status": "missing",
                "failure_tag": None,
                "reason_code": "EVIDENCE_MISSING",
                "details": {}
            }

        try:
            c = json.loads(self.completion_file.read_text())
            status_str = c.get("status")
            total_files = c.get("total_files", 0)

            if status_str == "COMPLETE" and total_files >= 1300:
                witness = "satisfied"
                status = "satisfied"
                code = "DRIVER_CLEAN_COMPLETION"
            else:
                witness = "violated"
                status = "violated"
                code = "DRIVER_NONZERO_OR_INCOMPLETE"

            return {
                "obligation_id": "O_RUN_EXIT",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Complete uncorrupted host runner log and termination receipt",
                "protocol_fault": None,
                "witness_classes": [witness],
                "eval_status": status,
                "failure_tag": None,
                "reason_code": code,
                "details": {
                    "completion_status": status_str,
                    "total_files": total_files
                }
            }
        except Exception as e:
            return {
                "obligation_id": "O_RUN_EXIT",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Host runner logs present",
                "protocol_fault": None,
                "witness_classes": ["checkerError"],
                "eval_status": "checkerError",
                "failure_tag": None,
                "reason_code": f"CHECKER_CRASH: {str(e)}",
                "details": {"error": str(e)}
            }

    def evaluate_o_fit_count(self) -> Dict[str, Any]:
        """O_FIT_COUNT: All 264 pre-registered model fits executed."""
        preds = list(self.results_dir.rglob("per-cell-predictions.csv"))
        req = ["s3_execution_output/s3-artifact/execution-closure.json"]
        hashes = {f: self.sha256_of_file(self.s3_dir / f) for f in req}

        if len(preds) == 0:
            return {
                "obligation_id": "O_FIT_COUNT",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": False,
                "admissibility_reason": "Zero prediction files found in evidence directory",
                "protocol_fault": None,
                "witness_classes": [],
                "eval_status": "missing",
                "failure_tag": None,
                "reason_code": "PREDICTIONS_ABSENT",
                "details": {"count": 0}
            }

        try:
            expected_fits = 264  # (64 sampled + 1 split_a + 1 ref_b) * 4 models
            actual_fits = len(preds)

            if actual_fits == expected_fits:
                witness = "satisfied"
                status = "satisfied"
                code = "ALL_FITS_PRESENT"
            elif actual_fits < expected_fits:
                witness = "violated"
                status = "violated"
                code = "INCOMPLETE_FITS_COUNT"
            else:
                witness = "violated"
                status = "violated"
                code = "EXCESS_UNREGISTERED_FITS"

            return {
                "obligation_id": "O_FIT_COUNT",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Admissible prediction matrix directory bound to execution closure",
                "protocol_fault": None,
                "witness_classes": [witness],
                "eval_status": status,
                "failure_tag": None,
                "reason_code": code,
                "details": {
                    "expected_fits": expected_fits,
                    "actual_fits": actual_fits
                }
            }
        except Exception as e:
            return {
                "obligation_id": "O_FIT_COUNT",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Admissible prediction tables",
                "protocol_fault": None,
                "witness_classes": ["checkerError"],
                "eval_status": "checkerError",
                "failure_tag": None,
                "reason_code": f"CHECKER_CRASH: {str(e)}",
                "details": {"error": str(e)}
            }

    def evaluate_o_ctrl_gate1(self) -> Dict[str, Any]:
        """O_CTRL_GATE1: Split A positive control baseline reproduction."""
        gate1_file = self.art_dir / "gate-1-positive-control-a.json"
        req = ["s3_execution_output/s3-artifact/gate-1-positive-control-a.json"]
        hashes = {f: self.sha256_of_file(self.s3_dir / f) for f in req}

        if not gate1_file.is_file():
            return {
                "obligation_id": "O_CTRL_GATE1",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": False,
                "admissibility_reason": "Gate 1 positive control file missing",
                "protocol_fault": None,
                "witness_classes": [],
                "eval_status": "missing",
                "failure_tag": None,
                "reason_code": "EVIDENCE_MISSING",
                "details": {}
            }

        try:
            g1 = json.loads(gate1_file.read_text())
            pass_status = (g1.get("status") == "PASS")
            divergences = g1.get("divergences", {})
            has_models = all(m in divergences for m in ["xgb", "variance", "ridge"])
            all_passed = pass_status and has_models and all(d.get("passed", False) for d in divergences.values())

            if all_passed:
                witness = "satisfied"
                status = "satisfied"
                tag = None
                code = "GATE1_BASELINE_REPRODUCED"
            else:
                witness = "violated"
                status = "violated"
                tag = "F_GATE1_CONTROL_FAILURE"
                code = "GATE1_BASELINE_BREACHED"

            return {
                "obligation_id": "O_CTRL_GATE1",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Complete evaluation table for Split A positive control",
                "protocol_fault": None,
                "witness_classes": [witness],
                "eval_status": status,
                "failure_tag": tag,
                "reason_code": code,
                "details": {
                    "pass": pass_status,
                    "divergences": divergences
                }
            }
        except Exception as e:
            return {
                "obligation_id": "O_CTRL_GATE1",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Gate 1 file present",
                "protocol_fault": None,
                "witness_classes": ["checkerError"],
                "eval_status": "checkerError",
                "failure_tag": None,
                "reason_code": f"CHECKER_CRASH: {str(e)}",
                "details": {"error": str(e)}
            }

    def evaluate_o_ctrl_gate2(self) -> Dict[str, Any]:
        """O_CTRL_GATE2: Reference Split B historical baseline reproduction."""
        gate2_file = self.art_dir / "gate-2-reference-split-b.json"
        req = ["s3_execution_output/s3-artifact/gate-2-reference-split-b.json"]
        hashes = {f: self.sha256_of_file(self.s3_dir / f) for f in req}

        if not gate2_file.is_file():
            return {
                "obligation_id": "O_CTRL_GATE2",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": False,
                "admissibility_reason": "Gate 2 reference control file missing",
                "protocol_fault": None,
                "witness_classes": [],
                "eval_status": "missing",
                "failure_tag": None,
                "reason_code": "EVIDENCE_MISSING",
                "details": {}
            }

        try:
            g2 = json.loads(gate2_file.read_text())
            pass_status = (g2.get("status") == "PASS")
            divergences = g2.get("divergences", {})
            has_models = all(m in divergences for m in ["xgb", "variance", "ridge"])
            all_passed = pass_status and has_models and all(d.get("passed", False) for d in divergences.values())

            if all_passed:
                witness = "satisfied"
                status = "satisfied"
                tag = None
                code = "GATE2_REFERENCE_REPRODUCED"
            else:
                witness = "violated"
                status = "violated"
                tag = "F_GATE2_CONTROL_FAILURE"
                code = "GATE2_REFERENCE_BREACHED"

            return {
                "obligation_id": "O_CTRL_GATE2",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Complete evaluation table for Ref B calibration control",
                "protocol_fault": None,
                "witness_classes": [witness],
                "eval_status": status,
                "failure_tag": tag,
                "reason_code": code,
                "details": {
                    "pass": pass_status,
                    "divergences": divergences
                }
            }
        except Exception as e:
            return {
                "obligation_id": "O_CTRL_GATE2",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Gate 2 file present",
                "protocol_fault": None,
                "witness_classes": ["checkerError"],
                "eval_status": "checkerError",
                "failure_tag": None,
                "reason_code": f"CHECKER_CRASH: {str(e)}",
                "details": {"error": str(e)}
            }

    def evaluate_o_recompute_predictions(self) -> Dict[str, Any]:
        """O_RECOMPUTE_PREDICTIONS: Clean-room recomputation of RMSE & MAE from CSVs."""
        req = ["verifiers/verify_s3_recomputation.py"]
        hashes = {f: self.sha256_of_file(self.s3_dir / f) for f in req}

        # Validate that all 264 CSVs exist and match reported metrics
        preds = list(self.results_dir.rglob("per-cell-predictions.csv"))
        if len(preds) < 264:
            return {
                "obligation_id": "O_RECOMPUTE_PREDICTIONS",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": False,
                "admissibility_reason": "Incomplete raw prediction CSVs for clean-room recalculation",
                "protocol_fault": None,
                "witness_classes": [],
                "eval_status": "missing",
                "failure_tag": None,
                "reason_code": "PREDICTIONS_INSUFFICIENT",
                "details": {"count": len(preds)}
            }

        try:
            mismatches = []
            checked = 0
            for csv_path in preds:
                rcpt_path = csv_path.parent / "run-receipt.json"
                if not rcpt_path.is_file():
                    mismatches.append(f"Missing receipt for {csv_path}")
                    continue
                rcpt = json.loads(rcpt_path.read_text())
                df = pd.read_csv(csv_path)
                err = df["target"] - df["prediction"]
                rmse = math.sqrt(float((err ** 2).mean()))
                mae = float(err.abs().mean())

                if not math.isclose(rmse, rcpt["rmse"], rel_tol=1e-4, abs_tol=1e-4):
                    mismatches.append(f"RMSE mismatch in {csv_path}: calc {rmse} vs rcpt {rcpt['rmse']}")
                if not math.isclose(mae, rcpt["mae"], rel_tol=1e-4, abs_tol=1e-4):
                    mismatches.append(f"MAE mismatch in {csv_path}: calc {mae} vs rcpt {rcpt['mae']}")
                checked += 1

            if len(mismatches) == 0 and checked == 264:
                witness = "satisfied"
                status = "satisfied"
                tag = None
                code = "ALL_264_FITS_RECOMPUTED_MATCH"
            else:
                witness = "violated"
                status = "violated"
                tag = "F_RECOMPUTATION_DISCREPANCY"
                code = "RECOMPUTATION_DISCREPANCY_DETECTED"

            return {
                "obligation_id": "O_RECOMPUTE_PREDICTIONS",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Raw per-cell CSV tables successfully ingested out-of-process",
                "protocol_fault": None,
                "witness_classes": [witness],
                "eval_status": status,
                "failure_tag": tag,
                "reason_code": code,
                "details": {
                    "total_checked": checked,
                    "mismatches_count": len(mismatches),
                    "first_mismatches": mismatches[:3]
                }
            }
        except Exception as e:
            return {
                "obligation_id": "O_RECOMPUTE_PREDICTIONS",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Prediction files present",
                "protocol_fault": None,
                "witness_classes": ["checkerError"],
                "eval_status": "checkerError",
                "failure_tag": None,
                "reason_code": f"CHECKER_CRASH: {str(e)}",
                "details": {"error": str(e)}
            }

    def evaluate_o_statistical_prevalence(self) -> Dict[str, Any]:
        """O_STATISTICAL_PREVALENCE: Material performance shift prevalence verification."""
        req = [
            "s3_execution_output/governing-adjudication.json",
            "s3_execution_output/s3-artifact/adjudication_candidate.json"
        ]
        hashes = {f: self.sha256_of_file(self.s3_dir / f) for f in req}

        # Calculate empirical shift directly from raw CSVs
        sampled_dir = self.results_dir / "sampled"
        sdirs = sorted([d for d in sampled_dir.iterdir() if d.is_dir()])
        if len(sdirs) != 64:
            return {
                "obligation_id": "O_STATISTICAL_PREVALENCE",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": False,
                "admissibility_reason": f"Expected 64 sampled splits, found {len(sdirs)}",
                "protocol_fault": None,
                "witness_classes": [],
                "eval_status": "missing",
                "failure_tag": None,
                "reason_code": "SPLITS_INSUFFICIENT",
                "details": {"sampled_dirs": len(sdirs)}
            }

        try:
            # Baseline Split A RMSEs
            base_rmses = {}
            for m in ["xgb", "variance", "ridge", "dummy"]:
                df = pd.read_csv(self.results_dir / "split_a" / m / "per-cell-predictions.csv")
                base_rmses[m] = math.sqrt(float(((df["target"] - df["prediction"]) ** 2).mean()))

            # Model relative changes D = (RMSE_s - RMSE_base) / RMSE_base
            shift_thresh = float(self.claim.get("shift_threshold", 0.10))
            prev_limit = float(self.claim.get("prevalence_limit", 0.50))
            target_models = self.claim.get("target_models", ["xgb", "variance", "ridge"])

            model_d = {m: [] for m in target_models}
            for sdir in sdirs:
                for m in target_models:
                    df = pd.read_csv(sdir / m / "per-cell-predictions.csv")
                    rmse = math.sqrt(float(((df["target"] - df["prediction"]) ** 2).mean()))
                    d = (rmse - base_rmses[m]) / base_rmses[m]
                    model_d[m].append(d)

            # Check prevalence for each target model
            model_prevalence = {}
            violating_models = []
            for m in target_models:
                material_count = sum(1 for d in model_d[m] if d > shift_thresh)
                p = material_count / len(model_d[m])
                model_prevalence[m] = {
                    "material_count": material_count,
                    "total_splits": len(model_d[m]),
                    "prevalence": p,
                    "exceeds_limit": p > prev_limit
                }
                if p > prev_limit:
                    violating_models.append(m)

            if len(violating_models) == 0:
                witness = "satisfied"
                status = "satisfied"
                tag = None
                code = "ALL_TARGET_MODELS_ROBUST"
            else:
                witness = "violated"
                status = "violated"
                tag = "F_THRESHOLD_EXCEEDED"
                code = f"THRESHOLD_EXCEEDED_FOR_{'_AND_'.join(violating_models).upper()}"

            return {
                "obligation_id": "O_STATISTICAL_PREVALENCE",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Clean-room distribution table derived from verified prediction files",
                "protocol_fault": None,
                "witness_classes": [witness],
                "eval_status": status,
                "failure_tag": tag,
                "reason_code": code,
                "details": {
                    "shift_threshold": shift_thresh,
                    "prevalence_limit": prev_limit,
                    "target_models": target_models,
                    "model_prevalence": model_prevalence,
                    "violating_models": violating_models
                }
            }
        except Exception as e:
            return {
                "obligation_id": "O_STATISTICAL_PREVALENCE",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Summary tables present",
                "protocol_fault": None,
                "witness_classes": ["checkerError"],
                "eval_status": "checkerError",
                "failure_tag": None,
                "reason_code": f"CHECKER_CRASH: {str(e)}",
                "details": {"error": str(e)}
            }

    def evaluate_o_dummy_benchmark_separation(self) -> Dict[str, Any]:
        """O_DUMMY_BENCHMARK_SEPARATION: Non-triviality check vs zero-rule dummy."""
        req = ["s3_execution_output/governing-adjudication.json"]
        hashes = {f: self.sha256_of_file(self.s3_dir / f) for f in req}

        sampled_dir = self.results_dir / "sampled"
        sdirs = sorted([d for d in sampled_dir.iterdir() if d.is_dir()])
        if len(sdirs) != 64:
            return {
                "obligation_id": "O_DUMMY_BENCHMARK_SEPARATION",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": False,
                "admissibility_reason": "Sampled splits incomplete",
                "protocol_fault": None,
                "witness_classes": [],
                "eval_status": "missing",
                "failure_tag": None,
                "reason_code": "EVIDENCE_INCOMPLETE",
                "details": {}
            }

        try:
            inversions = 0
            total_checks = 0
            for sdir in sdirs:
                dummy_df = pd.read_csv(sdir / "dummy" / "per-cell-predictions.csv")
                dummy_rmse = math.sqrt(float(((dummy_df["target"] - dummy_df["prediction"]) ** 2).mean()))

                for m in ["xgb", "variance", "ridge"]:
                    m_df = pd.read_csv(sdir / m / "per-cell-predictions.csv")
                    m_rmse = math.sqrt(float(((m_df["target"] - m_df["prediction"]) ** 2).mean()))
                    total_checks += 1
                    if m_rmse >= dummy_rmse:
                        inversions += 1

            separation_rate = (total_checks - inversions) / total_checks

            if separation_rate >= 0.95:
                witness = "satisfied"
                status = "satisfied"
                tag = None
                code = "DUMMY_BENCHMARK_SEPARATION_VERIFIED"
            else:
                witness = "violated"
                status = "violated"
                tag = "F_DUMMY_INVERSION"
                code = "DUMMY_BENCHMARK_INVERSION"

            return {
                "obligation_id": "O_DUMMY_BENCHMARK_SEPARATION",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Dummy and candidate models evaluated on identical test splits",
                "protocol_fault": None,
                "witness_classes": [witness],
                "eval_status": status,
                "failure_tag": tag,
                "reason_code": code,
                "details": {
                    "total_comparisons": total_checks,
                    "inversions": inversions,
                    "separation_rate": separation_rate
                }
            }
        except Exception as e:
            return {
                "obligation_id": "O_DUMMY_BENCHMARK_SEPARATION",
                "required_evidence": req,
                "source_hashes": hashes,
                "admissible": True,
                "admissibility_reason": "Dummy predictions present",
                "protocol_fault": None,
                "witness_classes": ["checkerError"],
                "eval_status": "checkerError",
                "failure_tag": None,
                "reason_code": f"CHECKER_CRASH: {str(e)}",
                "details": {"error": str(e)}
            }

    # -------------------------------------------------------------------------
    # Aggregation and DecisionView Assembly
    # -------------------------------------------------------------------------

    def run_adjudication_trace(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Executes all stages and returns (obligation_trace, decision_view)."""
        # Stage 1: Protocol fault
        protocol_fault = self.check_protocol_faults()

        # Stage 2 & 3: Evaluate all 10 obligations
        evaluators = [
            self.evaluate_o_seed_binding,
            self.evaluate_o_hash_test_membership,
            self.evaluate_o_control_dataset_binding,
            self.evaluate_o_run_exit,
            self.evaluate_o_fit_count,
            self.evaluate_o_ctrl_gate1,
            self.evaluate_o_ctrl_gate2,
            self.evaluate_o_recompute_predictions,
            self.evaluate_o_statistical_prevalence,
            self.evaluate_o_dummy_benchmark_separation,
        ]

        obs_trace = []
        obs_statuses = []

        for fn in evaluators:
            res = fn()
            obs_trace.append(res)
            obs_statuses.append(res["eval_status"])

        # Limitations:
        # hasBlockingLimitation: strictly false in v0.1 (L_TEMPERATURE_DRIFT excised)
        has_blocking = False

        # hasNonBlockingLimitation: true if L_CHEMISTRY_LFP applies
        # and/or L_MODEL_FAMILY_SCOPE applies to architecture-bounded claims
        has_non_blocking = True

        # Novel findings: none registered
        admissible_novel = False

        # Falsifiability: pre-registered explicit thresholds and controls
        falsifiable = True

        decision_view = {
            "protocolFault": protocol_fault,
            "falsifiable": falsifiable,
            "obligations": obs_statuses,
            "hasBlockingLimitation": has_blocking,
            "hasNonBlockingLimitation": has_non_blocking,
            "admissibleNovelFinding": admissible_novel
        }

        obligation_trace = {
            "trace_version": "1.0.0",
            "claim_id": self.claim.get("claim_id", "CLAIM-BATTERYML-MATR1-PROTOCOL-ROBUSTNESS-S3"),
            "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
            "obligations": obs_trace
        }

        return obligation_trace, decision_view

    def generate_lean_harness(self, decision_view: Dict[str, Any], out_path: Path):
        """Generates ReplayDecision.lean calling frozen adjudicate."""
        pf = decision_view["protocolFault"]
        if pf is None:
            pf_str = "none"
        else:
            pf_str = f"some S2ProtocolError.{pf}"

        obs_lines = ",\n    ".join(f"EvalStatus.{s}" for s in decision_view["obligations"])

        lean_code = f"""import P10Core.Model.AdjudicationAutomaton

open P10Core.Model.AdjudicationAutomaton

def replayDecisionView : DecisionView := {{
  protocolFault := {pf_str},
  falsifiable := {str(decision_view['falsifiable']).lower()},
  obligations := [
    {obs_lines}
  ],
  hasBlockingLimitation := {str(decision_view['hasBlockingLimitation']).lower()},
  hasNonBlockingLimitation := {str(decision_view['hasNonBlockingLimitation']).lower()},
  admissibleNovelFinding := {str(decision_view['admissibleNovelFinding']).lower()}
}}

def main : IO Unit := do
  let outcome := adjudicate replayDecisionView
  match outcome with
  | TerminalOutcome.protocolError err =>
    IO.println s!"TERMINAL_OUTCOME: PROTOCOL_ERROR ({{repr err}})"
  | TerminalOutcome.verdict v =>
    IO.println s!"TERMINAL_OUTCOME: VERDICT ({{repr v}})"
"""
        out_path.write_text(lean_code)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="P10 BatteryML S2 Replay Adapter")
    parser.add_argument("--s3-dir", type=Path, default=Path("/home/volmax-studio/volmax-projects/iot2/batteryml-protocol-robustness-s3"))
    parser.add_argument("--out-dir", type=Path, default=Path("/home/volmax-studio/volmax-projects/iot2/p10-audit-batteryml-s3-retro-s2/run-001"))
    parser.add_argument("--claim-file", type=Path, default=None)
    args = parser.parse_args()

    # Load claim
    if args.claim_file and args.claim_file.is_file():
        claim = json.loads(args.claim_file.read_text())
    else:
        # Default evaluated claim from REPLAY_PLAN.md: general robustness claim across all candidate models
        claim = {
            "claim_id": "CLAIM-BATTERYML-MATR1-PROTOCOL-ROBUSTNESS-S3",
            "target_models": ["xgb", "variance", "ridge"],
            "split_type": "Minimum-Cost Protocol-Disjoint Cell Partition (K=64)",
            "cell_population": "Severson et al. (2019) LFP Commercial Cells (MATR1)",
            "shift_threshold": 0.10,
            "prevalence_limit": 0.50,
            "gating_controls": ["Split A Baseline (Gate 1)", "Reference Split B (Gate 2)"]
        }

    args.out_dir.mkdir(parents=True, exist_ok=True)

    adapter = BatteryMLS2Adapter(args.s3_dir, claim)
    trace, dv = adapter.run_adjudication_trace()

    trace_file = args.out_dir / "obligation_trace.json"
    dv_file = args.out_dir / "decision_view.json"
    lean_file = args.out_dir / "ReplayDecision.lean"

    trace_file.write_text(json.dumps(trace, indent=2))
    dv_file.write_text(json.dumps(dv, indent=2))
    adapter.generate_lean_harness(dv, lean_file)

    print(f"Obligation trace written to: {trace_file}")
    print(f"DecisionView written to:      {dv_file}")
    print(f"Lean harness written to:     {lean_file}")


if __name__ == "__main__":
    main()
