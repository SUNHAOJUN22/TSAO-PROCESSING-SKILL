"""Rejected transitions must never leave a mutable gate in the requested state."""

from __future__ import annotations

import copy
from dataclasses import asdict

import pytest

from tsao.gates import ApprovalStatus, GateRecord, GateStatus

TRANSITIONS = (
    (GateStatus.NOT_EVALUATED, GateStatus.PASS),
    (GateStatus.HOLD, GateStatus.PASS),
    (GateStatus.CONDITIONAL, GateStatus.RETIRED),
    (GateStatus.PASS, GateStatus.FAIL),
)


def approved_record(status: GateStatus) -> GateRecord:
    return GateRecord(
        "G0",
        status=status,
        owner="synthetic owner",
        evidence_ids=["synthetic evidence"],
        approval_status=ApprovalStatus.APPROVED,
        approver="synthetic reviewer",
    )


@pytest.mark.parametrize(("old_status", "new_status"), TRANSITIONS)
@pytest.mark.parametrize("invalid_evidence", [[{}], [["nested evidence"]]])
def test_malformed_evidence_cannot_commit_a_rejected_state(
    old_status: GateStatus, new_status: GateStatus, invalid_evidence: list
) -> None:
    record = approved_record(old_status)
    record.evidence_ids = copy.deepcopy(invalid_evidence)
    before = copy.deepcopy(asdict(record))
    with pytest.raises(TypeError):
        record.transition(new_status)
    assert asdict(record) == before


@pytest.mark.parametrize(("old_status", "new_status"), TRANSITIONS)
def test_validation_exception_preserves_the_entire_original_record(
    old_status: GateStatus, new_status: GateStatus, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = approved_record(old_status)
    before = copy.deepcopy(asdict(record))

    def unavailable_validation(_record: GateRecord) -> list[str]:
        raise RuntimeError("synthetic validation failure")

    monkeypatch.setattr(GateRecord, "validate", unavailable_validation)
    with pytest.raises(RuntimeError, match="synthetic validation failure"):
        record.transition(new_status)
    assert asdict(record) == before


@pytest.mark.parametrize(("old_status", "new_status"), TRANSITIONS)
def test_validated_transition_updates_only_the_status(
    old_status: GateStatus, new_status: GateStatus
) -> None:
    record = approved_record(old_status)
    expected = asdict(record)
    expected["status"] = new_status
    evidence = record.evidence_ids
    record.transition(new_status)
    assert asdict(record) == expected
    assert record.evidence_ids is evidence


def test_reported_validation_issues_preserve_the_original_state() -> None:
    record = GateRecord("G0", status=GateStatus.HOLD)
    before = asdict(record)
    with pytest.raises(ValueError, match="invalid target Gate state"):
        record.transition(GateStatus.PASS)
    assert asdict(record) == before
