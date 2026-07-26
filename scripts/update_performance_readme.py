from __future__ import annotations

import argparse
import json
from pathlib import Path

START = "<!-- PERFORMANCE_RESULTS_START -->"
END = "<!-- PERFORMANCE_RESULTS_END -->"
_LABELS = {
    "epdm_three_level_64_site_families": (
        "EPDM three-level model, 64 site families",
        "EPDM 三级模型，64 个位点族",
    ),
    "epdm_semibatch_material_energy_step": (
        "EPDM semibatch material-energy step",
        "EPDM 半连续物料—能量步进",
    ),
    "poe_rk4_400_steps": ("POE RK4, 400 steps", "POE RK4，400 步"),
    "process_package_500_equipment": (
        "Universal process package, 500 equipment items",
        "通用工艺包，500 台设备",
    ),
    "provenance_300_files_build_and_verify": (
        "Source identity, 300 files build + verify",
        "源身份，300 文件构建与核验",
    ),
}


def _duration(value: float) -> str:
    if value < 0.001:
        return f"{value * 1_000_000:.2f} µs"
    return f"{value * 1_000:.2f} ms"


def _render(report: dict[str, object], language_index: int) -> str:
    rows = report.get("comparisons")
    if not isinstance(rows, list) or not rows:
        raise ValueError("performance comparison contains no rows")
    if language_index == 0:
        lines = [
            START,
            "| Workload | Baseline median | Optimized median | Speedup | Result identity |",
            "|---|---:|---:|---:|---|",
        ]
        match, mismatch = "match", "mismatch"
    else:
        lines = [
            START,
            "| 负载 | 基线中位耗时 | 优化后中位耗时 | 加速比 | 结果身份 |",
            "|---|---:|---:|---:|---|",
        ]
        match, mismatch = "一致", "不一致"
    by_name = {row.get("name"): row for row in rows if isinstance(row, dict)}
    for name, labels in _LABELS.items():
        row = by_name.get(name)
        if not isinstance(row, dict):
            raise ValueError(f"missing performance comparison row: {name}")
        identity = match if row.get("result_digest_match") is True else mismatch
        lines.append(
            "| "
            + labels[language_index]
            + f" | {_duration(float(row['baseline_median_s']))}"
            + f" | {_duration(float(row['optimized_median_s']))}"
            + f" | {float(row['speedup']):.2f}× | {identity} |"
        )
    lines.append(END)
    return "\n".join(lines)


def _replace(path: Path, block: str, *, check: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError(f"{path} must contain exactly one performance marker pair")
    prefix, remainder = text.split(START, 1)
    _, suffix = remainder.split(END, 1)
    updated = prefix + block + suffix
    if check:
        return updated == text
    path.write_text(updated, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render release performance evidence into READMEs")
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--readme", type=Path, default=Path("README.md"))
    parser.add_argument("--readme-zh", type=Path, default=Path("README.zh-CN.md"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    report = json.loads(args.comparison.read_text(encoding="utf-8"))
    if not isinstance(report, dict) or report.get("pass") is not True:
        raise ValueError("only a passing performance comparison may be published")
    matches = [
        _replace(args.readme, _render(report, 0), check=args.check),
        _replace(args.readme_zh, _render(report, 1), check=args.check),
    ]
    return 0 if all(matches) else 2


if __name__ == "__main__":
    raise SystemExit(main())
