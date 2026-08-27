from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/public-distribution-boundary.yml"


def test_controlled_registry_has_a_permanent_fail_closed_workflow() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "pull_request:" in text
    assert "schedule:" in text
    assert "workflow_dispatch:" in text
    assert "contents: read" in text
    assert "assert_public_distribution_allowed" in text
    assert "public source distribution" in text
    assert "public wheel" in text
    assert "was permitted while the registry remains controlled" in text
    assert "continue-on-error" not in text
    assert "contents: write" not in text
    assert "upload-artifact" not in text


def test_public_distribution_boundary_runs_the_containment_regressions() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "tests/test_distribution_containment_v20.py" in text
    assert "tests/test_release_integrity_alpha6.py" in text
    assert "tests/test_main_only_ci_policy.py" in text
    assert "git status --porcelain=v1" in text
