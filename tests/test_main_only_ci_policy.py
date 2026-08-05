from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ci.yml"
BASELINE = "8719e59140202aae53cdfb80239b80dedad6767a"


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_ci_is_main_only_and_cancels_superseded_runs() -> None:
    text = _workflow_text()
    assert "push:\n    branches: [main]" in text
    assert "pull_request:" not in text
    assert "group: tsao-main-${{ github.workflow }}" in text
    assert "cancel-in-progress: true" in text


def test_performance_baseline_is_explicit_and_ancestry_checked() -> None:
    text = _workflow_text()
    assert f'PERFORMANCE_BASELINE_COMMIT: "{BASELINE}"' in text
    assert "git rev-parse HEAD^" not in text
    assert 'git cat-file -e "${baseline_commit}^{commit}"' in text
    assert 'git merge-base --is-ancestor "$baseline_commit" HEAD' in text
    assert 'git worktree add --detach "$baseline_root" "$baseline_commit"' in text
    assert "trap - EXIT" in text


def test_repository_tracks_only_the_permanent_ci_workflow() -> None:
    workflows = sorted(path.name for path in (ROOT / ".github/workflows").glob("*.yml"))
    assert workflows == ["ci.yml"]
    assert not (ROOT / ".github/upgrade").exists()
