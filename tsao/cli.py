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
from .provenance import build_manifest
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
    doctor_parser.add_argument(
        "--strict-source-clean",
        action="store_true",
        help="fail when cache or virtual-environment paths are present",
    )
    doctor_parser.add_argument(
        "--refresh-source-manifest",
        action="store_true",
        help="rebuild SOURCE_CORE_MANIFEST.tsv before core verification",
    )

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

    poe_parser = commands.add_parser("poe", help="POE specialist status, audits and references")
    poe_commands = poe_parser.add_subparsers(dest="poe_command", required=True)
    for name in ("status", "audit-p0", "audit-p1"):
        subcommand = poe_commands.add_parser(name)
        subcommand.add_argument("--root", default=".")
    poe_commands.add_parser("reference-demo")
    return parser


def _print(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "doctor":
            root = Path(args.root)
            if args.refresh_source_manifest:
                if args.profile == "full":
                    raise ValueError("full profile cannot refresh only the public-source manifest")
                build_manifest(root, root / "reports/SOURCE_CORE_MANIFEST.tsv")
            result = diagnose(
                root,
                profile=args.profile,
                strict_source_clean=args.strict_source_clean,
            )
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
        if args.command == "poe":
            if args.poe_command == "status":
                import yaml

                root = Path(args.root)
                manifest = yaml.safe_load((root / "manifest.yaml").read_text(encoding="utf-8"))
                poe = next(item for item in manifest["subskills"] if item["id"] == "poe")
                _print({"version": __import__("tsao").__version__, **poe})
                return 0
            if args.poe_command == "audit-p0":
                from skills.poe.scripts.audit_p0 import audit as audit_p0

                result = audit_p0(Path(args.root))
                _print(result)
                return 0 if result["pass"] else 2
            if args.poe_command == "audit-p1":
                from skills.poe.scripts.audit_p1 import audit as audit_p1

                result = audit_p1(Path(args.root))
                _print(result)
                return 0 if result["pass"] else 2
            if args.poe_command == "reference-demo":
                from skills.poe.core import (
                    first_order_cstr_conversion,
                    first_order_pfr_conversion,
                    reactor_reference_suite,
                )

                _print(
                    {
                        "status": "CALCULATED_REFERENCE_ONLY",
                        "reactors": reactor_reference_suite(0.2, 5.0),
                        "PFR": first_order_pfr_conversion(0.2, 5.0),
                        "CSTR": first_order_cstr_conversion(0.2, 5.0),
                        "scientific_technical_approval": "NOT_EVALUATED",
                    }
                )
                return 0
    except (OSError, TypeError, ValueError) as exc:
        print(
            json.dumps({"pass": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
