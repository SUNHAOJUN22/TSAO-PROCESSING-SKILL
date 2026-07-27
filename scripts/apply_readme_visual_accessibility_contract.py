from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(relative: str, old: str, new: str, label: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one source anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    command_old = (
        "python scripts/generate_uiux_readme_assets.py\n"
        "python scripts/sync_readme_visuals.py --check\n"
        "python scripts/run_ci.py"
    )
    command_new = (
        "python scripts/generate_uiux_readme_assets.py\n"
        "python scripts/harden_readme_svg_accessibility.py\n"
        "python scripts/verify_readme_visual_accessibility.py\n"
        "python scripts/sync_readme_visuals.py --check\n"
        "python scripts/run_ci.py"
    )
    replace_once("README.md", command_old, command_new, "English README visual commands")
    replace_once("README.zh-CN.md", command_old, command_new, "Chinese README visual commands")

    replace_once(
        "docs/README_VISUAL_SYSTEM.md",
        "python scripts/generate_uiux_readme_assets.py\n"
        "python scripts/sync_readme_visuals.py --check",
        "python scripts/generate_uiux_readme_assets.py\n"
        "python scripts/harden_readme_svg_accessibility.py\n"
        "python scripts/verify_readme_visual_accessibility.py\n"
        "python scripts/sync_readme_visuals.py --check",
        "visual-system generation workflow",
    )
    replace_once(
        "docs/README_VISUAL_SYSTEM.md",
        "The four historical generators remain available for lineage and focused maintenance. `generate_uiux_readme_assets.py` runs last and is the final visual-normalization layer for all 18 files.",
        "The four historical generators remain available for lineage and focused maintenance. `generate_uiux_readme_assets.py` remains the master visual-normalization layer for all 18 files; `harden_readme_svg_accessibility.py` then adds stable responsive/rendering metadata, and `verify_readme_visual_accessibility.py` fail-closes on contrast, text size, external resources, emoji, missing title/description or inconsistent root attributes. The committed palette exceeds 4.5:1 for primary text and 3:1 for secondary text and semantic glyphs on the dark surfaces.",
        "visual-system accessibility contract",
    )

    replace_once(
        "docs/CAPABILITY_MATRIX.md",
        "18 deterministic SVGs, persisted Scientific Midnight Bento design system, bilingual parity and XML accessibility tests",
        "18 deterministic SVGs, persisted Scientific Midnight Bento design system, WCAG contrast, explicit title/desc, 12px minimum text, no external resources, bilingual parity and XML accessibility tests",
        "capability visual verification boundary",
    )

    replace_once(
        ".github/workflows/ci.yml",
        "          python scripts/generate_performance_readme_assets.py\n"
        "          python scripts/generate_uiux_readme_assets.py\n"
        "          git diff --exit-code -- docs/assets/readme",
        "          python scripts/generate_performance_readme_assets.py\n"
        "          python scripts/generate_uiux_readme_assets.py\n"
        "          python scripts/harden_readme_svg_accessibility.py\n"
        "          python scripts/verify_readme_visual_accessibility.py\n"
        "          git diff --exit-code -- docs/assets/readme",
        "permanent CI visual verification",
    )

    replace_once(
        "scripts/verify_wheel_contents.py",
        '    "generate_uiux_readme_assets.py",\n    "sync_readme_visuals.py",',
        '    "generate_uiux_readme_assets.py",\n'
        '    "harden_readme_svg_accessibility.py",\n'
        '    "verify_readme_visual_accessibility.py",\n'
        '    "sync_readme_visuals.py",',
        "Wheel visual maintenance scripts",
    )

    replace_once(
        "tests/test_repository_contracts.py",
        '    "scripts/generate_uiux_readme_assets.py",\n'
        '    "scripts/sync_readme_visuals.py",',
        '    "scripts/generate_uiux_readme_assets.py",\n'
        '    "scripts/harden_readme_svg_accessibility.py",\n'
        '    "scripts/verify_readme_visual_accessibility.py",\n'
        '    "scripts/sync_readme_visuals.py",',
        "repository visual paths",
    )

    print("applied README visual accessibility delivery contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
