from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_public_parity_ledger_is_truthful():
    rows = list(csv.DictReader((ROOT / "reports/ASSET_PROVENANCE_ALPHA5.tsv").open(encoding="utf-8"), delimiter="\t"))
    assert len(rows) >= 5
    assert len(rows) == len({row["path"] for row in rows})
    assert all(len(row["sha256"]) == 64 for row in rows)
    assert {"TSAO-master", "EPDM-v9", "SJTU-POE", "SJTU-universal-polymer"} <= {row["asset_family"] for row in rows}
    report = json.loads((ROOT / "reports/SOURCE_PARITY_ALPHA5.json").read_text(encoding="utf-8"))
    assert report["version"] == "0.1.0-alpha.5"
    assert report["complete_distribution"]["tests"] == 472
    assert report["public_repository_sync"]["full_parity_verified"] is False
    assert report["technical_approval_status"] == "NOT_EVALUATED"
