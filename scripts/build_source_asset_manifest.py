#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from tsao.provenance import build_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    count = build_manifest(Path(args.root), Path(args.out))
    print(f"files={count} out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
