from __future__ import annotations

from pathlib import Path


def replace_once(text: str, old: str, new: str, *, label: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"{label} anchor changed")
    return text.replace(old, new, 1)


def main() -> int:
    comparator = Path("scripts/compare_performance_v2.py")
    text = comparator.read_text(encoding="utf-8")
    text = replace_once(
        text,
        'LEGACY_HISTORICAL_BASELINES = {"0.1.0-alpha.10"}\n\nSPECIAL_SPECS = (',
        '''LEGACY_HISTORICAL_BASELINES = {"0.1.0-alpha.10"}

HISTORICAL_RETIRED_WORKLOADS = {
    "wheel_content_verification": (
        "public wheel generation is intentionally blocked by "
        "BLOCKED_CONTROLLED_METADATA_CLASSIFICATION; source qualification and "
        "distribution-containment regressions replace this historical workload"
    )
}

SPECIAL_SPECS = (''',
        label="historical baseline constant",
    )
    text = replace_once(
        text,
        '''    missing = sorted(set(baseline_rows) - set(current_rows))
    if missing:
        errors.append(f"current report is missing baseline workloads: {missing}")
''',
        '''    missing = sorted(set(baseline_rows) - set(current_rows))
    if historical:
        unexpected_missing: list[str] = []
        for name in missing:
            reason = HISTORICAL_RETIRED_WORKLOADS.get(name)
            if reason is None:
                unexpected_missing.append(name)
                continue
            not_applicable.append(f"{name}: {reason}")
        missing = unexpected_missing
    if missing:
        errors.append(f"current report is missing baseline workloads: {missing}")
''',
        label="missing-workload comparator",
    )
    comparator.write_text(text, encoding="utf-8")

    Path("tests/test_historical_performance_boundary.py").write_text(
        '''from __future__ import annotations

from scripts.compare_performance_v2 import _common_comparisons


def _row(name: str) -> dict[str, object]:
    return {
        "name": name,
        "median_s_per_call": 1.0,
        "peak_memory_bytes": 1,
        "result_sha256": name,
    }


def test_controlled_public_wheel_is_not_applicable_only_for_historical_trend() -> None:
    errors: list[str] = []
    not_applicable: list[str] = []
    comparisons = _common_comparisons(
        {"wheel_content_verification": _row("wheel_content_verification")},
        {},
        historical=True,
        errors=errors,
        not_applicable=not_applicable,
    )
    assert comparisons == []
    assert errors == []
    assert len(not_applicable) == 1
    assert "wheel_content_verification" in not_applicable[0]
    assert "BLOCKED_CONTROLLED_METADATA_CLASSIFICATION" in not_applicable[0]


def test_unexpected_historical_missing_workload_still_fails_closed() -> None:
    errors: list[str] = []
    not_applicable: list[str] = []
    _common_comparisons(
        {"unexpected_workload": _row("unexpected_workload")},
        {},
        historical=True,
        errors=errors,
        not_applicable=not_applicable,
    )
    assert errors == [
        "current report is missing baseline workloads: ['unexpected_workload']"
    ]
    assert not_applicable == []


def test_current_qualification_cannot_hide_missing_wheel_workload() -> None:
    errors: list[str] = []
    not_applicable: list[str] = []
    _common_comparisons(
        {"wheel_content_verification": _row("wheel_content_verification")},
        {},
        historical=False,
        errors=errors,
        not_applicable=not_applicable,
    )
    assert errors == [
        "current report is missing baseline workloads: ['wheel_content_verification']"
    ]
    assert not_applicable == []
''',
        encoding="utf-8",
    )

    english = Path("README.md")
    english_text = english.read_text(encoding="utf-8")
    if "## Historical performance qualification boundary" not in english_text:
        english_text += '''

## Historical performance qualification boundary

Current blocking performance qualification compares the current source tree with the alpha.14 parent on the same runner and Python interpreter. Numerical parity, same-path timing, optimized-path benefit retention, scale checks, and all unexpected missing workloads remain fail-closed.

The alpha.10 `wheel_content_verification` timing is recorded as `NOT_APPLICABLE` only when that historical workload is absent because public wheel generation is intentionally blocked by `BLOCKED_CONTROLLED_METADATA_CLASSIFICATION`. Source qualification and distribution-containment regressions replace that retired public-artifact workload. This exception does not permit a wheel or source snapshot to be emitted, does not relax any current performance threshold, and does not convert software qualification into scientific, engineering, HSE, customer, or industrial approval.
'''
        english.write_text(english_text, encoding="utf-8")

    chinese = Path("README.zh-CN.md")
    chinese_text = chinese.read_text(encoding="utf-8")
    if "## 历史性能资格边界" not in chinese_text:
        chinese_text += '''

## 历史性能资格边界

当前具有阻断效力的性能资格，在同一运行器和同一 Python 解释器上，将当前源码树与 alpha.14 父基线比较。数值等价、同路径耗时、优化路径收益保持率、规模扩展检查以及所有非预期缺失工作负载仍然保持 fail-closed。

alpha.10 的 `wheel_content_verification` 计时仅在该历史工作负载缺失时记为 `NOT_APPLICABLE`，因为公共 wheel 生成已被 `BLOCKED_CONTROLLED_METADATA_CLASSIFICATION` 明确阻断。当前由源码资格与分发封闭回归替代这一已退役的公共制品工作负载。该例外不允许生成 wheel 或源码快照，不放宽任何当前性能阈值，也不把软件资格扩大解释为科学、工程、HSE、客户或工业批准。
'''
        chinese.write_text(chinese_text, encoding="utf-8")

    Path(".github/workflows/apply-performance-boundary-fix.yml").unlink()
    Path(__file__).unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
