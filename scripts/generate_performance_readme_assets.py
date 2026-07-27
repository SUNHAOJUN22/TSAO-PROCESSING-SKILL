from __future__ import annotations

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/assets/readme"

INK = "#102033"
MUTED = "#52647a"
BLUE = "#2563eb"
CYAN = "#0891b2"
TEAL = "#0f766e"
GREEN = "#15803d"
AMBER = "#d97706"
RED = "#dc2626"
PURPLE = "#7c3aed"


def _text(
    x: int,
    y: int,
    value: str,
    *,
    size: int = 18,
    weight: int = 500,
    fill: str = INK,
    anchor: str = "start",
) -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="Inter,Segoe UI,Arial,sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">'
        f"{escape(value)}</text>"
    )


def _rect(
    x: int,
    y: int,
    width: int,
    height: int,
    *,
    fill: str = "#ffffff",
    stroke: str = "#d7e0ea",
    radius: int = 20,
) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    )


def _line(x1: int, y1: int, x2: int, y2: int, *, color: str = MUTED) -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        'stroke-width="3" stroke-linecap="round" marker-end="url(#arrow)"/>'
    )


def _wrap(title: str, description: str, body: list[str]) -> str:
    definitions = """
    <defs>
      <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#f8fbff"/><stop offset="100%" stop-color="#eef4fb"/>
      </linearGradient>
      <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3"
              orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="#52647a"/>
      </marker>
    </defs>
    """
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="680" '
        'viewBox="0 0 1200 680" role="img">'
        f"<title>{escape(title)}</title><desc>{escape(description)}</desc>"
        f"{definitions}"
        '<rect width="1200" height="680" fill="url(#bg)"/>'
        + "".join(body)
        + "</svg>\n"
    )


def batch_parameter_scan() -> str:
    body = [
        _text(54, 68, "EPDM broadcast parameter-scan pipeline", size=34, weight=760),
        _text(
            54,
            102,
            "Independent temperature, residence-time, active-site and activity scenarios without Python-loop dispatch",
            size=17,
            fill=MUTED,
        ),
        '<line x1="54" y1="124" x2="1146" y2="124" stroke="#dce4ee" stroke-width="2"/>',
        _rect(55, 175, 210, 330, stroke="#93c5fd"),
        _text(160, 220, "Scenario axes", size=23, weight=760, fill=BLUE, anchor="middle"),
        _text(160, 270, "temperature [nT, 1]", size=16, anchor="middle"),
        _text(160, 310, "residence [1, nτ]", size=16, anchor="middle"),
        _text(160, 350, "active sites [nA, 1]", size=16, anchor="middle"),
        _text(160, 390, "activity multiplier", size=16, anchor="middle"),
        _text(160, 447, "finite · positive", size=15, weight=700, fill=RED, anchor="middle"),
        _text(160, 476, "broadcast-compatible", size=15, weight=700, fill=RED, anchor="middle"),
        _rect(355, 175, 230, 330, stroke="#67e8f9"),
        _text(470, 220, "Broadcast mesh", size=23, weight=760, fill=CYAN, anchor="middle"),
        _text(470, 270, "common scenario shape", size=16, anchor="middle"),
        _text(470, 310, "one validation boundary", size=16, anchor="middle"),
        _text(470, 350, "no numpy.vectorize", size=16, anchor="middle"),
        _text(470, 390, "no object loop", size=16, anchor="middle"),
        _text(470, 447, "explicit axis semantics", size=15, weight=700, fill=TEAL, anchor="middle"),
        _rect(675, 175, 230, 330, stroke="#c4b5fd"),
        _text(790, 220, "Array kernels", size=23, weight=760, fill=PURPLE, anchor="middle"),
        _text(790, 270, "Arrhenius ufuncs", size=16, anchor="middle"),
        _text(790, 310, "shared exposure", size=16, anchor="middle"),
        _text(790, 350, "−expm1(−k·C*·τ)", size=16, anchor="middle"),
        _text(790, 390, "E / P / diene arrays", size=16, anchor="middle"),
        _text(790, 447, "CALCULATED_REFERENCE_ONLY", size=13, weight=700, fill=AMBER, anchor="middle"),
        _rect(995, 175, 150, 330, stroke="#86efac"),
        _text(1070, 220, "Outputs", size=23, weight=760, fill=GREEN, anchor="middle"),
        _text(1070, 275, "shape", size=16, anchor="middle"),
        _text(1070, 315, "scenario count", size=16, anchor="middle"),
        _text(1070, 355, "rate constants", size=16, anchor="middle"),
        _text(1070, 395, "conversions", size=16, anchor="middle"),
        _text(1070, 447, "scalar parity", size=15, weight=700, fill=GREEN, anchor="middle"),
        _line(265, 340, 355, 340),
        _line(585, 340, 675, 340),
        _line(905, 340, 995, 340),
        _rect(160, 555, 880, 70, fill="#ecfdf5", stroke="#86efac", radius=18),
        _text(
            600,
            585,
            "1,000-scenario screening: one array call · elementwise scalar tolerance contract",
            size=18,
            weight=750,
            fill=GREEN,
            anchor="middle",
        ),
        _text(
            600,
            612,
            "Batch throughput is software evidence; it does not certify EPDM kinetic parameters",
            size=14,
            fill=INK,
            anchor="middle",
        ),
    ]
    return _wrap(
        "EPDM batch parameter scan",
        "Broadcast parameter axes, validated NumPy kernels and scalar-parity output contract.",
        body,
    )


