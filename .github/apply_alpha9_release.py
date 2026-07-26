from __future__ import annotations

import configparser
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_VERSION = "0.1.0-alpha.9"
PEP440_VERSION = "0.1.0a9"


def replace_once(relative: str, old: str, new: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected text not found in {relative}: {old[:120]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def write_json(relative: str, payload: dict[str, object]) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def update_pyproject() -> None:
    replace_once("pyproject.toml", 'version = "0.1.0a8"', f'version = "{PEP440_VERSION}"')
    replace_once(
        "pyproject.toml",
        '''classifiers = [
  "Development Status :: 3 - Alpha",
  "License :: OSI Approved :: Apache Software License",
  "Programming Language :: Python :: 3",
  "Topic :: Scientific/Engineering :: Chemistry",
]

[project.optional-dependencies]''',
        '''classifiers = [
  "Development Status :: 3 - Alpha",
  "License :: OSI Approved :: Apache Software License",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Programming Language :: Python :: 3.14",
  "Topic :: Scientific/Engineering :: Chemistry",
]

[project.urls]
Source = "https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL"
Issues = "https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/issues"

[project.optional-dependencies]''',
    )
    replace_once(
        "pyproject.toml",
        '''  "reports/FINAL_AUDIT_REPORT.md",
  "reports/README.md",
]''',
        '''  "reports/FINAL_AUDIT_REPORT.md",
  "reports/README.md",
  "reports/RELEASE_IDENTITY.json",
  "reports/ALPHA9_SOURCE_CORE_STATUS.json",
  "reports/COMPLETE_DISTRIBUTION_REFERENCE.json",
  "reports/SOURCE_CORE_MANIFEST.tsv",
]''',
    )


def update_current_identity_files() -> None:
    replace_once(
        "tsao/__init__.py",
        '__version__ = "0.1.0-alpha.8"',
        f'__version__ = "{PUBLIC_VERSION}"',
    )
    replace_once("manifest.yaml", "version: 0.1.0-alpha.8", f"version: {PUBLIC_VERSION}")
    replace_once("SKILL.md", "version: 0.1.0-alpha.8", f"version: {PUBLIC_VERSION}")
    replace_once("CITATION.cff", "version: 0.1.0-alpha.8", f"version: {PUBLIC_VERSION}")
    replace_once("CITATION.cff", "date-released: 2026-07-24", "date-released: 2026-07-26")
    replace_once("README.md", "status-alpha.8", "status-alpha.9")
    replace_once("README.zh-CN.md", "status-alpha.8", "status-alpha.9")
    replace_once(
        "docs/CAPABILITY_MATRIX.md",
        "# TSAO capability matrix — 0.1.0-alpha.8",
        f"# TSAO capability matrix — {PUBLIC_VERSION}",
    )


def update_ci() -> None:
    replace_once(
        ".github/workflows/ci.yml",
        "name: TSAO alpha8 qualification",
        "name: TSAO alpha9 qualification",
    )
    replace_once(".github/workflows/ci.yml", "[FINALIZE-ALPHA8]", "[FINALIZE-ALPHA9]")
    replace_once(
        ".github/workflows/ci.yml",
        "TSAO-PROCESSING-SKILL-source-alpha.8.zip",
        "TSAO-PROCESSING-SKILL-source-alpha.9.zip",
    )
    replace_once(".github/workflows/ci.yml", "tsao-source-alpha8-", "tsao-source-alpha9-")


def update_changelog() -> None:
    replace_once(
        "CHANGELOG.md",
        "## Unreleased hardening — 2026-07-26",
        f"## {PUBLIC_VERSION} — 2026-07-26",
    )
    replace_once(
        "CHANGELOG.md",
        '''- Added cross-platform Skillpack smoke checks and downloadable structured qualification reports to GitHub Actions.

## 0.1.0-alpha.8''',
        '''- Added cross-platform Skillpack smoke checks and downloadable structured qualification reports to GitHub Actions.
- Sealed target-directory and clean standard-virtual-environment installs with hard module/data origin checks.
- Promoted the hardened source tree to alpha.9 so distinct source and Wheel contents no longer share the released alpha.8 identity.
- Added exact Python classifiers, project URLs, dependency-parity tests and Wheel METADATA/console-script verification.
- Packaged immutable release identity, current source status, complete-distribution boundary and source manifest inside the Wheel.

## 0.1.0-alpha.8''',
    )


def update_reports() -> None:
    identity_path = ROOT / "reports/RELEASE_IDENTITY.json"
    identity = json.loads(identity_path.read_text(encoding="utf-8"))
    identity["version"] = PUBLIC_VERSION
    source_core = identity["source_core"]
    if not isinstance(source_core, dict):
        raise RuntimeError("reports/RELEASE_IDENTITY.json source_core must be an object")
    source_core["status"] = "reports/ALPHA9_SOURCE_CORE_STATUS.json"
    write_json("reports/RELEASE_IDENTITY.json", identity)

    write_json(
        "reports/COMPLETE_DISTRIBUTION_REFERENCE.json",
        {
            "format": "TSAO-COMPLETE-DISTRIBUTION-REFERENCE-2",
            "version": PUBLIC_VERSION,
            "qualification": "NOT_EVALUATED",
            "reason": (
                "The controlled complete distribution, including excluded historical binary "
                "assets, has not been rebuilt and cleanroom-qualified for alpha.9. The public "
                "source core and open Wheel are verified separately."
            ),
            "historical_reference": "reports/history/COMPLETE_DISTRIBUTION_REFERENCE_ALPHA6.json",
            "scientific_technical_approval": "NOT_EVALUATED",
            "engineering_design_approval": "NOT_EVALUATED",
            "industrial_performance_guarantee": "NOT_EVALUATED",
        },
    )
    write_json(
        "reports/ALPHA9_SOURCE_CORE_STATUS.json",
        {
            "version": PUBLIC_VERSION,
            "status": "QUALIFIED_ALPHA",
            "source_core_manifest": "reports/SOURCE_CORE_MANIFEST.tsv",
            "universal_process_package": "IMPLEMENTED_ALPHA",
            "process_general_modules": "14_OF_14",
            "process_general_workflows": "6_OF_6",
            "epdm": "EXECUTABLE_FLAGSHIP_ALPHA_P1_REFERENCE",
            "epdm_module_contracts": "14_OF_14",
            "epdm_requirement_registry": "20_OF_20",
            "poe": "EXECUTABLE_SPECIALIST_ALPHA_P1_REFERENCE",
            "polymer_general_scripts": "6_OF_6",
            "readme_assets": "16_OF_16",
            "python_versions": ["3.11", "3.12", "3.13", "3.14"],
            "wheel_install_modes": ["PIP_TARGET", "STANDARD_VENV"],
            "standard_venv_isolation": "NO_SYSTEM_SITE_PACKAGES",
            "installed_import_origin": "VERIFIED_INSIDE_INSTALL_ROOT",
            "artifact_software_qualification": "PASS",
            "scientific_technical_approval": "NOT_EVALUATED",
            "engineering_design_approval": "NOT_EVALUATED",
            "customer_qualification": "NOT_EVALUATED",
            "industrial_performance_guarantee": "NOT_EVALUATED",
        },
    )

    (ROOT / "reports/README.md").write_text(
        '''# Reports

This directory separates immutable release/source identities from mutable runtime output. Software qualification never substitutes for scientific, engineering, HSE, legal, customer or industrial approval.

## Current alpha.9 identities

- `RELEASE_IDENTITY.json` — alpha.9 source/release boundary and current source-status pointer.
- `ALPHA9_SOURCE_CORE_STATUS.json` — qualified public source, four-Skill, sixteen-diagram and isolated-install status.
- `SOURCE_CORE_MANIFEST.tsv` — frozen public-source identity verified by `tsao doctor --profile core`.
- `COMPLETE_DISTRIBUTION_REFERENCE.json` — explicitly `NOT_EVALUATED` until the controlled complete distribution, including excluded historical binaries, is rebuilt and cleanroom-qualified for alpha.9.
- `FINAL_AUDIT_REPORT.md` — latest repository, Wheel, CI, branch and responsibility-boundary audit.
- `poe/POE_ALPHA7_P1_REMEDIATION.md` — POE P1 remediation history and remaining external Gates.

## Historical identities

- `ALPHA8_SOURCE_CORE_STATUS.json` and `ALPHA8_PROCESS_PACKAGE_EPDM_REMEDIATION.md` — frozen alpha.8 records.
- `ALPHA7_SOURCE_CORE_STATUS.json` — frozen alpha.7 source identity.
- `history/COMPLETE_DISTRIBUTION_REFERENCE_ALPHA6.json` — qualified alpha.6 controlled complete distribution.
- `history/ALPHA6_SOURCE_CORE_STATUS.json` and `history/CI_RESULTS_BEFORE_RUNTIME_SPLIT.json` — frozen alpha.6 records.
- Alpha.6 POE P0 reports remain historical evidence of the preceding release.

## Runtime output

`scripts/run_ci.py` writes mutable execution output under `reports/runtime/`. Runtime files are excluded from frozen source and release manifests. Promote a result to a versioned report only with the exact tested source identity and approval boundary.
''',
        encoding="utf-8",
    )

    replace_once(
        "reports/FINAL_AUDIT_REPORT.md",
        "Repository: `SUNHAOJUN22/TSAO-PROCESSING-SKILL`",
        f"Repository: `SUNHAOJUN22/TSAO-PROCESSING-SKILL`  \nRelease identity: `{PUBLIC_VERSION}`",
    )
    replace_once(
        "reports/FINAL_AUDIT_REPORT.md",
        "This pass closed four remaining release-consistency gaps:",
        "This pass closed six remaining release-consistency gaps:",
    )
    replace_once(
        "reports/FINAL_AUDIT_REPORT.md",
        '''4. the visual system did not separately show control/safety, simulator-neutral exchange, EPDM parameter confidence or the raw-polymer-to-customer evidence bridge.

## Branch state''',
        '''4. the visual system did not separately show control/safety, simulator-neutral exchange, EPDM parameter confidence or the raw-polymer-to-customer evidence bridge;
5. substantial post-alpha.8 source and Wheel changes still reused the released alpha.8 identity;
6. the reports index and complete-distribution reason still described alpha.7, and immutable release identities were not shipped inside the Wheel.

## Release identity convergence

The current source, Python package, Skill manifest, citation, capability matrix, CI archive names, report index and Wheel metadata now identify `0.1.0-alpha.9` (`0.1.0a9` in PEP 440 form). Alpha.8 reports remain historical records. Requirements and `pyproject.toml` dependency declarations are tested for exact parity, and the built Wheel must expose the matching METADATA version plus both console scripts.

## Branch state''',
    )


def update_repository_contracts() -> None:
    replace_once(
        "tests/test_repository_contracts.py",
        '''    "reports/ALPHA8_SOURCE_CORE_STATUS.json",
    "reports/history/COMPLETE_DISTRIBUTION_REFERENCE_ALPHA6.json",''',
        '''    "reports/ALPHA8_SOURCE_CORE_STATUS.json",
    "reports/ALPHA9_SOURCE_CORE_STATUS.json",
    "reports/history/COMPLETE_DISTRIBUTION_REFERENCE_ALPHA6.json",''',
    )
    replace_once(
        "tests/test_repository_contracts.py",
        'assert tsao.__version__ == "0.1.0-alpha.8"',
        f'assert tsao.__version__ == "{PUBLIC_VERSION}"',
    )
    replace_once(
        "tests/test_repository_contracts.py",
        'assert pyproject["project"]["version"] == "0.1.0a8"',
        f'assert pyproject["project"]["version"] == "{PEP440_VERSION}"',
    )
    replace_once(
        "tests/test_repository_contracts.py",
        'assert "## 0.1.0-alpha.8" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")',
        f'assert "## {PUBLIC_VERSION}" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")',
    )
    replace_once(
        "tests/test_repository_contracts.py",
        'assert "alpha8" in workflow.casefold()',
        'assert "alpha9" in workflow.casefold()',
    )


def update_wheel_identity_verifier() -> None:
    path = ROOT / "scripts/verify_wheel_contents.py"
    text = path.read_text(encoding="utf-8")
    old_imports = '''import argparse
import json
import zipfile
from pathlib import Path
'''
    new_imports = '''import argparse
import configparser
import json
import zipfile
from email.parser import Parser
from pathlib import Path

from tsao import __version__
'''
    if old_imports not in text:
        raise RuntimeError("Wheel verifier import block not found")
    text = text.replace(old_imports, new_imports, 1)

    old_constants = '''_SHARE_ROOT = "share/tsao-processing-skill"


def _choose_wheel'''
    new_constants = '''_SHARE_ROOT = "share/tsao-processing-skill"
_EXPECTED_DIST_NAME = "tsao-processing-skill"
_EXPECTED_PEP440_VERSION = __version__.replace("-alpha.", "a")
_EXPECTED_CONSOLE_SCRIPTS = {
    "tsao": "tsao.cli:main",
    "tsao-skillpacks": "tsao.skillpacks:main",
}


def _choose_wheel'''
    if old_constants not in text:
        raise RuntimeError("Wheel verifier constant block not found")
    text = text.replace(old_constants, new_constants, 1)

    helpers = '''def _unique_dist_info_member(
    names: set[str],
    suffix: str,
    *,
    label: str,
    errors: list[str],
) -> str | None:
    matches = sorted(name for name in names if name.endswith(f".dist-info/{suffix}"))
    if len(matches) != 1:
        errors.append(f"expected exactly one Wheel {label}, found {len(matches)}")
        return None
    return matches[0]


def _verify_wheel_identity(
    archive: zipfile.ZipFile,
    wheel: Path,
    names: set[str],
    errors: list[str],
) -> dict[str, object]:
    identity: dict[str, object] = {
        "expected_name": _EXPECTED_DIST_NAME,
        "expected_version": _EXPECTED_PEP440_VERSION,
        "console_scripts": {},
    }
    if f"-{_EXPECTED_PEP440_VERSION}-" not in wheel.name:
        errors.append(
            "wheel filename version mismatch: "
            f"expected {_EXPECTED_PEP440_VERSION} in {wheel.name}"
        )

    metadata_member = _unique_dist_info_member(
        names,
        "METADATA",
        label="METADATA member",
        errors=errors,
    )
    if metadata_member is not None:
        try:
            metadata = Parser().parsestr(archive.read(metadata_member).decode("utf-8"))
        except (KeyError, UnicodeDecodeError) as exc:
            errors.append(f"could not read Wheel METADATA: {exc}")
        else:
            actual_name = (metadata.get("Name") or "").casefold().replace("_", "-")
            actual_version = metadata.get("Version") or ""
            identity["metadata_name"] = actual_name
            identity["metadata_version"] = actual_version
            if actual_name != _EXPECTED_DIST_NAME:
                errors.append(
                    "wheel metadata name mismatch: "
                    f"expected {_EXPECTED_DIST_NAME}, found {actual_name or '<missing>'}"
                )
            if actual_version != _EXPECTED_PEP440_VERSION:
                errors.append(
                    "wheel metadata version mismatch: "
                    f"expected {_EXPECTED_PEP440_VERSION}, found {actual_version or '<missing>'}"
                )

    entry_member = _unique_dist_info_member(
        names,
        "entry_points.txt",
        label="entry_points.txt member",
        errors=errors,
    )
    scripts: dict[str, str] = {}
    if entry_member is not None:
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str
        try:
            parser.read_string(archive.read(entry_member).decode("utf-8"))
        except (KeyError, UnicodeDecodeError, configparser.Error) as exc:
            errors.append(f"could not read Wheel entry points: {exc}")
        else:
            if parser.has_section("console_scripts"):
                scripts = dict(parser.items("console_scripts"))
    identity["console_scripts"] = scripts
    for name, target in _EXPECTED_CONSOLE_SCRIPTS.items():
        if name not in scripts:
            errors.append(f"missing wheel console script: {name}")
        elif scripts[name] != target:
            errors.append(
                f"wheel console script mismatch for {name}: "
                f"expected {target}, found {scripts[name]}"
            )
    return identity


'''
    marker = "def verify(wheel: Path) -> dict[str, object]:\n"
    if marker not in text:
        raise RuntimeError("Wheel verifier entry point not found")
    text = text.replace(marker, helpers + marker, 1)

    old_verify_open = '''def verify(wheel: Path) -> dict[str, object]:
    errors: list[str] = []
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
    missing = sorted(_REQUIRED - names)'''
    new_verify_open = '''def verify(wheel: Path) -> dict[str, object]:
    errors: list[str] = []
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        identity = _verify_wheel_identity(archive, wheel, names, errors)
    missing = sorted(_REQUIRED - names)'''
    if old_verify_open not in text:
        raise RuntimeError("Wheel verifier body opening not found")
    text = text.replace(old_verify_open, new_verify_open, 1)

    old_reports = '''        f"{_SHARE_ROOT}/reports/FINAL_AUDIT_REPORT.md",
        f"{_SHARE_ROOT}/schemas/project.schema.json",'''
    new_reports = '''        f"{_SHARE_ROOT}/reports/FINAL_AUDIT_REPORT.md",
        f"{_SHARE_ROOT}/reports/RELEASE_IDENTITY.json",
        f"{_SHARE_ROOT}/reports/ALPHA9_SOURCE_CORE_STATUS.json",
        f"{_SHARE_ROOT}/reports/COMPLETE_DISTRIBUTION_REFERENCE.json",
        f"{_SHARE_ROOT}/reports/SOURCE_CORE_MANIFEST.tsv",
        f"{_SHARE_ROOT}/schemas/project.schema.json",'''
    if old_reports not in text:
        raise RuntimeError("Wheel verifier report requirements not found")
    text = text.replace(old_reports, new_reports, 1)

    old_return = '''        "errors": errors,
        "poe_members": len([name for name in names if name.startswith("skills/poe/")]),'''
    new_return = '''        "errors": errors,
        "identity": identity,
        "poe_members": len([name for name in names if name.startswith("skills/poe/")]),'''
    if old_return not in text:
        raise RuntimeError("Wheel verifier result block not found")
    text = text.replace(old_return, new_return, 1)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    update_pyproject()
    update_current_identity_files()
    update_ci()
    update_changelog()
    update_reports()
    update_repository_contracts()
    update_wheel_identity_verifier()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
