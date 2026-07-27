#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_uiux_readme_assets import ASSETS, OUT  # noqa: E402

ROOT_ATTRIBUTES = {
    "focusable": "false",
    "preserveAspectRatio": "xMidYMid meet",
    "shape-rendering": "geometricPrecision",
    "text-rendering": "optimizeLegibility",
    "data-design-system": "scientific-midnight-bento",
    "data-design-version": "2",
}
_SVG_OPEN = re.compile(r"\A<svg\b(?P<attrs>[^>]*)>", re.DOTALL)


def harden_svg_text(text: str) -> str:
    match = _SVG_OPEN.search(text)
    if match is None:
        raise ValueError("SVG document does not begin with an <svg> element")
    attrs = match.group("attrs")
    for name in ROOT_ATTRIBUTES:
        attrs = re.sub(rf'\s+{re.escape(name)}="[^"]*"', "", attrs)
    additions = "".join(f' {name}="{value}"' for name, value in ROOT_ATTRIBUTES.items())
    replacement = f"<svg{attrs}{additions}>"
    return replacement + text[match.end() :]


def harden_assets(directory: Path = OUT, *, check: bool = False) -> dict[str, object]:
    expected = set(ASSETS)
    present = {path.name for path in directory.glob("*.svg")}
    errors: list[str] = []
    if present != expected:
        missing = sorted(expected - present)
        unexpected = sorted(present - expected)
        if missing:
            errors.append(f"missing SVG assets: {missing}")
        if unexpected:
            errors.append(f"unexpected SVG assets: {unexpected}")

    changed: list[str] = []
    for name in sorted(expected & present):
        path = directory / name
        original = path.read_text(encoding="utf-8")
        try:
            hardened = harden_svg_text(original)
        except ValueError as exc:
            errors.append(f"{name}: {exc}")
            continue
        if hardened != original:
            changed.append(name)
            if not check:
                path.write_text(hardened, encoding="utf-8")

    if check and changed:
        errors.append(f"SVG accessibility hardening is not current: {changed}")
    return {
        "pass": not errors,
        "asset_count": len(expected),
        "changed": changed,
        "check_mode": check,
        "root_attributes": ROOT_ATTRIBUTES,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Harden TSAO README SVG accessibility metadata")
    parser.add_argument("--directory", type=Path, default=OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = harden_assets(args.directory, check=args.check)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
