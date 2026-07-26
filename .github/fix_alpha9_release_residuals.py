from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    workflow_path = ROOT / ".github/workflows/ci.yml"
    workflow = workflow_path.read_text(encoding="utf-8")
    workflow = workflow.replace(
        "TSAO-PROCESSING-SKILL-source-alpha.8.zip",
        "TSAO-PROCESSING-SKILL-source-alpha.9.zip",
    )
    workflow_path.write_text(workflow, encoding="utf-8")

    active_files = (
        "pyproject.toml",
        "tsao/__init__.py",
        "manifest.yaml",
        "SKILL.md",
        "CITATION.cff",
        "README.md",
        "README.zh-CN.md",
        "docs/CAPABILITY_MATRIX.md",
        ".github/workflows/ci.yml",
        "reports/RELEASE_IDENTITY.json",
        "reports/COMPLETE_DISTRIBUTION_REFERENCE.json",
        "reports/README.md",
        "tests/test_repository_contracts.py",
    )
    failures: list[str] = []
    for relative in active_files:
        text = (ROOT / relative).read_text(encoding="utf-8")
        for stale in ("0.1.0-alpha.8", "0.1.0a8", "status-alpha.8"):
            if stale in text:
                failures.append(f"{relative}: stale {stale}")
    if "alpha8" in workflow.casefold() or "alpha.8.zip" in workflow:
        failures.append(".github/workflows/ci.yml: stale alpha8 archive or marker")
    if failures:
        raise RuntimeError("; ".join(failures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
