from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

from tsao.distribution_policy import (
    BLOCKED_STATUS,
    evaluate_public_distribution,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_public_distribution_policy.py"


def _load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("distribution_policy_cli", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_registry(root: Path) -> None:
    (root / "source_asset_registry.part01.json").write_text(
        json.dumps(
            {
                "assets": [
                    {
                        "asset_id": "controlled-1",
                        "confidentiality": "CONTROLLED_INTERNAL",
                        "evidence_class": "CONTROLLED_HISTORICAL_EVIDENCE",
                        "license_scope": "PROJECT_CONTROLLED",
                        "public_fixture_eligible": False,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (root / "source_asset_registry.json").write_text(
        json.dumps(
            {
                "expected_asset_count": 1,
                "asset_count": 1,
                "asset_files": ["source_asset_registry.part01.json"],
            }
        ),
        encoding="utf-8",
    )


def test_compatibility_cli_delegates_to_the_canonical_policy(tmp_path: Path) -> None:
    module = _load_script()
    assert module.evaluate is evaluate_public_distribution
    _write_registry(tmp_path)
    result = module.evaluate(tmp_path, ["wheel", "source-snapshot"])
    assert result["status"] == BLOCKED_STATUS
    assert result["pass"] is False
    assert result["blocked_surfaces"] == ["source-snapshot", "wheel"]


def test_compatibility_cli_contains_no_second_policy_engine() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert "import hashlib" not in source
    assert "json.loads" not in source
    assert "def evaluate(" not in source
    assert "evaluate_public_distribution" in source
