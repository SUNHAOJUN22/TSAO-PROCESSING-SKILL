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


def test_ci_installs_the_verified_lock_without_dependency_resolution() -> None:
    text = _workflow_text()
    assert text.count("python -m pip install --quiet --require-hashes -r requirements.lock") == 2
    assert text.count("python -m pip install --quiet --no-deps --no-build-isolation -e .") == 2
    assert "--allow-missing" not in text
    assert "pip install --quiet -e .[dev]" not in text

def test_ci_records_the_exact_main_sha_and_run_result() -> None:
    text = _workflow_text()
    assert "qualification-ledger:" in text
    assert "needs: [qualification, source-snapshot]" in text
    assert "issues: write" in text
    assert 'gh issue comment 68 --repo "$GITHUB_REPOSITORY"' in text
    assert 'test "$verdict" = PASS' in text

