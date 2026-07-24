from __future__ import annotations

import base64
import hashlib
from pathlib import Path

ROOT = Path.cwd()


def patch_mother_files() -> None:
    parts = sorted((ROOT / "reports/runtime").glob("alpha8-capabilities.b64.*"))
    payload = base64.b64decode(
        "".join(path.read_text(encoding="ascii") for path in parts),
        validate=True,
    )
    expected = "0bb0d0b6be957b4d6e6ca3439dd227a3cac93a1b41ba2004e2aa7037fec76dc2"
    if hashlib.sha256(payload).hexdigest() != expected:
        raise SystemExit("capabilities SHA mismatch")
    (ROOT / "tsao/capabilities.py").write_bytes(payload)

    path = ROOT / "tsao/cli.py"
    text = path.read_text(encoding="utf-8")
    if 'commands.add_parser("package"' not in text:
        parser_marker = '    poe_commands.add_parser("reference-demo")\n    return parser\n'
        parser_block = """    poe_commands.add_parser("reference-demo")

    package_parser = commands.add_parser("package", help="universal process-package templates and audits")
    package_commands = package_parser.add_subparsers(dest="package_command", required=True)
    package_template = package_commands.add_parser("template")
    package_template.add_argument("--family", required=True)
    package_audit = package_commands.add_parser("audit")
    package_audit.add_argument("--file", required=True)

    epdm_parser = commands.add_parser("epdm", help="EPDM flagship status, audit and references")
    epdm_commands = epdm_parser.add_subparsers(dest="epdm_command", required=True)
    epdm_commands.add_parser("status")
    epdm_audit = epdm_commands.add_parser("audit")
    epdm_audit.add_argument("--file")
    epdm_commands.add_parser("reference-demo")
    return parser
"""
        if parser_marker not in text:
            raise SystemExit("CLI parser marker missing")
        text = text.replace(parser_marker, parser_block, 1)

    if 'if args.command == "package":' not in text:
        main_marker = '        if args.command == "poe":\n'
        main_block = """        if args.command == "package":
            from .process_package import process_package_template, validate_process_package

            if args.package_command == "template":
                _print(process_package_template(args.family))
                return 0
            payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
            result = validate_process_package(payload)
            _print(result)
            return 0 if result["pass"] else 2
        if args.command == "epdm":
            if args.epdm_command == "status":
                import yaml

                manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
                epdm = next(item for item in manifest["subskills"] if item["id"] == "epdm")
                _print({"version": __import__("tsao").__version__, **epdm})
                return 0
            if args.epdm_command == "audit":
                from skills.epdm.package_audit import audit_epdm_process_package

                source = Path(args.file) if args.file else Path("skills/epdm/fixtures/reference_cases.json")
                payload = json.loads(source.read_text(encoding="utf-8"))
                if not args.file:
                    payload = payload["valid_package"]
                result = audit_epdm_process_package(payload)
                _print(result)
                return 0 if result["pass"] else 2
            if args.epdm_command == "reference-demo":
                from skills.epdm.core import EpdmKineticParameters, EpdmKineticState, architecture_metrics, heat_removal_margin

                metrics = architecture_metrics(EpdmKineticState(1.2, 1.0, 0.04, 0.001, 1e-6), EpdmKineticParameters(2.0, 1.6, 0.5, 0.08, 0.02, 10.0), secondary_diene_insertion_probability=0.05, branch_efficiency=0.5, gel_critical_branch_index=1.0)
                _print({"status": "CALCULATED_REFERENCE_ONLY", "architecture": metrics, "heat_removal_margin": heat_removal_margin(80.0, 110.0), "scientific_technical_approval": "NOT_EVALUATED"})
                return 0
"""
        if main_marker not in text:
            raise SystemExit("CLI main marker missing")
        text = text.replace(main_marker, main_block + main_marker, 1)

    required_once = (
        'commands.add_parser("package"',
        'commands.add_parser("epdm"',
        'if args.command == "package":',
        'if args.command == "epdm":',
    )
    for token in required_once:
        if text.count(token) != 1:
            raise SystemExit(f"CLI token count must be one: {token}")
    path.write_text(text, encoding="utf-8")
