from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected exactly one source anchor")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    runtime = ROOT / "scripts/verify_wheel_runtime.py"
    replace_once(
        runtime,
        'if skillpacks.get("readme_svg_assets", 0) < 16:',
        'if skillpacks.get("readme_svg_assets", 0) < 18:',
        "runtime asset threshold",
    )
    replace_once(
        runtime,
        'errors.append(f"{label} does not contain all sixteen README assets")',
        'errors.append(f"{label} does not contain all eighteen README assets")',
        "runtime asset message",
    )

    wheel = ROOT / "scripts/verify_wheel_contents.py"
    replace_once(
        wheel,
        '_README_ASSETS = (\n    "control-safety-cause-effect.svg",',
        '_README_ASSETS = (\n    "batch-parameter-scan.svg",\n    "control-safety-cause-effect.svg",',
        "wheel batch asset",
    )
    replace_once(
        wheel,
        '    "process-package-data-model.svg",\n    "recovery-recycle-risk-loop.svg",',
        '    "process-package-data-model.svg",\n    "performance-regression-gate.svg",\n    "recovery-recycle-risk-loop.svg",',
        "wheel performance asset",
    )
    replace_once(
        wheel,
        '    "generate_decision_readme_assets.py",\n    "run_ci.py",',
        '    "generate_decision_readme_assets.py",\n    "generate_performance_readme_assets.py",\n    "generate_uiux_readme_assets.py",\n    "sync_readme_visuals.py",\n    "run_ci.py",',
        "wheel visual maintenance scripts",
    )
    replace_once(
        wheel,
        '    "compare_performance.py",\n    "update_performance_readme.py",',
        '    "compare_performance.py",\n    "benchmark_performance_v2.py",\n    "compare_performance_v2.py",\n    "update_performance_readme.py",',
        "wheel performance v2 scripts",
    )
    replace_once(
        wheel,
        '        f"{_SHARE_ROOT}/docs/CAPABILITY_MATRIX.md",',
        '        f"{_SHARE_ROOT}/docs/CAPABILITY_MATRIX.md",\n        f"{_SHARE_ROOT}/docs/README_VISUAL_SYSTEM.md",',
        "wheel visual system document",
    )

    wheel_test = ROOT / "tests/test_wheel_contract.py"
    replace_once(
        wheel_test,
        '            "readme_svg_assets": 16,',
        '            "readme_svg_assets": 18,',
        "wheel test asset count",
    )

    repository_test = ROOT / "tests/test_repository_contracts.py"
    text = repository_test.read_text(encoding="utf-8")
    required = (
        '    "scripts/verify_wheel_runtime.py",\n',
        '    "scripts/verify_wheel_runtime.py",\n'
        '    "scripts/generate_uiux_readme_assets.py",\n'
        '    "scripts/sync_readme_visuals.py",\n'
        '    "docs/README_VISUAL_SYSTEM.md",\n',
    )
    if required[1] not in text:
        if text.count(required[0]) != 1:
            raise SystemExit("repository required-path anchor is not unique")
        repository_test.write_text(text.replace(required[0], required[1], 1), encoding="utf-8")

    print("applied eighteen-diagram UI/UX visual delivery contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
