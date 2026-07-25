from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
ASSET_PATTERN = re.compile(r"!\[([^\]]+)\]\((docs/assets/readme/[^)]+\.svg)\)")


def test_bilingual_readmes_have_complete_local_svg_assets():
    expected_names: set[str] | None = None
    for readme_name in ("README.md", "README.zh-CN.md"):
        text = (ROOT / readme_name).read_text(encoding="utf-8")
        matches = ASSET_PATTERN.findall(text)
        assert len(matches) >= 8
        assert all(alt.strip() for alt, _ in matches)
        paths = [ROOT / relative for _, relative in matches]
        assert all(path.is_file() for path in paths)
        for path in paths:
            document = ElementTree.parse(path)
            assert document.getroot().tag.endswith("svg")
        current_names = {path.name for path in paths}
        if expected_names is None:
            expected_names = current_names
        else:
            assert current_names == expected_names


def test_readme_assets_are_deterministically_declared_by_generator():
    from scripts.generate_readme_assets import ASSETS, OUT

    generated_names = set(ASSETS)
    committed_names = {path.name for path in OUT.glob("*.svg")}
    assert generated_names == committed_names
    assert len(generated_names) >= 8
