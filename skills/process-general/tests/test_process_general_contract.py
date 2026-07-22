from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_and_module_depth():
    manifest = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.2.0"
    assert manifest["technical_approval_status"] == "NOT_EVALUATED"
    modules = sorted((ROOT / "modules").glob("*.md"))
    assert len(modules) == 14
    for path in modules:
        text = path.read_text(encoding="utf-8").casefold()
        for token in (
            "decision question",
            "required inputs",
            "executable workflow",
            "failure modes",
            "exit criteria",
            "external accountable work",
        ):
            assert token in text, f"{path.name}: {token}"


def test_workflow_depth():
    workflows = sorted((ROOT / "workflows").glob("*.md"))
    assert len(workflows) == 6
    for path in workflows:
        text = path.read_text(encoding="utf-8").casefold()
        assert "inputs" in text and "steps" in text and "exit" in text
