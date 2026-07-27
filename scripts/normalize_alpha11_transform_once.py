from __future__ import annotations

# One-shot compatibility bridge; deleted by the successful Alpha.11 promotion.
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/CAPABILITY_MATRIX.md"
COMPARE = ROOT / "scripts/compare_performance_v2.py"
UIUX = ROOT / "scripts/generate_uiux_readme_assets.py"
PERFORMANCE_ASSETS = ROOT / "scripts/generate_performance_readme_assets.py"
PATCH_HELPER = ROOT / "scripts/patch_alpha11_compare_once.py"

ADVANCED_ROW = "| README functional graphics | universal lifecycle, architecture, data, control and integration | mechanism, kinetics, batch screening, uncertainty, reactor, process and customer bridge | represented in platform/evidence/performance views | represented in four-Skill delivery | 18 deterministic SVGs, persisted Scientific Midnight Bento design system, WCAG contrast, explicit title/desc, 12px minimum text, no external resources, bilingual parity and XML accessibility tests |\n"
LEGACY_ROW = "| README functional graphics | universal lifecycle, architecture, data, control and integration | mechanism, kinetics, uncertainty, reactor, process and customer bridge | represented in platform/evidence views | represented in four-Skill delivery | 16 deterministic SVGs, bilingual parity and XML tests |\n"
GENERATED_BLOCK = (
    "| README functional graphics | universal lifecycle, architecture, data, control and integration | mechanism, kinetics, batch screening, uncertainty, reactor, process and customer bridge | represented in platform/evidence views | represented in four-Skill delivery | 18 deterministic SVGs, bilingual parity and XML tests |\n"
    "| Batch screening / trajectory execution | framework contracts | NumPy broadcast scenario screening + once-validated full-history semibatch trajectory | fixed-state full-history and terminal-only RK4 | reusable experiment planning | scalar parity, exact/tolerance contracts, shape and domain attacks |\n"
    "| Performance regression | generic and large-package workloads | 64/512 site families, scalar/batch scans and 10k-step trajectories | 400/10k RK4, Jacobian, fitting and 10k-point dynamics | inherited CI contract | timing, peak memory, exact/analytic parity and 10× scale Gates |\n"
)
COMPUTE_ROW = "| Computational efficiency | validated numerics reused in balance loops | vectorized batch screening, site-family and semibatch fast paths | POE RK4, terminal-only, fitting and linear settling analysis | reusable scripts unchanged | exact/tolerance/semantic parity + timing, memory and scale Gates |\n"
PERFORMANCE_ROW = "| Performance regression | package-scale non-regression | batch/trajectory speed and parity | RK4 speed and terminal memory | inherited | frozen baseline, median timing, peak memory, three tenfold scale checks and fail-closed comparison |\n"
SOURCE_CI_ROW = "| Source/CI efficiency | one-read canonical identity and pruned walk | inherited | inherited | inherited | Doctor scan reuse; independent audits run in parallel after coverage |\n"
OLD_POLICIES = '''PARITY_POLICIES = {
    "doctor_core_repository": "repository semantic contract: PASS and approval boundaries",
    "wheel_content_verification": "wheel semantic contract: identity and required-member tests",
    "poe_dynamic_response_10000_points": "analytical response and metric tolerance contract",
    "poe_finite_difference_jacobian_8x200": "analytical Jacobian tolerance contract",
}
'''
NEW_POLICIES = '''PARITY_POLICIES = {
    "doctor_core_repository": "repository semantic contract: PASS and approval boundaries",
    "skillpack_inventory": (
        "skillpack semantic contract: four Skills, 14/6/6 inventory, "
        "README assets and approval boundaries"
    ),
    "wheel_content_verification": "wheel semantic contract: identity and required-member tests",
    "poe_dynamic_response_10000_points": "analytical response and metric tolerance contract",
    "poe_finite_difference_jacobian_8x200": "analytical Jacobian tolerance contract",
}
'''
PERFORMANCE_GENERATOR = '''from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_uiux_readme_assets import (  # noqa: E402
    OUT,
    render_batch_scan,
    render_perf_gate,
)

ASSETS = {
    "batch-parameter-scan.svg": render_batch_scan,
    "performance-regression-gate.svg": render_perf_gate,
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, builder in ASSETS.items():
        (OUT / name).write_text(builder(), encoding="utf-8")
    print(f"generated {len(ASSETS)} performance README assets in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def normalize(text: str) -> str:
    if ADVANCED_ROW in text:
        text = text.replace(ADVANCED_ROW, LEGACY_ROW, 1)
        text = text.replace(COMPUTE_ROW, "", 1)
        text = text.replace(PERFORMANCE_ROW, "", 1)
    elif LEGACY_ROW not in text:
        raise SystemExit("capability matrix is neither the current advanced state nor the alpha10 transform baseline")
    return text


def restore(text: str) -> str:
    if GENERATED_BLOCK not in text:
        raise SystemExit("alpha11 generated capability block was not found")
    text = text.replace(GENERATED_BLOCK, ADVANCED_ROW, 1)
    if SOURCE_CI_ROW not in text:
        raise SystemExit("capability matrix Source/CI anchor was not found")
    return text.replace(SOURCE_CI_ROW, COMPUTE_ROW + PERFORMANCE_ROW + SOURCE_CI_ROW, 1)


def patch_compare() -> None:
    text = COMPARE.read_text(encoding="utf-8")
    if NEW_POLICIES not in text:
        if text.count(OLD_POLICIES) != 1:
            raise SystemExit("performance comparison parity-policy block changed unexpectedly")
        COMPARE.write_text(text.replace(OLD_POLICIES, NEW_POLICIES, 1), encoding="utf-8")
    PATCH_HELPER.unlink(missing_ok=True)


def patch_visual_generators() -> None:
    text = UIUX.read_text(encoding="utf-8")
    old = 'text(1089, 335, "10.46×", size=25, fill=TEXT, weight=850, anchor="middle")'
    new = 'text(1089, 335, "≥3× gate", size=22, fill=TEXT, weight=850, anchor="middle")'
    if new not in text:
        if text.count(old) != 1:
            raise SystemExit("UIUX batch-speed label changed unexpectedly")
        UIUX.write_text(text.replace(old, new, 1), encoding="utf-8")
    PERFORMANCE_ASSETS.write_text(PERFORMANCE_GENERATOR, encoding="utf-8")


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "normalize"
    text = MATRIX.read_text(encoding="utf-8")
    if mode == "normalize":
        text = normalize(text)
    elif mode == "restore":
        text = restore(text)
        patch_compare()
        patch_visual_generators()
    else:
        raise SystemExit(f"unknown mode: {mode}")
    MATRIX.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
