from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from . import __version__
from .capabilities import capability_contract_issues
from .provenance import verify_manifest

_REQUIRED = (
    "README.md",
    "README.zh-CN.md",
    "SKILL.md",
    "ARCHITECTURE.md",
    "manifest.yaml",
    "pyproject.toml",
    "CITATION.cff",
    "schemas/project.schema.json",
    "schemas/source_asset.schema.json",
    "skills/process-general/SKILL.md",
    "skills/epdm/SKILL.md",
    "skills/poe/SKILL.md",
    "skills/polymer-general/SKILL.md",
)
_CACHE_PARTS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".venv", "venv"}


def _version_issues(root: Path) -> list[str]:
    issues: list[str] = []
    try:
        pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        manifest = yaml.safe_load((root / "manifest.yaml").read_text(encoding="utf-8"))
        citation = yaml.safe_load((root / "CITATION.cff").read_text(encoding="utf-8"))
        skill = (root / "SKILL.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
        return [f"cannot read version metadata: {exc}"]
    pep440 = __version__.replace("-alpha.", "a")
    if pyproject.get("project", {}).get("version") != pep440:
        issues.append("pyproject version does not match package version")
    if not isinstance(manifest, dict) or manifest.get("version") != __version__:
        issues.append("manifest version does not match package version")
    if not isinstance(citation, dict) or citation.get("version") != __version__:
        issues.append("CITATION version does not match package version")
    if f"version: {__version__}" not in skill:
        issues.append("SKILL frontmatter version does not match package version")
    return issues


def _schema_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for path in sorted((root / "schemas").glob("*.schema.json")):
        try:
            Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            issues.append(f"invalid schema {path.name}: {exc}")
    return issues


def _repository_issues(root: Path) -> list[str]:
    issues = [f"missing required path: {item}" for item in _REQUIRED if not (root / item).exists()]
    for path in root.rglob("*"):
        relative_parts = path.relative_to(root).parts
        if any(part in _CACHE_PARTS for part in relative_parts):
            continue
        if path.is_symlink():
            issues.append(f"repository contains symlink: {path.relative_to(root).as_posix()}")
    readme = root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        for command in ("tsao.cli doctor", "tsao.cli init", "tsao.cli audit"):
            if command not in text:
                issues.append(f"README missing canonical command: {command}")
    return issues


def _has_full_distribution_markers(root: Path) -> bool:
    return all(
        (root / marker).is_file()
        for marker in (
            "reports/COMPLETE_DISTRIBUTION_MANIFEST.tsv",
            "FILE_MANIFEST.tsv",
            "checksums.sha256",
            "SBOM.json",
        )
    )


def diagnose(root: Path, *, profile: str = "auto") -> dict[str, Any]:
    root = Path(root).resolve()
    if profile not in {"auto", "core", "full"}:
        raise ValueError("profile must be auto, core or full")
    active_profile = profile
    if active_profile == "auto":
        active_profile = "full" if _has_full_distribution_markers(root) else "core"
    checks: dict[str, list[str]] = {
        "repository": _repository_issues(root),
        "version": _version_issues(root),
        "schemas": _schema_issues(root),
        "capabilities": capability_contract_issues(root),
    }
    manifest_name = (
        "reports/COMPLETE_DISTRIBUTION_MANIFEST.tsv"
        if active_profile == "full"
        else "reports/SOURCE_CORE_MANIFEST.tsv"
    )
    checks["provenance"] = verify_manifest(root, root / manifest_name)
    issues = [f"{name}: {issue}" for name, values in checks.items() for issue in values]
    return {
        "version": __version__,
        "profile": active_profile,
        "pass": not issues,
        "checks": {
            name: {"pass": not values, "issues": values}
            for name, values in checks.items()
        },
        "issues": issues,
        "scientific_technical_approval": "NOT_EVALUATED",
        "engineering_design_approval": "NOT_EVALUATED",
        "industrial_performance_guarantee": "NOT_EVALUATED",
    }
