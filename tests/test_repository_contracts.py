from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from urllib.parse import unquote

import pytest
import yaml
from jsonschema import Draft202012Validator

import tsao

ROOT = Path(__file__).resolve().parents[1]
CACHE_PARTS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache"}
REQUIRED = {
    "README.md", "README.zh-CN.md", "SKILL.md", "ARCHITECTURE.md", "ROADMAP.md",
    "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "GOVERNANCE.md",
    "CITATION.cff", "LICENSE", "NOTICE.md", "manifest.yaml", "pyproject.toml",
    "scripts/run_ci.py", "tsao/doctor.py", "reports/SOURCE_PARITY_ALPHA5.json",
    "reports/ASSET_PROVENANCE_ALPHA5.tsv", "skills/process-general/SKILL.md",
    "skills/epdm/SKILL.md", "skills/poe/SKILL.md", "skills/polymer-general/SKILL.md",
}


def source_paths(pattern: str):
    return (path for path in ROOT.rglob(pattern) if not any(part in CACHE_PARTS for part in path.relative_to(ROOT).parts))


def test_required_repository_paths_exist():
    assert sorted(path for path in REQUIRED if not (ROOT / path).exists()) == []


def test_json_yaml_and_schemas_parse():
    for path in sorted(source_paths("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
    for pattern in ("*.yaml", "*.yml"):
        for path in sorted(source_paths(pattern)):
            yaml.safe_load(path.read_text(encoding="utf-8"))
    for path in sorted((ROOT / "schemas").glob("*.schema.json")):
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_version_metadata_is_consistent():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert pyproject["project"]["version"] == "0.1.0a5"
    assert tsao.__version__ == "0.1.0-alpha.5"
    assert manifest["version"] == tsao.__version__
    assert citation["version"] == tsao.__version__
    assert f"version: {tsao.__version__}" in skill
    assert manifest["artifact_software_qualification"] == "NOT_EVALUATED"
    assert "tsao doctor" in (ROOT / "README.md").read_text(encoding="utf-8")


def test_relative_markdown_links_resolve():
    failures = []
    link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for path in sorted(source_paths("*.md")):
        for raw_target in link_re.findall(path.read_text(encoding="utf-8")):
            target = raw_target.strip().strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not target or any(character in target for character in "{}*|"):
                continue
            resolved = (path.parent / target).resolve(strict=False)
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                failures.append(f"{path.relative_to(ROOT)} escapes root: {raw_target}")
                continue
            if not resolved.exists():
                failures.append(f"{path.relative_to(ROOT)} missing: {raw_target}")
    assert failures == []


@pytest.mark.parametrize("suffix", [".pyc", ".pyo", ".pem", ".p12", ".pfx", ".key"])
def test_no_forbidden_source_files(suffix: str):
    assert list(source_paths(f"*{suffix}")) == []
