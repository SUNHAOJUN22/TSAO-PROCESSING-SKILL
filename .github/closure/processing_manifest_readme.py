"""One-shot deterministic closure for Processing provenance and README boundaries."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/closure-processing-manifest-readme.yml"
SELF = Path(__file__).resolve()
MARKER = "<!-- closure:qualification-boundary -->"


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def update_readme(path: str, section: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if MARKER in text:
        text = text.split(MARKER, 1)[0].rstrip()
    target.write_text(f"{text}\n\n{MARKER}\n{section.strip()}\n", encoding="utf-8")


def main() -> int:
    WORKFLOW.unlink()
    SELF.unlink()
    closure_dir = SELF.parent
    if closure_dir.exists() and not any(closure_dir.iterdir()):
        closure_dir.rmdir()

    update_readme(
        "README.md",
        """
## Qualification and controlled-distribution boundary

The performance gate annotates repository-scale work units through a tested, fail-closed helper before comparing like-for-like runs. Missing, non-finite, zero, or mismatched work-unit metadata is rejected rather than converted into a favorable timing result.

Software qualification is evaluated from the exact source tree. A successful test, doctor, coverage, or performance result does **not** authorize a public wheel, sdist, or source snapshot. While controlled historical metadata remains classified as project-controlled, public artifacts must continue to fail with `BLOCKED_CONTROLLED_METADATA_CLASSIFICATION` and must leave no distributable artifact behind.
""",
    )
    update_readme(
        "README.zh-CN.md",
        """
## 软件资格与受控分发边界

性能门通过经过测试、失败封闭的注释器记录仓库尺度工作量，再比较同一工作合同下的结果。缺失、非有限、为零或身份不一致的工作量元数据会被拒绝，不能被转换成有利的性能结论。

软件资格绑定到精确源码树。测试、doctor、覆盖率或性能门通过，均不构成公开 wheel、sdist 或源码快照的授权。只要受控历史元数据仍被标记为项目受控，公共制品就必须继续以 `BLOCKED_CONTROLLED_METADATA_CLASSIFICATION` 失败封闭，并且不得留下可分发制品。
""",
    )

    run(sys.executable, "-m", "ruff", "check", "--fix", "tests/test_performance_work_unit_annotation.py")
    run(sys.executable, "-m", "ruff", "format", "tests/test_performance_work_unit_annotation.py")
    run(
        sys.executable,
        "scripts/build_source_asset_manifest.py",
        "--root",
        ".",
        "--out",
        "reports/SOURCE_CORE_MANIFEST.tsv",
    )

    for script in (
        "generate_readme_assets.py",
        "generate_extended_readme_assets.py",
        "generate_decision_readme_assets.py",
        "generate_performance_readme_assets.py",
        "generate_uiux_readme_assets.py",
        "harden_readme_svg_accessibility.py",
        "verify_readme_visual_accessibility.py",
    ):
        run(sys.executable, f"scripts/{script}")
    run(sys.executable, "scripts/sync_readme_visuals.py", "--check")
    run(sys.executable, "scripts/run_ci.py")
    run(
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "tests/test_performance_work_unit_annotation.py",
        "tests/test_doctor_alpha5.py",
        "tests/test_performance_contract.py",
        "tests/test_performance_v2_numeric_parity.py",
    )
    run(
        sys.executable,
        "-m",
        "ruff",
        "check",
        "tsao",
        "tests",
        "scripts",
        "skills/process-general",
        "skills/epdm",
        "skills/poe",
        "skills/polymer-general",
    )
    run(
        sys.executable,
        "-m",
        "ruff",
        "format",
        "--check",
        "tsao",
        "tests",
        "scripts",
        "skills/process-general",
        "skills/epdm",
        "skills/poe",
        "skills/polymer-general",
    )
    run(sys.executable, "-m", "tsao.cli", "doctor", "--root", ".", "--profile", "core")
    run("git", "diff", "--check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
