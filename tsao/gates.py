from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from enum import StrEnum

from ._utils import nonempty


class GateStatus(StrEnum):
    NOT_EVALUATED = "NOT_EVALUATED"
    HOLD = "HOLD"
    CONDITIONAL = "CONDITIONAL"
    PASS = "PASS"
    FAIL = "FAIL"
    RETIRED = "RETIRED"


class ApprovalStatus(StrEnum):
    NOT_EVALUATED = "NOT_EVALUATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


ALLOWED_TRANSITIONS: dict[GateStatus, set[GateStatus]] = {
    GateStatus.NOT_EVALUATED: {
        GateStatus.HOLD,
        GateStatus.CONDITIONAL,
        GateStatus.PASS,
        GateStatus.FAIL,
        GateStatus.RETIRED,
    },
    GateStatus.HOLD: {
        GateStatus.CONDITIONAL,
        GateStatus.PASS,
        GateStatus.FAIL,
        GateStatus.RETIRED,
    },
    GateStatus.CONDITIONAL: {
        GateStatus.HOLD,
        GateStatus.PASS,
        GateStatus.FAIL,
        GateStatus.RETIRED,
    },
    GateStatus.PASS: {GateStatus.HOLD, GateStatus.FAIL, GateStatus.RETIRED},
    GateStatus.FAIL: {GateStatus.HOLD, GateStatus.RETIRED},
    GateStatus.RETIRED: set(),
}

_GATE_ID_RE = re.compile(r"^G(?:[0-9]|1[0-8])$")


@dataclass(slots=True)
class GateRecord:
    gate_id: str
    status: GateStatus = GateStatus.NOT_EVALUATED
    owner: str | None = None
    evidence_ids: list[str] = field(default_factory=list)
    approval_status: ApprovalStatus = ApprovalStatus.NOT_EVALUATED
    approver: str | None = None

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not _GATE_ID_RE.fullmatch(self.gate_id):
            issues.append("invalid gate id")
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            issues.append("duplicate evidence ids")
        if any(not isinstance(item, str) or not item.strip() for item in self.evidence_ids):
            issues.append("evidence ids must be non-empty strings")
        if self.status == GateStatus.PASS:
            if not nonempty(self.owner):
                issues.append("PASS requires owner")
            if not self.evidence_ids:
                issues.append("PASS requires evidence")
            if self.approval_status != ApprovalStatus.APPROVED:
                issues.append("PASS requires approval")
            if not nonempty(self.approver):
                issues.append("PASS requires named approver")
        if self.status == GateStatus.RETIRED:
            if not nonempty(self.owner):
                issues.append("RETIRED requires owner")
            if self.approval_status != ApprovalStatus.APPROVED:
                issues.append("RETIRED requires approval")
            if not nonempty(self.approver):
                issues.append("RETIRED requires named approver")
        return issues

    def transition(self, new_status: GateStatus) -> None:
        if new_status not in ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(f"illegal transition {self.status}->{new_status}")
        old_status = self.status
        self.status = new_status
        issues = self.validate()
        if issues:
            self.status = old_status
            raise ValueError("invalid target Gate state: " + "; ".join(issues))


def validate_gate_sequence(gates: list[GateRecord]) -> list[str]:
    issues: list[str] = []
    ids = [gate.gate_id for gate in gates]
    counts = Counter(ids)
    duplicate_ids = sorted(gate_id for gate_id, count in counts.items() if count > 1)
    if len(gates) != 19 or set(ids) != {f"G{i}" for i in range(19)} or duplicate_ids:
        issues.append("gate set must contain each of G0-G18 exactly once")
    if duplicate_ids:
        issues.append("duplicate gate ids: " + ", ".join(duplicate_ids))
    by_id = {gate.gate_id: gate for gate in gates}
    for gate in gates:
        issues.extend(f"{gate.gate_id}: {issue}" for issue in gate.validate())
    for index in range(1, 19):
        current = by_id.get(f"G{index}")
        if current is None or current.status != GateStatus.PASS:
            continue
        blocking = [
            f"G{prior}"
            for prior in range(index)
            if by_id.get(f"G{prior}") is None
            or by_id[f"G{prior}"].status not in {GateStatus.PASS, GateStatus.RETIRED}
        ]
        if blocking:
            issues.append(f"G{index} cannot PASS before " + ", ".join(blocking))
    return issues
