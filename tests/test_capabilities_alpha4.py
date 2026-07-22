from pathlib import Path

from tsao.capabilities import (
    GATES,
    MATURITY_LEVELS,
    WORKSTREAMS,
    build_work_packages,
    capability_contract_issues,
)
from tsao.project import audit_project, bootstrap_project

ROOT = Path(__file__).resolve().parents[1]


def test_capability_constants_are_complete():
    assert GATES == tuple(f"G{i}" for i in range(19))
    assert len(WORKSTREAMS) == 14
    assert len(MATURITY_LEVELS) == 10


def test_work_package_matrix_is_19_by_14_and_fail_closed():
    packages = build_work_packages("DEMO")
    assert len(packages) == 266
    assert len({item["work_package_id"] for item in packages}) == 266
    assert {item["gate_id"] for item in packages} == set(GATES)
    assert all(item["approval_status"] == "NOT_EVALUATED" for item in packages)


def test_project_bootstrap_writes_executable_artifacts(tmp_path: Path):
    brief = tmp_path / "brief.yaml"
    brief.write_text(
        "project_id: P-1\ntitle: Catalytic reactor retrofit\n"
        "summary: catalytic reactor separation control\n",
        encoding="utf-8",
    )
    project = tmp_path / "project"
    manifest = bootstrap_project(brief, project)
    assert manifest["version"] == "0.1.0-alpha.4"
    assert (project / "00_governance/work_packages.json").is_file()
    assert (project / "00_governance/maturity.json").is_file()
    assert (project / "00_governance/execution_status.json").is_file()
    assert audit_project(project) == []


def test_capability_contract_has_no_missing_artifacts():
    assert capability_contract_issues(ROOT) == []
