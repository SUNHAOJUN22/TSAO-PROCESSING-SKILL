from __future__ import annotations

from pathlib import Path
from typing import Any

GATES = tuple(f"G{index}" for index in range(19))
MATURITY_LEVELS = (
    "M0 idea", "M1 evidence-framed", "M2 chemistry-proven",
    "M3 laboratory-process-proven", "M4 bench-integrated", "M5 pilot-ready",
    "M6 pilot-proven", "M7 demo-proven", "M8 industrial-ready",
    "M9 operationally-validated",
)
WORKSTREAMS = (
    ("governance", "Governance and decision rights", "Research Director"),
    ("evidence-ip", "Evidence, standards, patents and research graph", "Evidence Lead"),
    ("product-quality", "Product, application, CQA and customer needs", "Product Lead"),
    ("chemistry", "Raw materials, catalysts, impurities and chemistry", "Chemistry Lead"),
    ("analytics-data", "Sampling, analytical methods and data systems", "Analytical/Data Lead"),
    ("statistics-doe", "DoE, statistics, inference and uncertainty", "Statistician/DoE Lead"),
    ("kinetics-properties", "Mechanism, kinetics, properties and distributions", "Property/Kinetics Modeler"),
    ("reactor-multiphysics", "Reactors, transport and multiphysics", "Reactor/Multiphysics Lead"),
    ("process-synthesis", "Separation, recycle, utilities and process synthesis", "Process Systems Lead"),
    ("scaleup-pilot", "Lab, bench, pilot, demonstration and scale-up", "Scale-up/Pilot Lead"),
    ("control-operations", "Steady state, dynamics, control and operations", "Control/Operations Lead"),
    ("hse-reliability", "Safety, environment, reliability and integrity", "HSE/Reliability Lead"),
    ("tea-supply-ip", "Economics, lifecycle, supply chain and IP interface", "TEA/Supply/IP Lead"),
    ("reporting-transfer", "Reports, process package, acceptance and transfer", "Package Publisher"),
)
SUBSKILLS = ("process-general", "epdm", "poe", "polymer-general")


def build_work_packages(project_id: str) -> list[dict[str, Any]]:
    if not isinstance(project_id, str) or not project_id.strip():
        raise ValueError("project_id must be a non-empty string")
    packages: list[dict[str, Any]] = []
    for gate_index, gate_id in enumerate(GATES):
        for stream_index, (stream_id, title, owner_role) in enumerate(WORKSTREAMS, start=1):
            packages.append({
                "work_package_id": f"{project_id}-{gate_id}-{stream_index:02d}",
                "gate_id": gate_id,
                "workstream_id": stream_id,
                "title": title,
                "owner_role": owner_role,
                "status": "PLANNED",
                "approval_status": "NOT_EVALUATED",
                "inputs": [], "outputs": [], "blockers": [],
                "external_execution": False,
                "dependency_gate": None if gate_index == 0 else GATES[gate_index - 1],
            })
    return packages


def initial_maturity_record() -> dict[str, Any]:
    return {
        "current_level": "M0",
        "status": "NOT_EVALUATED",
        "evidence_ids": [],
        "approver": None,
        "levels": [
            {"level": value.split()[0], "definition": value.split(" ", 1)[1], "status": "NOT_EVALUATED"}
            for value in MATURITY_LEVELS
        ],
    }


def capability_contract_issues(root: Path) -> list[str]:
    root = Path(root)
    required = [
        "SKILL.md", "README.md", "README.zh-CN.md",
        "skills/process-general/SKILL.md", "skills/epdm/SKILL.md",
        "skills/poe/SKILL.md", "skills/polymer-general/SKILL.md",
        "schemas/work_package.schema.json", "schemas/maturity.schema.json",
        "schemas/scaleup_claim.schema.json", "schemas/external_execution.schema.json",
        "schemas/acceptance.schema.json",
    ]
    issues = [f"missing capability artifact: {item}" for item in required if not (root / item).is_file()]
    modules = list((root / "skills/process-general/modules").glob("*.md"))
    if len(modules) != 14:
        issues.append(f"process-general must contain 14 modules, found {len(modules)}")
    if (root / "SKILL.md").is_file():
        text = (root / "SKILL.md").read_text(encoding="utf-8").casefold()
        for token in ("g0", "g18", "m0 idea", "m9 operationally-validated", "parallel professional workstreams"):
            if token not in text:
                issues.append(f"root skill missing capability token: {token}")
    return issues
