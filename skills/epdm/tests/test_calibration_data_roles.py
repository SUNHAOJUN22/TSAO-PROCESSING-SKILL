"""Declared holdouts must remain independent in the actual calibration plan."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from skills.epdm.contracts import GateDecision, GateReasonCode
from skills.epdm.validation_v2 import validate_v2_project

PROJECT = Path(__file__).resolve().parents[1] / "fixtures/v2_phase_a1_reference_project.json"


def project():
    return json.loads(PROJECT.read_text(encoding="utf-8"))


@pytest.mark.parametrize("role", ["VALIDATION", "HOLDOUT"])
def test_reserved_evaluation_targets_cannot_enter_parameter_calibration(role):
    data = project()
    dataset = data["datasets"][1]
    dataset["role"] = role
    dataset["targets"][0]["use"] = role
    before = copy.deepcopy(data)
    report = validate_v2_project(data)
    assert report.decision == GateDecision.FAIL
    assert any(issue.reason_code == GateReasonCode.DATA_LEAKAGE for issue in report.errors)
    assert data == before


def independent_project():
    data = project()
    dataset = copy.deepcopy(data["datasets"][1])
    dataset.update(dataset_id="DS-HOLDOUT", role="HOLDOUT", experiment_ids=["EXP-HOLDOUT"])
    target = dataset["targets"][0]
    target.update(
        target_id="T-HOLDOUT",
        dataset_id="DS-HOLDOUT",
        observation_id="OBS-HOLDOUT",
        experiment_id="EXP-HOLDOUT",
        experiment_group_id="GROUP-HOLDOUT",
        use="HOLDOUT",
    )
    data["datasets"].append(dataset)
    stage = copy.deepcopy(data["calibration_plans"][0]["stages"][1])
    stage.update(
        stage_id="STAGE-HOLDOUT",
        stage_kind="INDEPENDENT_VALIDATION",
        target_ids=["T-HOLDOUT"],
        varied_parameter_ids=[],
        fixed_parameter_ids=["KP-E", "EA-E"],
    )
    data["calibration_plans"][0]["stages"].append(stage)
    return data


def test_separate_holdout_can_validate_a_frozen_parameter_set():
    report = validate_v2_project(independent_project())
    assert report.decision == GateDecision.PASS, report


def test_independent_validation_cannot_tune_parameters():
    data = independent_project()
    stage = data["calibration_plans"][0]["stages"][-1]
    stage.update(varied_parameter_ids=["KP-E"], fixed_parameter_ids=["EA-E"])
    report = validate_v2_project(data)
    assert report.decision == GateDecision.FAIL
    assert any("independent validation" in issue.message for issue in report.errors)


def test_calibration_target_cannot_be_reused_as_independent_validation():
    data = independent_project()
    data["calibration_plans"][0]["stages"][-1]["target_ids"].append("T-COMP-E")
    report = validate_v2_project(data)
    assert report.decision == GateDecision.FAIL
    assert any(issue.reason_code == GateReasonCode.DATA_LEAKAGE for issue in report.errors)


def test_experiment_group_leakage_still_blocks_distinct_target_ids():
    data = independent_project()
    data["datasets"][-1]["targets"][0]["experiment_group_id"] = data["datasets"][1]["targets"][0][
        "experiment_group_id"
    ]
    report = validate_v2_project(data)
    assert report.decision == GateDecision.FAIL
    assert any(issue.reason_code == GateReasonCode.DATA_LEAKAGE for issue in report.errors)
