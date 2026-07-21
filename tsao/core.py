from __future__ import annotations

import hashlib
import json
import re
import shutil
import zipfile
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from pathlib import Path

import numpy as np
import yaml


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


ALLOWED_TRANSITIONS = {
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
        try:
            number = int(self.gate_id[1:]) if self.gate_id.startswith("G") else -1
        except ValueError:
            number = -1
        if not 0 <= number <= 18:
            issues.append("invalid gate id")
        if self.status == GateStatus.PASS:
            if not self.owner:
                issues.append("PASS requires owner")
            if not self.evidence_ids:
                issues.append("PASS requires evidence")
            if self.approval_status != ApprovalStatus.APPROVED:
                issues.append("PASS requires approval")
            if not self.approver:
                issues.append("PASS requires named approver")
        return issues

    def transition(self, new_status: GateStatus) -> None:
        if new_status not in ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(f"illegal transition {self.status}->{new_status}")
        self.status = new_status


@dataclass(slots=True)
class EvidenceItem:
    evidence_id: str
    grade: str
    decision_eligible: bool
    applicability: str
    review_due_on: str | None = None
    contradiction_status: str = "NONE"

    def usable(self, as_of: date | None = None) -> bool:
        as_of = as_of or date.today()
        expired = bool(
            self.review_due_on and date.fromisoformat(self.review_due_on) < as_of
        )
        return (
            self.grade in {"A", "B"}
            and self.decision_eligible
            and bool(self.applicability)
            and self.contradiction_status != "OPEN"
            and not expired
        )


@dataclass(slots=True)
class ModelRecord:
    model_id: str
    risk_class: str
    status: str = "PLANNED"
    identifiability: str = "NOT_EVALUATED"
    independent_reviewer: str | None = None

    def qualified(self) -> bool:
        if self.status != "QUALIFIED" or self.identifiability not in {
            "PASS",
            "CONDITIONAL",
        }:
            return False
        return self.risk_class not in {"MR4", "MR5"} or bool(
            self.independent_reviewer
        )


class AssuranceGraph:
    def __init__(self) -> None:
        self.nodes: dict[str, dict] = {}
        self.out: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
        self.inc: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)

    def add_node(self, node_id: str, node_type: str, **attrs) -> None:
        if node_id in self.nodes:
            raise ValueError("duplicate node")
        self.nodes[node_id] = {"type": node_type, **attrs}

    def add_edge(self, source: str, target: str, relation: str) -> None:
        if source not in self.nodes or target not in self.nodes:
            raise KeyError("edge endpoint missing")
        self.out[source].append((target, relation))
        self.inc[target].append((source, relation))

    def has_path(
        self, source: str, target: str, relations: set[str] | None = None
    ) -> bool:
        queue = deque([source])
        seen = {source}
        while queue:
            node = queue.popleft()
            if node == target:
                return True
            for nxt, relation in self.out[node]:
                if relations and relation not in relations:
                    continue
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        return False

    def orphans(self) -> list[str]:
        return sorted(n for n in self.nodes if not self.out[n] and not self.inc[n])


ROUTES = {
    "epdm": {
        "epdm",
        "epr",
        "ethylene propylene diene",
        "乙丙橡胶",
        "三元乙丙",
        "enb",
        "dcpd",
        "vnb",
    },
    "poe": {
        "poe",
        "polyolefin elastomer",
        "聚烯烃弹性体",
        "乙烯辛烯",
        "solution polyolefin elastomer",
    },
    "polymer-general": {
        "polymer",
        "polymerization",
        "聚合",
        "树脂",
        "橡胶",
        "分子量",
        "催化剂",
    },
    "bioprocess": {"fermentation", "bioreactor", "发酵", "enzyme", "cell culture"},
    "electrochemical": {
        "electrolysis",
        "battery",
        "fuel cell",
        "电化学",
        "电解",
        "电池",
    },
    "solids": {"crystallization", "precipitation", "powder", "结晶", "沉淀", "粉体"},
    "fine-chemical-batch": {
        "batch",
        "fine chemical",
        "pharmaceutical",
        "批式",
        "精细化工",
        "医药",
    },
    "petrochemical": {
        "refinery",
        "petrochemical",
        "olefin",
        "石化",
        "炼化",
        "裂解",
    },
}


def route(text: str) -> list[tuple[str, float]]:
    normalized = re.sub(r"\s+", " ", text.lower())
    scores = []
    for name, terms in ROUTES.items():
        hits = sum(1 for term in terms if term in normalized)
        scores.append((name, hits / max(1, len(terms))))
    selected = sorted((x for x in scores if x[1] > 0), key=lambda x: (-x[1], x[0]))
    return selected or [("generic-process", 0.0)]


