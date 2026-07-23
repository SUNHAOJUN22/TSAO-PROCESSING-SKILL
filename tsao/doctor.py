from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from . import __version__
from .capabilities import capability_contract_issues

REQUIRED_PATHS = {
    "README.md", "README.zh-CN.md", "SKILL.md", "manifest.yaml", "pyproject.toml",
    "CITATION.cff", "schemas/project.schema.json", "skills/process-general/SKILL.md",
    "skills/epdm/SKILL.md", "skills/poe/SKILL.md", "skills/polymer-general/SKILL.md",
    "reports/SOURCE_PARITY_ALPHA5.json", "reports/ASSET_PROVENANCE_ALPHA5.tsv",
}
CACHE_PARTS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".pem", ".p12", ".pfx", ".key"}


def _frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path.name} missing YAML frontmatter")
    _, raw, _ = text.split("---", 2)
    value = yaml.safe_load(raw)
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} frontmatter must be an object")
    return value


def diagnose(root: Path) -> dict[str, Any]:
    root = Path(root)
    issues: list[str] = []
    warnings: list[str] = []
    if not root.is_dir() or root.is_symlink():
        return {"pass": False, "root": str(root), "version": __version__, "issues": ["root must be a regular directory"]}
    issues.extend(f"missing required path: {item}" for item in sorted(REQUIRED_PATHS) if not (root / item).exists())
    versions: dict[str, str] = {"python": __version__}
    try:
        pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        manifest = yaml.safe_load((root / "manifest.yaml").read_text(encoding="utf-8"))
        citation = yaml.safe_load((root / "CITATION.cff").read_text(encoding="utf-8"))
        skill = _frontmatter(root / "SKILL.md")
        versions.update({
            "pyproject": pyproject["project"]["version"],
            "manifest": manifest["version"],
            "citation": citation["version"],
            "skill": skill["version"],
        })
        if versions["pyproject"] != __version__.replace("-alpha.", "a"):
            issues.append("pyproject version disagrees with package version")
        if any(versions[key] != __version__ for key in ("manifest", "citation", "skill")):
            issues.append("human-readable version metadata is inconsistent")
        for key in ("scientific_technical_approval", "engineering_design_approval", "customer_qualification", "industrial_performance_guarantee"):
            if manifest.get(key) != "NOT_EVALUATED":
                issues.append(f"manifest must keep {key}=NOT_EVALUATED")
    except (OSError, UnicodeError, KeyError, TypeError, ValueError, tomllib.TOMLDecodeError, yaml.YAMLError) as exc:
        issues.append(f"cannot validate version metadata: {exc}")
    for path in sorted((root / "schemas").glob("*.schema.json")):
        try:
            Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            issues.append(f"invalid JSON Schema: {path.name}: {exc}")
    cache_count = 0
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in CACHE_PARTS for part in relative.parts):
            cache_count += int(path.is_file())
            continue
        if path.is_symlink():
            issues.append(f"symlink in source tree: {relative.as_posix()}")
        if path.is_file() and path.suffix.casefold() in FORBIDDEN_SUFFIXES:
            issues.append(f"forbidden source file: {relative.as_posix()}")
    if cache_count:
        warnings.append(f"{cache_count} runtime cache files ignored; release builder excludes them")
    issues.extend(capability_contract_issues(root))
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    for token in ("tsao doctor", "tsao init", "tsao audit", "NOT_EVALUATED"):
        if token not in readme:
            issues.append(f"README missing primary workflow token: {token}")
    return {
        "pass": not issues,
        "root": str(root),
        "version": __version__,
        "versions": versions,
        "issues": sorted(set(issues)),
        "warnings": warnings,
        "artifact_software_qualification": "PASS" if not issues else "FAIL",
        "scientific_technical_approval": "NOT_EVALUATED",
        "engineering_design_approval": "NOT_EVALUATED",
        "customer_qualification": "NOT_EVALUATED",
        "industrial_performance_guarantee": "NOT_EVALUATED",
    }
