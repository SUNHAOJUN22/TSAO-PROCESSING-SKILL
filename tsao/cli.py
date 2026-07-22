from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import (
    audit_project,
    bootstrap_project,
    deterministic_zip,
    route,
    validate_zip_archive,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tsao")
    commands = parser.add_subparsers(dest="command", required=True)

    route_parser = commands.add_parser("route", help="classify a process-development brief")
    route_parser.add_argument("text")

    init_parser = commands.add_parser("init", help="initialize a fail-closed project workspace")
    init_parser.add_argument("--brief", required=True)
    init_parser.add_argument("--out", required=True)
    init_parser.add_argument("--templates", default="templates")

    audit_parser = commands.add_parser("audit", help="audit a TSAO project workspace")
    audit_parser.add_argument("--root", required=True)

    build_parser = commands.add_parser("build", help="create a deterministic project archive")
    build_parser.add_argument("--root", required=True)
    build_parser.add_argument("--out", required=True)

    verify_parser = commands.add_parser("verify-archive", help="validate ZIP safety and integrity")
    verify_parser.add_argument("--archive", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "route":
            print(json.dumps(route(args.text), ensure_ascii=False))
            return 0
        if args.command == "init":
            manifest = bootstrap_project(
                Path(args.brief), Path(args.out), Path(args.templates)
            )
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
            return 0
        if args.command == "audit":
            issues = audit_project(Path(args.root))
            print(
                json.dumps(
                    {"pass": not issues, "issues": issues},
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0 if not issues else 2
        if args.command == "build":
            print(deterministic_zip(Path(args.root), Path(args.out)))
            return 0
        if args.command == "verify-archive":
            issues = validate_zip_archive(Path(args.archive))
            print(
                json.dumps(
                    {"pass": not issues, "issues": issues},
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0 if not issues else 2
    except (OSError, TypeError, ValueError) as exc:
        print(
            json.dumps({"pass": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
