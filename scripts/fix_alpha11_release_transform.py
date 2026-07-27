from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    test_path = ROOT / "tests/test_release_metadata_alpha11.py"
    text = test_path.read_text(encoding="utf-8")
    text = text.replace(
        'assert "alpha.10" in complete["reason"]',
        'assert "alpha.11" in complete["reason"]',
    )
    text = text.replace(
        'assert changelog.index("## 0.1.0-alpha.11") < changelog.index("## 0.1.0-alpha.9")',
        'assert changelog.index("## 0.1.0-alpha.11") < changelog.index("## 0.1.0-alpha.10")',
    )
    test_path.write_text(text, encoding="utf-8")

    reports_index = """# Reports

This directory separates immutable release/source identities from mutable runtime output. Software qualification never substitutes for scientific, engineering, HSE, legal, customer or industrial approval.

## Current alpha.11 identities

- `RELEASE_IDENTITY.json` — alpha.11 source/release boundary and current source-status pointer.
- `ALPHA11_SOURCE_CORE_STATUS.json` — qualified public source, four-Skill, eighteen-diagram, batch-performance and isolated-install status.
- `PERFORMANCE_BASELINE_ALPHA10_EXTENDED.json` — frozen pre-alpha.11 timing, profile, memory and scale baseline.
- `PERFORMANCE_OPTIMIZED_ALPHA11.json` and `PERFORMANCE_COMPARISON_ALPHA11.json` — measured alpha.11 evidence and fail-closed exact/tolerance/memory/scale comparison.
- `PERFORMANCE_TECHNOLOGY_REVIEW.md` and `PERFORMANCE_OPTIMIZATION_PLAN.md` — primary-source technology decisions and implementation plan.
- `SOURCE_CORE_MANIFEST.tsv` — frozen public-source identity verified by `tsao doctor --profile core`.
- `COMPLETE_DISTRIBUTION_REFERENCE.json` — explicitly `NOT_EVALUATED` until the controlled complete distribution, including excluded historical binaries, is rebuilt and cleanroom-qualified for alpha.11.
- `FINAL_AUDIT_REPORT.md` — latest repository, Wheel, CI, branch, performance and responsibility-boundary audit.
- `poe/POE_ALPHA7_P1_REMEDIATION.md` — POE P1 remediation history and remaining external Gates.

## Historical identities

- `ALPHA10_SOURCE_CORE_STATUS.json`, `PERFORMANCE_BASELINE_ALPHA9.json`, `PERFORMANCE_OPTIMIZED_ALPHA10.json` and `PERFORMANCE_COMPARISON_ALPHA10.json` — frozen alpha.10 records.
- `ALPHA9_SOURCE_CORE_STATUS.json` — frozen alpha.9 release record.
- `ALPHA8_SOURCE_CORE_STATUS.json` and `ALPHA8_PROCESS_PACKAGE_EPDM_REMEDIATION.md` — frozen alpha.8 records.
- `ALPHA7_SOURCE_CORE_STATUS.json` — frozen alpha.7 source identity.
- `history/COMPLETE_DISTRIBUTION_REFERENCE_ALPHA6.json` — qualified alpha.6 controlled complete distribution.
- `history/ALPHA6_SOURCE_CORE_STATUS.json` and `history/CI_RESULTS_BEFORE_RUNTIME_SPLIT.json` — frozen alpha.6 records.
- Alpha.6 POE P0 reports remain historical evidence of the preceding release.

## Runtime output

`scripts/run_ci.py` writes mutable execution output under `reports/runtime/`. Runtime files are excluded from frozen source and release manifests. Promote a result to a versioned report only with the exact tested source identity and approval boundary.
"""
    (ROOT / "reports/README.md").write_text(reports_index, encoding="utf-8")
    print("fixed alpha11 release test and reports index")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