def performance_regression_gate() -> str:
    body = [
        _text(54, 68, "Fail-closed performance regression gate", size=34, weight=760),
        _text(
            54,
            102,
            "Performance is accepted only when timing, memory, scaling and numerical parity pass together",
            size=17,
            fill=MUTED,
        ),
        '<line x1="54" y1="124" x2="1146" y2="124" stroke="#dce4ee" stroke-width="2"/>',
    ]
    stages = [
        (55, "Frozen baseline", "version · commit\ninput scale · environment", BLUE),
        (275, "Measurement", "warm-up · median\nmin/max · stdev", CYAN),
        (495, "Hotspots", "cProfile\ntraced peak memory", PURPLE),
        (715, "Parity", "exact digest\nor named tolerance", AMBER),
        (935, "Gate", "speed · memory\nscale · boundaries", GREEN),
    ]
    for index, (x, title, details, color) in enumerate(stages):
        body.extend(
            [
                _rect(x, 190, 190, 275, stroke=f"{color}77"),
                f'<circle cx="{x + 95}" cy="248" r="34" fill="{color}" stroke="#fff" stroke-width="4"/>',
                _text(x + 95, 320, title, size=20, weight=760, fill=color, anchor="middle"),
            ]
        )
        for detail_index, detail in enumerate(details.split("\n")):
            body.append(
                _text(
                    x + 95,
                    370 + 33 * detail_index,
                    detail,
                    size=15,
                    fill=MUTED,
                    anchor="middle",
                )
            )
        if index < len(stages) - 1:
            body.append(_line(x + 190, 330, x + 220, 330))
    body.extend(
        [
            _rect(90, 525, 1020, 100, fill="#fff7ed", stroke="#fdba74", radius=20),
            _text(600, 560, "PASS → permanent CI evidence", size=21, weight=780, fill=GREEN, anchor="middle"),
            _text(600, 592, "FAIL → retain evidence · identify hotspot · fix code · rerun the same workload", size=17, fill=RED, anchor="middle"),
            _text(600, 618, "No reduced precision, skipped validation or cached result may satisfy the gate", size=14, fill=INK, anchor="middle"),
        ]
    )
    return _wrap(
        "Performance regression gate",
        "Frozen baselines, repeatable measurements, hotspot attribution, parity checks and fail-closed CI decisions.",
        body,
    )


ASSETS = {
    "batch-parameter-scan.svg": batch_parameter_scan,
    "performance-regression-gate.svg": performance_regression_gate,
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, builder in ASSETS.items():
        (OUT / name).write_text(builder(), encoding="utf-8")
    print(f"generated {len(ASSETS)} performance README assets in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
