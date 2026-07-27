from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_VERSION = "0.1.0-alpha.11"
PEP440_VERSION = "0.1.0a11"
RELEASE_DATE = "2026-07-27"


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _write(relative: str, text: str) -> None:
    (ROOT / relative).write_text(text, encoding="utf-8")


def _replace(relative: str, old: str, new: str, *, count: int = 1) -> None:
    text = _read(relative)
    actual = text.count(old)
    if actual != count:
        raise SystemExit(
            f"{relative}: expected {count} occurrence(s) of {old!r}, found {actual}"
        )
    _write(relative, text.replace(old, new, count))


def _replace_all(relative: str, old: str, new: str, *, minimum: int = 1) -> None:
    text = _read(relative)
    actual = text.count(old)
    if actual < minimum:
        raise SystemExit(f"{relative}: expected at least {minimum} occurrence(s) of {old!r}")
    _write(relative, text.replace(old, new))


def _load_json(relative: str) -> dict[str, object]:
    data = json.loads(_read(relative))
    if not isinstance(data, dict):
        raise SystemExit(f"{relative}: JSON root must be an object")
    return data


def _write_json(relative: str, data: dict[str, object]) -> None:
    _write(relative, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def _update_versions() -> None:
    _replace("tsao/__init__.py", '0.1.0-alpha.10', PUBLIC_VERSION)
    _replace("pyproject.toml", 'version = "0.1.0a10"', f'version = "{PEP440_VERSION}"')
    _replace("SKILL.md", 'version: 0.1.0-alpha.10', f'version: {PUBLIC_VERSION}')
    _replace("CITATION.cff", 'version: 0.1.0-alpha.10', f'version: {PUBLIC_VERSION}')
    citation = _read("CITATION.cff")
    if f"date-released: {RELEASE_DATE}" not in citation:
        raise SystemExit("CITATION.cff release date is not the expected alpha11 date")


def _update_manifest() -> None:
    _replace("manifest.yaml", 'version: 0.1.0-alpha.10', f'version: {PUBLIC_VERSION}')
    _replace("manifest.yaml", 'readme_assets: 16_OF_16', 'readme_assets: 18_OF_18')
    _replace(
        "manifest.yaml",
        "  performance_baseline: ALPHA9_PRE_OPTIMIZATION\n"
        "  performance_regression: FAIL_CLOSED_RESULT_DIGEST_AND_SPEEDUP\n"
        "  performance_report: reports/PERFORMANCE_COMPARISON_ALPHA10.json\n"
        "  ci_independent_audits: PARALLEL_AFTER_COVERAGE\n",
        "  performance_baseline: reports/PERFORMANCE_BASELINE_ALPHA10_EXTENDED.json\n"
        "  performance_regression: FAIL_CLOSED_EXACT_TOLERANCE_MEMORY_AND_SCALE_GATES\n"
        "  performance_report: reports/PERFORMANCE_COMPARISON_ALPHA11.json\n"
        "  performance_benchmark_count: 20\n"
        "  epdm_batch_screening: NUMPY_BROADCAST_REFERENCE\n"
        "  epdm_semibatch_trajectory: ONCE_VALIDATED_FULL_HISTORY\n"
        "  poe_terminal_execution: NO_HISTORY_ALLOCATION_OPTION\n"
        "  ci_independent_audits: PARALLEL_AFTER_COVERAGE\n",
    )


def _update_packaging() -> None:
    _replace(
        "pyproject.toml",
        '  "reports/ALPHA10_SOURCE_CORE_STATUS.json",\n',
        '  "reports/ALPHA10_SOURCE_CORE_STATUS.json",\n'
        '  "reports/ALPHA11_SOURCE_CORE_STATUS.json",\n',
    )
    _replace(
        "pyproject.toml",
        '  "reports/PERFORMANCE_COMPARISON_ALPHA10.json",\n',
        '  "reports/PERFORMANCE_COMPARISON_ALPHA10.json",\n'
        '  "reports/PERFORMANCE_BASELINE_ALPHA10_EXTENDED.json",\n'
        '  "reports/PERFORMANCE_OPTIMIZED_ALPHA11.json",\n'
        '  "reports/PERFORMANCE_COMPARISON_ALPHA11.json",\n'
        '  "reports/PERFORMANCE_TECHNOLOGY_REVIEW.md",\n'
        '  "reports/PERFORMANCE_OPTIMIZATION_PLAN.md",\n',
    )

    verifier = _read("scripts/verify_wheel_contents.py")
    verifier = verifier.replace(
        '    "skills/epdm/core.py",\n',
        '    "skills/epdm/core.py",\n    "skills/epdm/batch.py",\n',
        1,
    )
    verifier = verifier.replace(
        '    "control-safety-cause-effect.svg",\n',
        '    "batch-parameter-scan.svg",\n    "control-safety-cause-effect.svg",\n',
        1,
    )
    verifier = verifier.replace(
        '    "process-package-data-model.svg",\n',
        '    "process-package-data-model.svg",\n    "performance-regression-gate.svg",\n',
        1,
    )
    verifier = verifier.replace(
        '    "generate_decision_readme_assets.py",\n',
        '    "generate_decision_readme_assets.py",\n'
        '    "generate_performance_readme_assets.py",\n',
        1,
    )
    verifier = verifier.replace(
        '    "benchmark_performance.py",\n',
        '    "benchmark_performance.py",\n'
        '    "benchmark_performance_v2.py",\n',
        1,
    )
    verifier = verifier.replace(
        '    "compare_performance.py",\n',
        '    "compare_performance.py",\n'
        '    "compare_performance_v2.py",\n',
        1,
    )
    verifier = verifier.replace(
        '        f"{_SHARE_ROOT}/reports/ALPHA10_SOURCE_CORE_STATUS.json",\n',
        '        f"{_SHARE_ROOT}/reports/ALPHA11_SOURCE_CORE_STATUS.json",\n'
        '        f"{_SHARE_ROOT}/reports/PERFORMANCE_BASELINE_ALPHA10_EXTENDED.json",\n'
        '        f"{_SHARE_ROOT}/reports/PERFORMANCE_OPTIMIZED_ALPHA11.json",\n'
        '        f"{_SHARE_ROOT}/reports/PERFORMANCE_COMPARISON_ALPHA11.json",\n'
        '        f"{_SHARE_ROOT}/reports/PERFORMANCE_TECHNOLOGY_REVIEW.md",\n'
        '        f"{_SHARE_ROOT}/reports/PERFORMANCE_OPTIMIZATION_PLAN.md",\n',
        1,
    )
    for token in (
        '"skills/epdm/batch.py"',
        '"batch-parameter-scan.svg"',
        '"performance-regression-gate.svg"',
        '"benchmark_performance_v2.py"',
        '"compare_performance_v2.py"',
        '"generate_performance_readme_assets.py"',
        'ALPHA11_SOURCE_CORE_STATUS.json',
        'PERFORMANCE_COMPARISON_ALPHA11.json',
    ):
        if token not in verifier:
            raise SystemExit(f"Wheel verifier transformation missed {token}")
    _write("scripts/verify_wheel_contents.py", verifier)

    _replace("tsao/skillpacks.py", 'README_ASSET_MINIMUM = 16', 'README_ASSET_MINIMUM = 18')
    _replace(
        "scripts/verify_wheel_runtime.py",
        'if skillpacks.get("readme_svg_assets", 0) < 16:\n'
        '            errors.append(f"{label} does not contain all sixteen README assets")',
        'if skillpacks.get("readme_svg_assets", 0) < 18:\n'
        '            errors.append(f"{label} does not contain all eighteen README assets")',
    )
    _replace_all(
        "tests/test_wheel_contract.py",
        '"readme_svg_assets": 16',
        '"readme_svg_assets": 18',
    )


def _update_readmes() -> None:
    for relative in ("README.md", "README.zh-CN.md"):
        _replace(relative, 'status-alpha.10', 'status-alpha.11')

    _replace(
        "README.md",
        "The inventory fails closed unless the four Skills, 14 general-process modules, 6 workflows, 6 polymer-general scripts and at least 16 README diagrams are present.",
        "The inventory fails closed unless the four Skills, 14 general-process modules, 6 workflows, 6 polymer-general scripts and all 18 README diagrams are present.",
    )
    _replace(
        "README.zh-CN.md",
        "四条 Skill、14 个通用模块、6 条工作流、6 个聚合物通用脚本或至少 16 幅 README 图中缺少任何一项，库存检查都会失败关闭。",
        "四条 Skill、14 个通用模块、6 条工作流、6 个聚合物通用脚本或全部 18 幅 README 图中缺少任何一项，库存检查都会失败关闭。",
    )

    _replace(
        "README.md",
        "![EPDM reactor-mode decision map](docs/assets/readme/epdm-reactor-mode-map.svg)",
        "### Batch screening and long trajectories\n\n"
        "![EPDM broadcast parameter-scan pipeline](docs/assets/readme/batch-parameter-scan.svg)\n\n"
        "`batch_pseudo_first_order_screening` broadcasts temperature, residence time, active-site concentration and propagation multipliers without Python-loop dispatch. `semibatch_trajectory` validates the model boundary once while preserving the complete step history, and POE offers an explicitly named terminal-only RK4 path when online loops do not need history allocation. Scalar APIs remain the reference parity anchors.\n\n"
        "![EPDM reactor-mode decision map](docs/assets/readme/epdm-reactor-mode-map.svg)",
    )
    _replace(
        "README.zh-CN.md",
        "![EPDM 反应器模式决策图](docs/assets/readme/epdm-reactor-mode-map.svg)",
        "### 批量筛选与长轨迹\n\n"
        "![EPDM 广播参数扫描流水线](docs/assets/readme/batch-parameter-scan.svg)\n\n"
        "`batch_pseudo_first_order_screening` 对温度、停留时间、活性位浓度和增长速率倍数执行真正的广播计算，不经过 Python 情景循环；`semibatch_trajectory` 只在模型边界校验一次，同时保留完整步进历史；POE 在在线循环不需要历史时提供具名的仅终态 RK4 路径。标量 API 继续作为等价性锚点。\n\n"
        "![EPDM 反应器模式决策图](docs/assets/readme/epdm-reactor-mode-map.svg)",
    )

    _replace(
        "README.md",
        "## Measured performance and reproducibility\n\nPerformance claims",
        "## Measured performance and reproducibility\n\n"
        "![Fail-closed performance regression gate](docs/assets/readme/performance-regression-gate.svg)\n\n"
        "Performance claims",
    )
    _replace(
        "README.zh-CN.md",
        "## 实测性能与可复现性\n\n性能结论",
        "## 实测性能与可复现性\n\n"
        "![失败关闭性能回归门](docs/assets/readme/performance-regression-gate.svg)\n\n"
        "性能结论",
    )

    _replace(
        "README.md",
        "python scripts/benchmark_performance.py --repeats 7 --output reports/runtime/PERFORMANCE_RESULTS.json\n"
        "python scripts/compare_performance.py \\\n"
        "  --baseline reports/PERFORMANCE_BASELINE_ALPHA9.json \\\n"
        "  --current reports/runtime/PERFORMANCE_RESULTS.json \\\n"
        "  --output reports/runtime/PERFORMANCE_COMPARISON.json\n"
        "python scripts/update_performance_readme.py \\\n"
        "  --comparison reports/PERFORMANCE_COMPARISON_ALPHA10.json --check",
        "python scripts/benchmark_performance_v2.py \\\n"
        "  --repeats 5 --wheel-dir wheelhouse \\\n"
        "  --output reports/runtime/PERFORMANCE_RESULTS_V2.json\n"
        "python scripts/compare_performance_v2.py \\\n"
        "  --baseline reports/PERFORMANCE_BASELINE_ALPHA10_EXTENDED.json \\\n"
        "  --current reports/runtime/PERFORMANCE_RESULTS_V2.json \\\n"
        "  --output reports/runtime/PERFORMANCE_COMPARISON_V2.json\n"
        "python scripts/update_performance_readme.py \\\n"
        "  --comparison reports/PERFORMANCE_COMPARISON_ALPHA11.json --check",
    )
    _replace(
        "README.zh-CN.md",
        "python scripts/benchmark_performance.py --repeats 7 --output reports/runtime/PERFORMANCE_RESULTS.json\n"
        "python scripts/compare_performance.py \\\n"
        "  --baseline reports/PERFORMANCE_BASELINE_ALPHA9.json \\\n"
        "  --current reports/runtime/PERFORMANCE_RESULTS.json \\\n"
        "  --output reports/runtime/PERFORMANCE_COMPARISON.json\n"
        "python scripts/update_performance_readme.py \\\n"
        "  --comparison reports/PERFORMANCE_COMPARISON_ALPHA10.json --check",
        "python scripts/benchmark_performance_v2.py \\\n"
        "  --repeats 5 --wheel-dir wheelhouse \\\n"
        "  --output reports/runtime/PERFORMANCE_RESULTS_V2.json\n"
        "python scripts/compare_performance_v2.py \\\n"
        "  --baseline reports/PERFORMANCE_BASELINE_ALPHA10_EXTENDED.json \\\n"
        "  --current reports/runtime/PERFORMANCE_RESULTS_V2.json \\\n"
        "  --output reports/runtime/PERFORMANCE_COMPARISON_V2.json\n"
        "python scripts/update_performance_readme.py \\\n"
        "  --comparison reports/PERFORMANCE_COMPARISON_ALPHA11.json --check",
    )

    _replace(
        "README.md",
        "The gate requires identical result digests. EPDM site-family and semibatch workloads, POE RK4 and source-identity verification also have explicit minimum speedups; the 500-equipment universal package workload has a no-material-regression floor.",
        "The v2 gate protects 17 common workloads and three optimized paths. Stable structures retain exact SHA-256 identity; floating-point array/LAPACK paths use named analytical tolerance tests; Doctor and Wheel use semantic contracts. The gate also enforces peak-memory and 10× scale-efficiency limits. NumPy remains the only required acceleration dependency; SciPy, Numba and JAX remain optional research candidates until separate cross-platform qualification proves a net benefit.",
    )
    _replace(
        "README.zh-CN.md",
        "性能门要求结果摘要完全一致；EPDM 位点族与半连续负载、POE RK4 和源身份核验还必须达到明确最低加速比，500 台设备通用工艺包负载则设有“不得实质退化”底线。",
        "v2 性能门保护 17 个共用负载和 3 条新增优化路径。结构稳定的结果继续要求精确 SHA-256；浮点数组和 LAPACK 路径采用具名解析容差测试；Doctor 与 Wheel 采用语义合同；同时约束峰值内存和 10 倍尺度效率。NumPy 仍是唯一必需加速依赖，SciPy、Numba 和 JAX 只有在独立跨平台资格证明净收益后才会成为可选后端。",
    )

    for relative in ("README.md", "README.zh-CN.md"):
        _replace(
            relative,
            "python scripts/generate_decision_readme_assets.py\n",
            "python scripts/generate_decision_readme_assets.py\n"
            "python scripts/generate_performance_readme_assets.py\n",
        )
    _replace("README.md", "all 16 diagrams", "all 18 diagrams")
    _replace("README.zh-CN.md", "全部 16 幅图", "全部 18 幅图")


def _update_docs() -> None:
    _replace(
        "docs/CAPABILITY_MATRIX.md",
        "# TSAO capability matrix — 0.1.0-alpha.10",
        f"# TSAO capability matrix — {PUBLIC_VERSION}",
    )
    _replace(
        "docs/CAPABILITY_MATRIX.md",
        "| README functional graphics | universal lifecycle, architecture, data, control and integration | mechanism, kinetics, uncertainty, reactor, process and customer bridge | represented in platform/evidence views | represented in four-Skill delivery | 16 deterministic SVGs, bilingual parity and XML tests |",
        "| README functional graphics | universal lifecycle, architecture, data, control and integration | mechanism, kinetics, batch screening, uncertainty, reactor, process and customer bridge | represented in platform/evidence views | represented in four-Skill delivery | 18 deterministic SVGs, bilingual parity and XML tests |\n"
        "| Batch screening / trajectory execution | framework contracts | NumPy broadcast scenario screening + once-validated full-history semibatch trajectory | fixed-state full-history and terminal-only RK4 | reusable experiment planning | scalar parity, exact/tolerance contracts, shape and domain attacks |\n"
        "| Performance regression | generic and large-package workloads | 64/512 site families, scalar/batch scans and 10k-step trajectories | 400/10k RK4, Jacobian, fitting and 10k-point dynamics | inherited CI contract | timing, peak memory, exact/analytic parity and 10× scale Gates |",
    )

    changelog = _read("CHANGELOG.md")
    marker = "# Changelog\n\n"
    if not changelog.startswith(marker):
        raise SystemExit("CHANGELOG.md heading is unexpected")
    section = (
        f"## {PUBLIC_VERSION} — {RELEASE_DATE}\n\n"
        "- Added NumPy-broadcast EPDM screening for temperature, residence-time, active-site and propagation-multiplier scenario grids.\n"
        "- Added a once-validated full-history EPDM semibatch trajectory and a POE terminal-only RK4 execution path.\n"
        "- Replaced POE RK4 inner-loop dataclass dispatch with a fixed-state numerical kernel while preserving public result identity.\n"
        "- Expanded performance evidence to 20 workloads with warm-ups, medians, variability, cProfile hotspots, peak traced memory and scale checks.\n"
        "- Added exact, analytical-tolerance and semantic parity contracts instead of applying an invalid cross-version digest rule to every workload.\n"
        "- Added primary-source technology review and an explicit non-adoption record for SciPy, Numba, JAX and process parallelism.\n"
        "- Added deterministic batch-scan and performance-regression diagrams, bringing the bilingual README contract to eighteen assets.\n"
        "- Upgraded the permanent CI to the alpha.11 v2 performance gate while retaining Python 3.11–3.14 and isolated Wheel installation checks.\n\n"
    )
    _write("CHANGELOG.md", marker + section + changelog[len(marker):])


def _update_reports() -> None:
    identity = _load_json("reports/RELEASE_IDENTITY.json")
    identity["version"] = PUBLIC_VERSION
    source_core = identity.get("source_core")
    if not isinstance(source_core, dict):
        raise SystemExit("release identity source_core is invalid")
    source_core["status"] = "reports/ALPHA11_SOURCE_CORE_STATUS.json"
    _write_json("reports/RELEASE_IDENTITY.json", identity)

    complete = _load_json("reports/COMPLETE_DISTRIBUTION_REFERENCE.json")
    complete["version"] = PUBLIC_VERSION
    complete["reason"] = (
        "The controlled complete distribution, including excluded historical binary assets, "
        "has not been rebuilt and cleanroom-qualified for alpha.11. The public source core, "
        "open Wheel and performance evidence are verified separately."
    )
    _write_json("reports/COMPLETE_DISTRIBUTION_REFERENCE.json", complete)

    status: dict[str, object] = {
        "version": PUBLIC_VERSION,
        "status": "QUALIFIED_ALPHA",
        "source_core_manifest": "reports/SOURCE_CORE_MANIFEST.tsv",
        "universal_process_package": "IMPLEMENTED_ALPHA",
        "process_general_modules": "14_OF_14",
        "process_general_workflows": "6_OF_6",
        "epdm": "EXECUTABLE_FLAGSHIP_ALPHA_P1_REFERENCE",
        "epdm_module_contracts": "14_OF_14",
        "epdm_requirement_registry": "20_OF_20",
        "epdm_batch_screening": "NUMPY_BROADCAST_REFERENCE",
        "epdm_semibatch_trajectory": "ONCE_VALIDATED_FULL_HISTORY",
        "poe": "EXECUTABLE_SPECIALIST_ALPHA_P1_REFERENCE",
        "poe_terminal_execution": "NO_HISTORY_ALLOCATION_OPTION",
        "polymer_general_scripts": "6_OF_6",
        "readme_assets": "18_OF_18",
        "performance_baseline": "reports/PERFORMANCE_BASELINE_ALPHA10_EXTENDED.json",
        "performance_optimized": "reports/PERFORMANCE_OPTIMIZED_ALPHA11.json",
        "performance_comparison": "reports/PERFORMANCE_COMPARISON_ALPHA11.json",
        "performance_gate": "EXACT_TOLERANCE_SEMANTIC_SPEED_MEMORY_AND_SCALE",
        "performance_workloads": 20,
        "python_versions": ["3.11", "3.12", "3.13", "3.14"],
        "wheel_install_modes": ["PIP_TARGET", "STANDARD_VENV"],
        "standard_venv_isolation": "NO_SYSTEM_SITE_PACKAGES",
        "installed_import_origin": "VERIFIED_INSIDE_INSTALL_ROOT",
        "artifact_software_qualification": "PASS",
        "scientific_technical_approval": "NOT_EVALUATED",
        "engineering_design_approval": "NOT_EVALUATED",
        "customer_qualification": "NOT_EVALUATED",
        "industrial_performance_guarantee": "NOT_EVALUATED",
    }
    _write_json("reports/ALPHA11_SOURCE_CORE_STATUS.json", status)

    reports_index = _read("reports/README.md")
    reports_index = reports_index.replace("## Current alpha.10 identities", "## Current alpha.11 identities", 1)
    reports_index = reports_index.replace(
        "- `RELEASE_IDENTITY.json` — alpha.10 source/release boundary and current source-status pointer.\n"
        "- `ALPHA10_SOURCE_CORE_STATUS.json` — qualified public source, four-Skill, sixteen-diagram and isolated-install status.\n",
        "- `RELEASE_IDENTITY.json` — alpha.11 source/release boundary and current source-status pointer.\n"
        "- `ALPHA11_SOURCE_CORE_STATUS.json` — qualified public source, four-Skill, eighteen-diagram, batch-performance and isolated-install status.\n"
        "- `PERFORMANCE_BASELINE_ALPHA10_EXTENDED.json` — frozen pre-alpha.11 extended timing and memory baseline.\n"
        "- `PERFORMANCE_OPTIMIZED_ALPHA11.json` and `PERFORMANCE_COMPARISON_ALPHA11.json` — measured alpha.11 evidence and fail-closed comparison.\n"
        "- `PERFORMANCE_TECHNOLOGY_REVIEW.md` and `PERFORMANCE_OPTIMIZATION_PLAN.md` — primary-source technology decisions and implementation plan.\n",
        1,
    )
    reports_index = reports_index.replace("for alpha.10.", "for alpha.11.", 1)
    reports_index = reports_index.replace(
        "## Historical identities\n\n",
        "## Historical identities\n\n"
        "- `ALPHA10_SOURCE_CORE_STATUS.json`, `PERFORMANCE_BASELINE_ALPHA9.json`, `PERFORMANCE_OPTIMIZED_ALPHA10.json` and `PERFORMANCE_COMPARISON_ALPHA10.json` — frozen alpha.10 records.\n",
        1,
    )
    _write("reports/README.md", reports_index)

    audit = _read("reports/FINAL_AUDIT_REPORT.md")
    audit = audit.replace("Release identity: `0.1.0-alpha.10`", f"Release identity: `{PUBLIC_VERSION}`", 1)
    audit += (
        "\n## Alpha.11 performance convergence\n\n"
        "The second performance pass added NumPy broadcast screening, a once-validated EPDM semibatch trajectory and a fixed-state POE RK4 kernel with an optional terminal-only result. The release evidence covers twenty workloads, peak traced memory and three tenfold scale checks. Stable records retain exact SHA-256 parity; floating-point array/LAPACK paths use named analytical tolerance tests; Doctor and Wheel use semantic contracts. SciPy, Numba, JAX and process parallelism remain documented candidates rather than unqualified base dependencies.\n\n"
        "The bilingual README contains eighteen deterministic functional SVGs. The open Wheel packages the alpha.10 extended baseline, alpha.11 optimized/comparison reports and the technology review. All scientific, engineering, HSE, customer and industrial approvals remain outside software self-qualification.\n"
    )
    _write("reports/FINAL_AUDIT_REPORT.md", audit)


def _update_tests() -> None:
    old_path = ROOT / "tests/test_release_metadata_alpha10.py"
    new_path = ROOT / "tests/test_release_metadata_alpha11.py"
    if not old_path.is_file() or new_path.exists():
        raise SystemExit("release metadata test rename precondition failed")
    text = old_path.read_text(encoding="utf-8")
    text = text.replace("PUBLIC_VERSION = \"0.1.0-alpha.10\"", f'PUBLIC_VERSION = "{PUBLIC_VERSION}"')
    text = text.replace("PEP440_VERSION = \"0.1.0a10\"", f'PEP440_VERSION = "{PEP440_VERSION}"')
    text = text.replace("test_alpha10_release_identity_is_consistent", "test_alpha11_release_identity_is_consistent")
    text = text.replace("ALPHA10_SOURCE_CORE_STATUS.json", "ALPHA11_SOURCE_CORE_STATUS.json")
    text = text.replace("PERFORMANCE_COMPARISON_ALPHA10.json", "PERFORMANCE_COMPARISON_ALPHA11.json")
    text = text.replace("comparison[\"comparisons\"]", "comparison[\"common_workload_comparisons\"]")
    text = text.replace(
        "assert all(row[\"result_digest_match\"] for row in comparison[\"common_workload_comparisons\"])",
        "assert all(row[\"pass\"] for row in comparison[\"common_workload_comparisons\"])\n"
        "    assert all(row[\"pass\"] for row in comparison[\"optimized_path_comparisons\"])\n"
        "    assert all(row[\"pass\"] for row in comparison[\"scale_checks\"])",
    )
    text = text.replace(
        '"reports/PERFORMANCE_BASELINE_ALPHA9.json",\n'
        '        "reports/PERFORMANCE_OPTIMIZED_ALPHA10.json",\n'
        '        "reports/PERFORMANCE_COMPARISON_ALPHA11.json",',
        '"reports/PERFORMANCE_BASELINE_ALPHA10_EXTENDED.json",\n'
        '        "reports/PERFORMANCE_OPTIMIZED_ALPHA11.json",\n'
        '        "reports/PERFORMANCE_COMPARISON_ALPHA11.json",\n'
        '        "reports/PERFORMANCE_TECHNOLOGY_REVIEW.md",\n'
        '        "reports/PERFORMANCE_OPTIMIZATION_PLAN.md",',
    )
    text = text.replace("test_current_release_docs_and_ci_are_alpha10", "test_current_release_docs_and_ci_are_alpha11")
    text = text.replace("0.1.0-alpha.10", PUBLIC_VERSION)
    text = text.replace("Current alpha.10 identities", "Current alpha.11 identities")
    text = text.replace("name: TSAO alpha10 qualification", "name: TSAO alpha11 qualification")
    text = text.replace("source-alpha.10.zip", "source-alpha.11.zip")
    text = text.replace("tsao-source-alpha10-", "tsao-source-alpha11-")
    text = text.replace("benchmark_performance.py", "benchmark_performance_v2.py")
    text = text.replace("compare_performance.py", "compare_performance_v2.py")
    text = text.replace("status-alpha.10", "status-alpha.11")
    new_path.write_text(text, encoding="utf-8")
    old_path.unlink()

    for relative in ("tests/test_repository_contracts.py",):
        text = _read(relative)
        text = text.replace('"0.1.0-alpha.10"', f'"{PUBLIC_VERSION}"')
        text = text.replace('"0.1.0a10"', f'"{PEP440_VERSION}"')
        text = text.replace("ALPHA10_SOURCE_CORE_STATUS.json", "ALPHA11_SOURCE_CORE_STATUS.json")
        text = text.replace("## 0.1.0-alpha.10", f"## {PUBLIC_VERSION}")
        text = text.replace("alpha10", "alpha11")
        _write(relative, text)


def main() -> int:
    _update_versions()
    _update_manifest()
    _update_packaging()
    _update_readmes()
    _update_docs()
    _update_reports()
    _update_tests()
    print(f"prepared {PUBLIC_VERSION} performance release metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