def validate_gate_sequence(gates: list[GateRecord]) -> list[str]:
    issues: list[str] = []
    by_id = {g.gate_id: g for g in gates}
    if set(by_id) != {f"G{i}" for i in range(19)}:
        issues.append("gate set must be exactly G0-G18")
    for gate in gates:
        issues.extend(f"{gate.gate_id}: {issue}" for issue in gate.validate())
    for i in range(1, 19):
        current = by_id.get(f"G{i}")
        previous = by_id.get(f"G{i-1}")
        if (
            current
            and previous
            and current.status == GateStatus.PASS
            and previous.status not in {GateStatus.PASS, GateStatus.RETIRED}
        ):
            issues.append(f"G{i} cannot PASS before G{i-1}")
    return issues


def balance_residual(
    inputs: dict[str, float],
    outputs: dict[str, float],
    generation: dict[str, float] | None = None,
) -> dict[str, float]:
    generation = generation or {}
    keys = set(inputs) | set(outputs) | set(generation)
    return {
        key: float(
            inputs.get(key, 0) + generation.get(key, 0) - outputs.get(key, 0)
        )
        for key in sorted(keys)
    }


def closure_fraction(inputs: dict[str, float], outputs: dict[str, float]) -> float:
    total_in = sum(inputs.values())
    if total_in <= 0:
        raise ValueError("input total must be positive")
    return 1 - abs(total_in - sum(outputs.values())) / total_in


def stoichiometric_rank(matrix: list[list[float]]) -> int:
    values = np.asarray(matrix, dtype=float)
    if values.ndim != 2 or values.size == 0:
        raise ValueError("non-empty 2D matrix required")
    return int(np.linalg.matrix_rank(values))


PROJECT_DIRS = [
    "00_governance",
    "01_evidence",
    "02_requirements",
    "03_measurement_data",
    "04_chemistry",
    "05_models",
    "06_lab",
    "07_bench",
    "08_separation_recycle",
    "09_pilot",
    "10_demonstration",
    "11_industrial",
    "12_control",
    "13_hse_reliability",
    "14_tea_lca_ip",
    "15_qualification",
    "16_technology_package",
    "17_transfer",
    "18_field_learning",
    "data/raw",
    "data/processed",
    "models",
    "reports",
    "logs",
]


def bootstrap_project(
    brief: Path, output: Path, template_root: Path | None = None
) -> dict:
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("output directory is not empty")
    text = brief.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    output.mkdir(parents=True, exist_ok=True)
    for directory in PROJECT_DIRS:
        (output / directory).mkdir(parents=True, exist_ok=True)
    if template_root and template_root.exists():
        for path in template_root.iterdir():
            if path.is_file():
                shutil.copy2(path, output / "00_governance" / path.name)
    routed = route(text)
    manifest = {
        "project_id": data.get("project_id", "TSAO-PROJECT"),
        "title": data.get("title", "Untitled process project"),
        "version": "0.1.0",
        "domain": [x[0] for x in routed],
        "subskills": [
            x[0]
            for x in routed
            if x[0] in {"epdm", "poe", "polymer-general"}
        ],
        "technical_approval_status": "NOT_EVALUATED",
        "gates": [
            {
                "gate_id": f"G{i}",
                "status": "NOT_EVALUATED",
                "owner": None,
                "evidence_ids": [],
                "approval_status": "NOT_EVALUATED",
                "approver": None,
            }
            for i in range(19)
        ],
    }
    (output / "project_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output / "brief.yaml").write_text(text, encoding="utf-8")
    return manifest


def audit_project(root: Path) -> list[str]:
    issues = [
        f"missing directory: {directory}"
        for directory in PROJECT_DIRS
        if not (root / directory).is_dir()
    ]
    manifest_path = root / "project_manifest.json"
    if not manifest_path.is_file():
        return issues + ["missing project_manifest.json"]
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return issues + [f"invalid project manifest: {exc}"]
    if data.get("technical_approval_status") != "NOT_EVALUATED":
        issues.append("project must not claim technical approval")
    if [g.get("gate_id") for g in data.get("gates", [])] != [
        f"G{i}" for i in range(19)
    ]:
        issues.append("gate sequence must be G0-G18")
    return issues


def deterministic_zip(root: Path, output: Path) -> str:
    forbidden = {"__pycache__", ".pytest_cache", ".ruff_cache", ".git"}
    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in forbidden for part in path.relative_to(root).parts)
        and path.suffix not in {".pyc", ".pyo"}
    )
    with zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in files:
            name = f"{root.name}/{path.relative_to(root).as_posix()}"
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    return hashlib.sha256(output.read_bytes()).hexdigest()
