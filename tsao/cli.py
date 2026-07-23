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
from .doctor import diagnose
from .snapshot import build_source_snapshot


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tsao")
    commands = parser.add_subparsers(dest="command", required=True)

    route_parser = commands.add_parser("route", help="classify a process-development brief")
    route_parser.add_argument("text")

    init_parser = commands.add_parser("init", help="initialize a fail-closed project workspace")
    init_parser.add_argument("--brief", required=True)
    init_parser.add_argument("--out", required=True)
    init_parser.add_argument("--templates")

    audit_parser = commands.add_parser("audit", help="audit a TSAO project workspace")
    audit_parser.add_argument("--root", required=True)

    doctor_parser = commands.add_parser("doctor", help="audit repository and provenance integrity")
    doctor_parser.add_argument("--root", default=".")
    doctor_parser.add_argument("--profile", choices=("auto", "core", "full"), default="auto")

    build_parser = commands.add_parser("build", help="create a deterministic project archive")
    build_parser.add_argument("--root", required=True)
    build_parser.add_argument("--out", required=True)

    snapshot_parser = commands.add_parser(
        "snapshot", help="build a deterministic archive of the public source manifest"
    )
    snapshot_parser.add_argument("--root", default=".")
    snapshot_parser.add_argument("--out", required=True)

    verify_parser = commands.add_parser("verify-archive", help="validate ZIP safety and integrity")
    verify_parser.add_argument("--archive", required=True)
    return parser


def _print(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "doctor":
            result = diagnose(Path(args.root), profile=args.profile)
            _print(result)
            return 0 if result["pass"] else 2
        if args.command == "route":
            _print(route(args.text))
            return 0
        if args.command == "init":
            templates = Path(args.templates) if args.templates else None
            _print(bootstrap_project(Path(args.brief), Path(args.out), templates))
            return 0
        if args.command == "audit":
            issues = audit_project(Path(args.root))
            _print({"pass": not issues, "issues": issues})
            return 0 if not issues else 2
        if args.command == "build":
            _print({"sha256": deterministic_zip(Path(args.root), Path(args.out))})
            return 0
        if args.command == "snapshot":
            _print(build_source_snapshot(Path(args.root), Path(args.out)))
            return 0
        if args.command == "verify-archive":
            issues = validate_zip_archive(Path(args.archive))
            _print({"pass": not issues, "issues": issues})
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
