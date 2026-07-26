from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
ASSET_PATTERN = re.compile(r"!\[([^\]]+)\]\((docs/assets/readme/[^)]+\.svg)\)")


def declared_asset_names() -> set[str]:
    from scripts.generate_decision_readme_assets import ASSETS as DECISION_ASSETS
    from scripts.generate_extended_readme_assets import EXTRA_ASSETS
    from scripts.generate_readme_assets import ASSETS

    return set(ASSETS) | set(EXTRA_ASSETS) | set(DECISION_ASSETS)


def test_bilingual_readmes_reference_every_declared_local_svg_asset():
    declared_names = declared_asset_names()
    assert len(declared_names) >= 16

    expected_names: set[str] | None = None
    for readme_name in ("README.md", "README.zh-CN.md"):
        readme_text = (ROOT / readme_name).read_text(encoding="utf-8")
        matches = ASSET_PATTERN.findall(readme_text)
        assert len(matches) == len(declared_names)
        assert all(alt.strip() for alt, _ in matches)

        asset_paths = [ROOT / relative for _, relative in matches]
        assert all(path.is_file() for path in asset_paths)
        for path in asset_paths:
            document = ElementTree.parse(path)
            assert document.getroot().tag.endswith("svg")

        current_names = {path.name for path in asset_paths}
        assert current_names == declared_names
        if expected_names is None:
            expected_names = current_names
        else:
            assert current_names == expected_names


def test_readme_assets_are_deterministically_declared_by_generators():
    from scripts.generate_decision_readme_assets import ASSETS as DECISION_ASSETS
    from scripts.generate_extended_readme_assets import EXTRA_ASSETS
    from scripts.generate_readme_assets import ASSETS, OUT

    generated_names = set(ASSETS) | set(EXTRA_ASSETS) | set(DECISION_ASSETS)
    committed_names = {path.name for path in OUT.glob("*.svg")}
    assert generated_names == committed_names
    assert len(generated_names) >= 16
