#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VISUAL_COUNT = 29


def _replace_once(text: str, old: str, new: str, *, label: str) -> str:
    if new in text:
        return text
    if text.count(old) != 1:
        raise ValueError(f"{label}: expected exactly one source anchor")
    return text.replace(old, new, 1)


def _english(text: str) -> str:
    text = _replace_once(
        text,
        "all 21 README diagrams",
        f"all {VISUAL_COUNT} README diagrams",
        label="English inventory count",
    )
    text = _replace_once(
        text,
        "all 21 diagrams",
        f"all {VISUAL_COUNT} diagrams",
        label="English Wheel count",
    )
    if "docs/assets/readme/ai-scientific-reasoning-loop.svg" not in text:
        raise ValueError("English AI visual section is missing")
    return text


def _chinese(text: str) -> str:
    text = _replace_once(
        text,
        "全部 21 幅 README 图",
        f"全部 {VISUAL_COUNT} 幅 README 图",
        label="Chinese inventory count",
    )
    text = _replace_once(
        text,
        "全部 21 幅图",
        f"全部 {VISUAL_COUNT} 幅图",
        label="Chinese Wheel count",
    )
    if "docs/assets/readme/ai-scientific-reasoning-loop.svg" not in text:
        raise ValueError("Chinese AI visual section is missing")
    return text


def _sync(path: Path, transform, *, check: bool) -> bool:
    current = path.read_text(encoding="utf-8")
    updated = transform(current)
    if check:
        return current == updated
    path.write_text(updated, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synchronize bilingual README visual contracts")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    results = [
        _sync(ROOT / "README.md", _english, check=args.check),
        _sync(ROOT / "README.zh-CN.md", _chinese, check=args.check),
    ]
    return 0 if all(results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
