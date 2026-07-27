#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _replace_once(text: str, old: str, new: str, *, label: str) -> str:
    if new in text:
        return text
    if text.count(old) != 1:
        raise ValueError(f"{label}: expected exactly one source anchor")
    return text.replace(old, new, 1)


def _english(text: str) -> str:
    text = _replace_once(
        text,
        "[简体中文](README.zh-CN.md) · [Architecture](ARCHITECTURE.md) · [Capability matrix](docs/CAPABILITY_MATRIX.md) · [Research integrity](docs/RESEARCH_INTEGRITY.md)",
        "[简体中文](README.zh-CN.md) · [Architecture](ARCHITECTURE.md) · [Capability matrix](docs/CAPABILITY_MATRIX.md) · [Research integrity](docs/RESEARCH_INTEGRITY.md) · [README visual system](docs/README_VISUAL_SYSTEM.md)",
        label="English navigation",
    )
    text = _replace_once(
        text,
        "The inventory fails closed unless the four Skills, 14 general-process modules, 6 workflows, 6 polymer-general scripts and at least 16 README diagrams are present.",
        "The inventory fails closed unless the four Skills, 14 general-process modules, 6 workflows, 6 polymer-general scripts and all 18 README diagrams are present.",
        label="English inventory",
    )
    text = _replace_once(
        text,
        "The EPDM audit fails closed when active-site evidence, diene topology, heat removal, high-viscosity mixing, phase stability, recycle-poison closure, non-equilibrium devolatilization or the raw-polymer-to-customer bridge is incomplete.\n\n## Install and run",
        "The EPDM audit fails closed when active-site evidence, diene topology, heat removal, high-viscosity mixing, phase stability, recycle-poison closure, non-equilibrium devolatilization or the raw-polymer-to-customer bridge is incomplete.\n\n### Batch scenario screening\n\n![EPDM batch parameter-scan data flow](docs/assets/readme/batch-parameter-scan.svg)\n\nBroadcast-compatible scenario arrays are validated once and retain explicit dimensions, numerical parity and the `CALCULATED_REFERENCE_ONLY` boundary.\n\n## Install and run",
        label="English batch figure",
    )
    text = _replace_once(
        text,
        "Performance claims are versioned software evidence, not engineering or industrial qualification. The release harness uses `timeit.repeat` medians for timing, `cProfile` for hotspot attribution and SHA-256 result digests to reject numerical drift.\n\n```bash",
        "Performance claims are versioned software evidence, not engineering or industrial qualification. The release harness uses `timeit.repeat` medians for timing, `cProfile` for hotspot attribution and SHA-256 result digests to reject numerical drift.\n\n![Performance regression qualification gate](docs/assets/readme/performance-regression-gate.svg)\n\n```bash",
        label="English performance figure",
    )
    text = _replace_once(
        text,
        "python scripts/generate_decision_readme_assets.py\npython scripts/run_ci.py",
        "python scripts/generate_decision_readme_assets.py\npython scripts/generate_performance_readme_assets.py\npython scripts/generate_uiux_readme_assets.py\npython scripts/harden_readme_svg_accessibility.py\npython scripts/verify_readme_visual_accessibility.py\npython scripts/sync_readme_visuals.py --check\npython scripts/run_ci.py",
        label="English generator commands",
    )
    text = _replace_once(
        text,
        "all 16 diagrams",
        "all 18 diagrams",
        label="English Wheel diagram count",
    )
    return text


def _chinese(text: str) -> str:
    text = _replace_once(
        text,
        "[English](README.md) · [总体架构](ARCHITECTURE.md) · [能力矩阵](docs/CAPABILITY_MATRIX.md) · [科研诚信](docs/RESEARCH_INTEGRITY.md)",
        "[English](README.md) · [总体架构](ARCHITECTURE.md) · [能力矩阵](docs/CAPABILITY_MATRIX.md) · [科研诚信](docs/RESEARCH_INTEGRITY.md) · [README 视觉系统](docs/README_VISUAL_SYSTEM.md)",
        label="Chinese navigation",
    )
    text = _replace_once(
        text,
        "四条 Skill、14 个通用模块、6 条工作流、6 个聚合物通用脚本或至少 16 幅 README 图中缺少任何一项，库存检查都会失败关闭。",
        "四条 Skill、14 个通用模块、6 条工作流、6 个聚合物通用脚本或全部 18 幅 README 图中缺少任何一项，库存检查都会失败关闭。",
        label="Chinese inventory",
    )
    text = _replace_once(
        text,
        "活性位证据、二烯拓扑、移热、高黏混合、相稳定、循环毒物闭合、非平衡脱挥或“生胶—客户线”桥接不完整时，EPDM 审计默认失败关闭。\n\n## 安装与运行",
        "活性位证据、二烯拓扑、移热、高黏混合、相稳定、循环毒物闭合、非平衡脱挥或“生胶—客户线”桥接不完整时，EPDM 审计默认失败关闭。\n\n### 批量情景筛选\n\n![EPDM 批量参数扫描数据流](docs/assets/readme/batch-parameter-scan.svg)\n\n广播兼容的情景数组只在入口校验一次，同时保留明确维度、数值等价性和 `CALCULATED_REFERENCE_ONLY` 边界。\n\n## 安装与运行",
        label="Chinese batch figure",
    )
    text = _replace_once(
        text,
        "性能结论属于版本化的软件证据，不等于工程或工业资格。发布基准使用 `timeit.repeat` 中位数计时、`cProfile` 定位热点，并用结果 SHA-256 拒绝任何数值漂移。\n\n```bash",
        "性能结论属于版本化的软件证据，不等于工程或工业资格。发布基准使用 `timeit.repeat` 中位数计时、`cProfile` 定位热点，并用结果 SHA-256 拒绝任何数值漂移。\n\n![性能回归资格门](docs/assets/readme/performance-regression-gate.svg)\n\n```bash",
        label="Chinese performance figure",
    )
    text = _replace_once(
        text,
        "python scripts/generate_decision_readme_assets.py\npython scripts/run_ci.py",
        "python scripts/generate_decision_readme_assets.py\npython scripts/generate_performance_readme_assets.py\npython scripts/generate_uiux_readme_assets.py\npython scripts/harden_readme_svg_accessibility.py\npython scripts/verify_readme_visual_accessibility.py\npython scripts/sync_readme_visuals.py --check\npython scripts/run_ci.py",
        label="Chinese generator commands",
    )
    text = _replace_once(
        text,
        "全部 16 幅图",
        "全部 18 幅图",
        label="Chinese Wheel diagram count",
    )
    return text


def _sync(path: Path, transform, *, check: bool) -> bool:
    current = path.read_text(encoding="utf-8")
    updated = transform(current)
    if check:
        return current == updated
    path.write_text(updated, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synchronize bilingual README visual contracts")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    results = [
        _sync(ROOT / "README.md", _english, check=args.check),
        _sync(ROOT / "README.zh-CN.md", _chinese, check=args.check),
    ]
    return 0 if all(results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
