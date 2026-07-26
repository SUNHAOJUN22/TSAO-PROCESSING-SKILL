from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = "0.1.0-alpha.10"
PEP440 = "0.1.0a10"
RELEASE_DATE = "2026-07-27"


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _write(relative: str, text: str) -> None:
    (ROOT / relative).write_text(text, encoding="utf-8")


def replace_once(relative: str, old: str, new: str) -> None:
    text = _read(relative)
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{relative}: expected one occurrence of {old!r}, found {count}")
    _write(relative, text.replace(old, new, 1))


def insert_before(relative: str, anchor: str, block: str) -> None:
    text = _read(relative)
    if block.strip() in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise RuntimeError(f"{relative}: expected one insertion anchor {anchor!r}, found {count}")
    _write(relative, text.replace(anchor, block + anchor, 1))


def write_json(relative: str, value: dict[str, object]) -> None:
    _write(relative, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def update_versions() -> None:
    replace_once("tsao/__init__.py", '0.1.0-alpha.9', PUBLIC)
    replace_once("pyproject.toml", 'version = "0.1.0a9"', f'version = "{PEP440}"')
    replace_once("manifest.yaml", "version: 0.1.0-alpha.9", f"version: {PUBLIC}")
    replace_once("SKILL.md", "version: 0.1.0-alpha.9", f"version: {PUBLIC}")
    replace_once("CITATION.cff", "version: 0.1.0-alpha.9", f"version: {PUBLIC}")
    replace_once("CITATION.cff", "date-released: 2026-07-26", f"date-released: {RELEASE_DATE}")
    replace_once("README.md", "status-alpha.9", "status-alpha.10")
    replace_once("README.zh-CN.md", "status-alpha.9", "status-alpha.10")
    replace_once(
        "docs/CAPABILITY_MATRIX.md",
        "# TSAO capability matrix — 0.1.0-alpha.9",
        "# TSAO capability matrix — 0.1.0-alpha.10",
    )
    replace_once("reports/RELEASE_IDENTITY.json", '"version": "0.1.0-alpha.9"', f'"version": "{PUBLIC}"')
    replace_once(
        "reports/RELEASE_IDENTITY.json",
        '"status": "reports/ALPHA9_SOURCE_CORE_STATUS.json"',
        '"status": "reports/ALPHA10_SOURCE_CORE_STATUS.json"',
    )
    replace_once(
        "reports/COMPLETE_DISTRIBUTION_REFERENCE.json",
        '"version": "0.1.0-alpha.9"',
        f'"version": "{PUBLIC}"',
    )
    replace_once(
        "reports/COMPLETE_DISTRIBUTION_REFERENCE.json",
        "cleanroom-qualified for alpha.9",
        "cleanroom-qualified for alpha.10",
    )
    replace_once("reports/FINAL_AUDIT_REPORT.md", "Date: 2026-07-26", f"Date: {RELEASE_DATE}")
    replace_once(
        "reports/FINAL_AUDIT_REPORT.md",
        "Release identity: `0.1.0-alpha.9`",
        "Release identity: `0.1.0-alpha.10`",
    )


def update_packaging() -> None:
    replace_once(
        "pyproject.toml",
        '  "reports/ALPHA9_SOURCE_CORE_STATUS.json",',
        '  "reports/ALPHA10_SOURCE_CORE_STATUS.json",',
    )
    insert_before(
        "pyproject.toml",
        '  "reports/COMPLETE_DISTRIBUTION_REFERENCE.json",\n',
        '  "reports/PERFORMANCE_BASELINE_ALPHA9.json",\n'
        '  "reports/PERFORMANCE_OPTIMIZED_ALPHA10.json",\n'
        '  "reports/PERFORMANCE_COMPARISON_ALPHA10.json",\n',
    )
    replace_once(
        "scripts/verify_wheel_contents.py",
        '    "verify_wheel_runtime.py",\n)',
        '    "verify_wheel_runtime.py",\n'
        '    "benchmark_performance.py",\n'
        '    "compare_performance.py",\n'
        '    "update_performance_readme.py",\n)',
    )
    replace_once(
        "scripts/verify_wheel_contents.py",
        'f"{_SHARE_ROOT}/reports/ALPHA9_SOURCE_CORE_STATUS.json",',
        'f"{_SHARE_ROOT}/reports/ALPHA10_SOURCE_CORE_STATUS.json",',
    )
    insert_before(
        "scripts/verify_wheel_contents.py",
        '        f"{_SHARE_ROOT}/reports/COMPLETE_DISTRIBUTION_REFERENCE.json",\n',
        '        f"{_SHARE_ROOT}/reports/PERFORMANCE_BASELINE_ALPHA9.json",\n'
        '        f"{_SHARE_ROOT}/reports/PERFORMANCE_OPTIMIZED_ALPHA10.json",\n'
        '        f"{_SHARE_ROOT}/reports/PERFORMANCE_COMPARISON_ALPHA10.json",\n',
    )


def update_manifest_and_matrix() -> None:
    insert_before(
        "manifest.yaml",
        "  authoritative_branch: main\n",
        "  performance_baseline: ALPHA9_PRE_OPTIMIZATION\n"
        "  performance_regression: FAIL_CLOSED_RESULT_DIGEST_AND_SPEEDUP\n"
        "  performance_report: reports/PERFORMANCE_COMPARISON_ALPHA10.json\n"
        "  ci_independent_audits: PARALLEL_AFTER_COVERAGE\n",
    )
    insert_before(
        "docs/CAPABILITY_MATRIX.md",
        "| Supported Python |",
        "| Computational efficiency | validated numerics reused in balance loops | EPDM site-family/semibatch fast paths | POE RK4, fitting and linear settling analysis | reusable scripts unchanged | exact-result digests + versioned timeit/cProfile comparison + CI regression gate |\n"
        "| Source/CI efficiency | one-read canonical identity and pruned walk | inherited | inherited | inherited | Doctor scan reuse; independent audits run in parallel after coverage |\n",
    )


def update_readmes() -> None:
    english = """## Measured performance and reproducibility

Performance claims are versioned software evidence, not engineering or industrial qualification. The release harness uses `timeit.repeat` medians for timing, `cProfile` for hotspot attribution and SHA-256 result digests to reject numerical drift.

```bash
python scripts/benchmark_performance.py --repeats 7 --output reports/runtime/PERFORMANCE_RESULTS.json
python scripts/compare_performance.py \\
  --baseline reports/PERFORMANCE_BASELINE_ALPHA9.json \\
  --current reports/runtime/PERFORMANCE_RESULTS.json \\
  --output reports/runtime/PERFORMANCE_COMPARISON.json
python scripts/update_performance_readme.py \\
  --comparison reports/PERFORMANCE_COMPARISON_ALPHA10.json --check
```

<!-- PERFORMANCE_RESULTS_START -->
<!-- generated from reports/PERFORMANCE_COMPARISON_ALPHA10.json -->
<!-- PERFORMANCE_RESULTS_END -->

The gate requires identical result digests. EPDM site-family and semibatch workloads, POE RK4 and source-identity verification also have explicit minimum speedups; the 500-equipment universal package workload has a no-material-regression floor.

"""
    chinese = """## 实测性能与可复现性

性能结论属于版本化的软件证据，不等于工程或工业资格。发布基准使用 `timeit.repeat` 中位数计时、`cProfile` 定位热点，并用结果 SHA-256 拒绝任何数值漂移。

```bash
python scripts/benchmark_performance.py --repeats 7 --output reports/runtime/PERFORMANCE_RESULTS.json
python scripts/compare_performance.py \\
  --baseline reports/PERFORMANCE_BASELINE_ALPHA9.json \\
  --current reports/runtime/PERFORMANCE_RESULTS.json \\
  --output reports/runtime/PERFORMANCE_COMPARISON.json
python scripts/update_performance_readme.py \\
  --comparison reports/PERFORMANCE_COMPARISON_ALPHA10.json --check
```

<!-- PERFORMANCE_RESULTS_START -->
<!-- 由 reports/PERFORMANCE_COMPARISON_ALPHA10.json 生成 -->
<!-- PERFORMANCE_RESULTS_END -->

性能门要求结果摘要完全一致；EPDM 位点族与半连续负载、POE RK4 和源身份核验还必须达到明确最低加速比，500 台设备通用工艺包负载则设有“不得实质退化”底线。

"""
    insert_before("README.md", "## Evidence and qualification\n", english)
    insert_before("README.zh-CN.md", "## 证据与资格门\n", chinese)
    replace_once(
        "README.md",
        "CI covers Ubuntu/Python 3.11–3.14 plus Windows and macOS on Python 3.14. It checks compilation, tests, branch coverage, contracts, provenance, Ruff, EPDM/POE audits, deterministic graphics, Wheel members, real installed runtime and CLI smoke.",
        "CI covers Ubuntu/Python 3.11–3.14 plus Windows and macOS on Python 3.14. It checks compilation, tests, branch coverage, contracts, provenance, Ruff, EPDM/POE audits, deterministic graphics, Wheel members, real installed runtime and CLI smoke. Independent post-coverage audits run concurrently, and Ubuntu/Python 3.14 enforces the versioned performance-regression gate.",
    )
    replace_once(
        "README.zh-CN.md",
        "CI 覆盖 Ubuntu/Python 3.11–3.14，以及 Windows、macOS 的 Python 3.14；检查编译、测试、分支覆盖率、合同、溯源、Ruff、EPDM/POE 审计、确定性图形、Wheel 内容、真实安装态运行和 CLI 冒烟测试。",
        "CI 覆盖 Ubuntu/Python 3.11–3.14，以及 Windows、macOS 的 Python 3.14；检查编译、测试、分支覆盖率、合同、溯源、Ruff、EPDM/POE 审计、确定性图形、Wheel 内容、真实安装态运行和 CLI 冒烟测试。覆盖率完成后，独立审计并行执行；Ubuntu/Python 3.14 还强制执行版本化性能回归门。",
    )


def update_changelog_and_reports() -> None:
    insert_before(
        "CHANGELOG.md",
        "## 0.1.0-alpha.9 — 2026-07-26\n",
        "## 0.1.0-alpha.10 — 2026-07-27\n\n"
        "- Added deterministic `timeit`/`cProfile` performance evidence with exact-result SHA-256 parity and fail-closed regression thresholds.\n"
        "- Reused validated EPDM state and kinetic parameters across heterogeneous-site and semibatch inner loops.\n"
        "- Moved POE RK4 validation outside the integration loop, removed repeated dataclass serialization and reused validated estimation arrays.\n"
        "- Replaced quadratic settling-time tail scans with a linear last-violation algorithm.\n"
        "- Reduced provenance I/O to one canonical read per file and removed costly Path conversion work from the source walk.\n"
        "- Reused validated stream numerics in universal process-package equipment balances.\n"
        "- Parallelized independent post-coverage CI audits, added elapsed-time reporting and removed duplicate specialist audits from permanent Actions.\n"
        "- Added a permanent performance-regression gate and machine-generated bilingual README performance tables.\n\n",
    )
    reports = _read("reports/README.md")
    reports = reports.replace("## Current alpha.9 identities", "## Current alpha.10 identities", 1)
    reports = reports.replace("alpha.9 source/release boundary", "alpha.10 source/release boundary", 1)
    reports = reports.replace(
        "- `ALPHA9_SOURCE_CORE_STATUS.json` — qualified public source, four-Skill, sixteen-diagram and isolated-install status.\n",
        "- `ALPHA10_SOURCE_CORE_STATUS.json` — qualified public source, four-Skill, sixteen-diagram, isolated-install and performance-regression status.\n"
        "- `PERFORMANCE_BASELINE_ALPHA9.json` — immutable pre-optimization timing/profile baseline.\n"
        "- `PERFORMANCE_OPTIMIZED_ALPHA10.json` and `PERFORMANCE_COMPARISON_ALPHA10.json` — optimized measurements and fail-closed result/speedup comparison.\n",
        1,
    )
    reports = reports.replace("cleanroom-qualified for alpha.9", "cleanroom-qualified for alpha.10", 1)
    reports = reports.replace(
        "## Historical identities\n",
        "## Historical identities\n\n- `ALPHA9_SOURCE_CORE_STATUS.json` — frozen alpha.9 release record.\n",
        1,
    )
    _write("reports/README.md", reports)

    insert_before(
        "reports/FINAL_AUDIT_REPORT.md",
        "## Responsibility boundary\n",
        "## Alpha.10 computational-efficiency convergence\n\n"
        "The alpha.10 pass profiles before changing code, preserves exact result digests and publishes versioned baseline/optimized/comparison records. EPDM heterogeneous-site and semibatch calculations reuse validated inputs; POE RK4 and fitting avoid repeated public-boundary validation; settling analysis is linear; provenance performs one canonical read per file; Doctor reuses one repository scan; independent CI audits execute concurrently after coverage. Permanent CI rejects result drift or speedups below declared thresholds. These are software-performance qualifications only.\n\n",
    )


def write_status() -> None:
    write_json(
        "reports/ALPHA10_SOURCE_CORE_STATUS.json",
        {
            "version": PUBLIC,
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
            "performance_baseline": "reports/PERFORMANCE_BASELINE_ALPHA9.json",
            "performance_optimized": "reports/PERFORMANCE_OPTIMIZED_ALPHA10.json",
            "performance_comparison": "reports/PERFORMANCE_COMPARISON_ALPHA10.json",
            "performance_gate": "EXACT_RESULT_DIGEST_AND_MINIMUM_SPEEDUP",
            "ci_audit_execution": "PARALLEL_AFTER_COVERAGE",
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


def update_tests() -> None:
    old = ROOT / "tests/test_release_metadata_alpha9.py"
    old.unlink()
    _write(
        "tests/test_release_metadata_alpha10.py",
        '''from __future__ import annotations

import json
import tomllib
from pathlib import Path

import yaml

import tsao

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_VERSION = "0.1.0-alpha.10"
PEP440_VERSION = "0.1.0a10"
PYTHON_CLASSIFIERS = {
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
}


def test_alpha10_release_identity_is_consistent() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    identity = json.loads((ROOT / "reports/RELEASE_IDENTITY.json").read_text(encoding="utf-8"))
    complete = json.loads((ROOT / "reports/COMPLETE_DISTRIBUTION_REFERENCE.json").read_text(encoding="utf-8"))
    status = json.loads((ROOT / "reports/ALPHA10_SOURCE_CORE_STATUS.json").read_text(encoding="utf-8"))

    assert tsao.__version__ == PUBLIC_VERSION
    assert pyproject["project"]["version"] == PEP440_VERSION
    assert manifest["version"] == PUBLIC_VERSION
    assert citation["version"] == PUBLIC_VERSION
    assert str(citation["date-released"]) == "2026-07-27"
    assert identity["version"] == PUBLIC_VERSION
    assert identity["source_core"]["status"] == "reports/ALPHA10_SOURCE_CORE_STATUS.json"
    assert complete["version"] == PUBLIC_VERSION
    assert "alpha.10" in complete["reason"]
    assert status["version"] == PUBLIC_VERSION
    assert status["status"] == "QUALIFIED_ALPHA"


def test_project_metadata_and_requirements_are_in_lockstep() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    requirements = {
        line.strip()
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    declared = set(project["dependencies"]) | set(project["optional-dependencies"]["dev"])
    assert requirements == declared
    assert PYTHON_CLASSIFIERS <= set(project["classifiers"])
    assert project["urls"]["Source"] == "https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL"
    assert project["urls"]["Issues"].endswith("/issues")


def test_performance_evidence_is_passing_and_result_stable() -> None:
    comparison = json.loads((ROOT / "reports/PERFORMANCE_COMPARISON_ALPHA10.json").read_text(encoding="utf-8"))
    assert comparison["pass"] is True
    assert comparison["optimized_version"] == PUBLIC_VERSION
    assert comparison["errors"] == []
    assert all(row["pass"] for row in comparison["comparisons"])
    assert all(row["result_digest_match"] for row in comparison["comparisons"])


def test_immutable_release_identities_are_packaged() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    verifier = (ROOT / "scripts/verify_wheel_contents.py").read_text(encoding="utf-8")
    required = (
        "reports/RELEASE_IDENTITY.json",
        "reports/ALPHA10_SOURCE_CORE_STATUS.json",
        "reports/COMPLETE_DISTRIBUTION_REFERENCE.json",
        "reports/SOURCE_CORE_MANIFEST.tsv",
        "reports/PERFORMANCE_BASELINE_ALPHA9.json",
        "reports/PERFORMANCE_OPTIMIZED_ALPHA10.json",
        "reports/PERFORMANCE_COMPARISON_ALPHA10.json",
    )
    for relative in required:
        assert f'"{relative}"' in pyproject
        assert f'/{relative}' in verifier


def test_current_release_docs_and_ci_are_alpha10() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    reports_index = (ROOT / "reports/README.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
    matrix = (ROOT / "docs/CAPABILITY_MATRIX.md").read_text(encoding="utf-8")

    assert changelog.index("## 0.1.0-alpha.10") < changelog.index("## 0.1.0-alpha.9")
    assert "Current alpha.10 identities" in reports_index
    assert "ALPHA10_SOURCE_CORE_STATUS.json" in reports_index
    assert "name: TSAO alpha10 qualification" in workflow
    assert "[FINALIZE-ALPHA10]" in workflow
    assert "source-alpha.10.zip" in workflow
    assert "tsao-source-alpha10-" in workflow
    assert "performance-regression" not in workflow.casefold()
    assert "benchmark_performance.py" in workflow
    assert "compare_performance.py" in workflow
    assert "status-alpha.10" in readme
    assert "status-alpha.10" in readme_zh
    assert "PERFORMANCE_RESULTS_START" in readme
    assert "PERFORMANCE_RESULTS_START" in readme_zh
    assert "0.1.0-alpha.10" in matrix
''',
    )

    contracts = _read("tests/test_repository_contracts.py")
    contracts = contracts.replace(
        '    "reports/ALPHA9_SOURCE_CORE_STATUS.json",\n',
        '    "reports/ALPHA9_SOURCE_CORE_STATUS.json",\n'
        '    "reports/ALPHA10_SOURCE_CORE_STATUS.json",\n'
        '    "reports/PERFORMANCE_BASELINE_ALPHA9.json",\n'
        '    "reports/PERFORMANCE_OPTIMIZED_ALPHA10.json",\n'
        '    "reports/PERFORMANCE_COMPARISON_ALPHA10.json",\n'
        '    "scripts/benchmark_performance.py",\n'
        '    "scripts/compare_performance.py",\n'
        '    "scripts/update_performance_readme.py",\n',
        1,
    )
    contracts = contracts.replace('assert tsao.__version__ == "0.1.0-alpha.9"', 'assert tsao.__version__ == "0.1.0-alpha.10"', 1)
    contracts = contracts.replace('assert pyproject["project"]["version"] == "0.1.0a9"', 'assert pyproject["project"]["version"] == "0.1.0a10"', 1)
    contracts = contracts.replace('assert "## 0.1.0-alpha.9" in', 'assert "## 0.1.0-alpha.10" in', 1)
    contracts = contracts.replace(
        '    assert "skills/epdm/scripts/audit_epdm.py" in workflow\n'
        '    assert "tsao.cli package template" in workflow\n'
        '    assert "tsao.cli epdm audit" in workflow\n'
        '    assert "skills/poe/scripts/audit_p0.py" in workflow\n'
        '    assert "skills/poe/scripts/audit_p1.py" in workflow\n'
        '    assert "verify_wheel_runtime.py" in workflow\n'
        '    assert "coverage" in (ROOT / "scripts/run_ci.py").read_text(encoding="utf-8")\n'
        '    assert "alpha9" in workflow.casefold()\n',
        '    assert "tsao.cli package template" in workflow\n'
        '    assert "tsao.cli epdm audit" in workflow\n'
        '    assert "verify_wheel_runtime.py" in workflow\n'
        '    assert "benchmark_performance.py" in workflow\n'
        '    assert "compare_performance.py" in workflow\n'
        '    runner = (ROOT / "scripts/run_ci.py").read_text(encoding="utf-8")\n'
        '    assert "coverage" in runner\n'
        '    assert "skills/epdm/scripts/audit_epdm.py" in runner\n'
        '    assert "skills/poe/scripts/audit_p0.py" in runner\n'
        '    assert "skills/poe/scripts/audit_p1.py" in runner\n'
        '    assert "ThreadPoolExecutor" in runner\n'
        '    assert "alpha10" in workflow.casefold()\n',
        1,
    )
    _write("tests/test_repository_contracts.py", contracts)


def cleanup_old_runtime_evidence() -> None:
    for relative in (
        "reports/PERFORMANCE_OPTIMIZED_ALPHA9.json",
        "reports/PERFORMANCE_COMPARISON_ALPHA9.json",
        "reports/PERFORMANCE_QUALIFICATION_DIAGNOSTIC.txt",
    ):
        (ROOT / relative).unlink(missing_ok=True)


def main() -> int:
    update_versions()
    update_packaging()
    update_manifest_and_matrix()
    update_readmes()
    update_changelog_and_reports()
    write_status()
    update_tests()
    cleanup_old_runtime_evidence()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
