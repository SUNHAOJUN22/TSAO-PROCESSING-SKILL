#!/usr/bin/env python3
from __future__ import annotations

from html import escape
from pathlib import Path
from textwrap import wrap

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/assets/readme"

W, H = 1200, 720

# TSAO README visual system: Scientific Midnight Bento
BG = "#07111F"
SURFACE = "#101E33"
SURFACE_2 = "#14243B"
BORDER = "#263A55"
TEXT = "#F8FAFC"
MUTED = "#A8B5C7"
DIM = "#6F8299"
BLUE = "#4F7CFF"
CYAN = "#22D3EE"
TEAL = "#2DD4BF"
GREEN = "#34D399"
AMBER = "#FBBF24"
ORANGE = "#FB923C"
RED = "#FB7185"
PURPLE = "#A78BFA"


def xesc(value: object) -> str:
    return escape(str(value), quote=True)


def svg_start(title: str, description: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{xesc(title)}</title>',
        f'<desc id="desc">{xesc(description)}</desc>',
        """
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#07111F"/>
    <stop offset="0.55" stop-color="#0B1729"/>
    <stop offset="1" stop-color="#07111F"/>
  </linearGradient>
  <radialGradient id="glowBlue" cx="0.1" cy="0.05" r="0.8">
    <stop offset="0" stop-color="#4F7CFF" stop-opacity="0.18"/>
    <stop offset="1" stop-color="#4F7CFF" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="glowCyan" cx="0.9" cy="0.8" r="0.65">
    <stop offset="0" stop-color="#22D3EE" stop-opacity="0.12"/>
    <stop offset="1" stop-color="#22D3EE" stop-opacity="0"/>
  </radialGradient>
  <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
    <path d="M 32 0 L 0 0 0 32" fill="none" stroke="#18304C" stroke-width="1" opacity="0.32"/>
  </pattern>
  <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#020617" flood-opacity="0.45"/>
  </filter>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8.5" refY="4" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,8 L9,4 z" fill="#6F8299"/>
  </marker>
  <marker id="arrowBlue" markerWidth="10" markerHeight="10" refX="8.5" refY="4" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,8 L9,4 z" fill="#4F7CFF"/>
  </marker>
  <style>
    .sans { font-family: Inter, "Segoe UI", Arial, sans-serif; }
    .mono { font-family: "JetBrains Mono", "SFMono-Regular", Consolas, monospace; }
  </style>
</defs>
""",
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
        f'<rect width="{W}" height="{H}" fill="url(#grid)"/>',
        f'<rect width="{W}" height="{H}" fill="url(#glowBlue)"/>',
        f'<rect width="{W}" height="{H}" fill="url(#glowCyan)"/>',
    ]


def finish(parts: list[str]) -> str:
    parts.append("</svg>\n")
    return "".join(parts)


def text(
    x: float,
    y: float,
    value: str,
    *,
    size: int = 16,
    fill: str = TEXT,
    weight: int = 500,
    anchor: str = "start",
    mono: bool = False,
    opacity: float = 1.0,
    letter: float = 0,
) -> str:
    cls = "mono" if mono else "sans"
    return (
        f'<text class="{cls}" x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}" opacity="{opacity}" '
        f'letter-spacing="{letter}">{xesc(value)}</text>'
    )


def multiline(
    x: float,
    y: float,
    value: str,
    *,
    width_chars: int = 24,
    size: int = 15,
    fill: str = TEXT,
    weight: int = 500,
    anchor: str = "start",
    line_height: int | None = None,
    mono: bool = False,
) -> str:
    lines: list[str] = []
    for raw in value.split("\n"):
        lines.extend(
            wrap(raw, width=width_chars, break_long_words=False, break_on_hyphens=False)
            or [""]
        )
    height = line_height or int(size * 1.45)
    cls = "mono" if mono else "sans"
    spans = [
        f'<tspan x="{x}" dy="{0 if index == 0 else height}">{xesc(line_value)}</tspan>'
        for index, line_value in enumerate(lines)
    ]
    return (
        f'<text class="{cls}" x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}">' + "".join(spans) + "</text>"
    )


def rect(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    fill: str = SURFACE,
    stroke: str = BORDER,
    radius: int = 20,
    stroke_width: float = 1.2,
    opacity: float = 1.0,
    shadow: bool = False,
) -> str:
    filter_value = ' filter="url(#shadow)"' if shadow else ""
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" '
        f'opacity="{opacity}"{filter_value}/>'
    )


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    stroke: str = DIM,
    width: float = 2,
    dash: str | None = None,
    arrow: bool = False,
    blue_arrow: bool = False,
    opacity: float = 1.0,
) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    marker = ""
    if arrow:
        marker = (
            ' marker-end="url(#arrowBlue)"'
            if blue_arrow
            else ' marker-end="url(#arrow)"'
        )
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
        f'stroke-width="{width}" stroke-linecap="round" opacity="{opacity}"'
        f"{dash_attr}{marker}/>"
    ).replace('/>"', '/>')


def path(
    data: str,
    *,
    stroke: str = DIM,
    width: float = 2,
    fill: str = "none",
    arrow: bool = False,
    opacity: float = 1.0,
) -> str:
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    return (
        f'<path d="{data}" stroke="{stroke}" stroke-width="{width}" fill="{fill}" '
        f'stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"{marker}/>'
    )


def circle(
    center_x: float,
    center_y: float,
    radius: float,
    *,
    fill: str = SURFACE_2,
    stroke: str = BORDER,
    width: float = 1.2,
) -> str:
    return (
        f'<circle cx="{center_x}" cy="{center_y}" r="{radius}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{width}"/>'
    )


def pill(
    x: float,
    y: float,
    label: str,
    color: str,
    *,
    width: float | None = None,
    height: float = 28,
    mono: bool = False,
) -> str:
    resolved_width = width or max(72, len(label) * (7.2 if mono else 7.8) + 28)
    return (
        rect(
            x,
            y,
            resolved_width,
            height,
            fill=f"{color}18",
            stroke=f"{color}88",
            radius=int(height / 2),
            stroke_width=1,
        )
        + text(
            x + resolved_width / 2,
            y + height / 2 + 5,
            label,
            size=12,
            fill=color,
            weight=700,
            anchor="middle",
            mono=mono,
            letter=0.2,
        )
    )


def header(
    parts: list[str],
    title_value: str,
    subtitle: str,
    *,
    eyebrow: str = "TSAO PROCESS INTELLIGENCE OS",
    accent: str = BLUE,
) -> None:
    parts.extend(
        [
            pill(52, 38, eyebrow, accent, height=30, mono=True),
            text(52, 105, title_value, size=34, weight=800),
            text(52, 138, subtitle, size=15, fill=MUTED, weight=500),
            line(52, 164, 1148, 164, stroke=BORDER, width=1),
        ]
    )


def small_icon(parts: list[str], center_x: float, center_y: float, kind: str, color: str) -> None:
    parts.append(
        circle(center_x, center_y, 22, fill=f"{color}18", stroke=f"{color}AA", width=1.2)
    )
    if kind == "flow":
        parts.extend(
            [
                circle(center_x - 8, center_y, 3.5, fill=color, stroke=color),
                circle(center_x + 8, center_y, 3.5, fill=color, stroke=color),
                line(
                    center_x - 4,
                    center_y,
                    center_x + 4,
                    center_y,
                    stroke=color,
                    width=2,
                    arrow=True,
                    blue_arrow=color == BLUE,
                ),
            ]
        )
    elif kind == "shield":
        parts.append(
            path(
                f"M {center_x} {center_y-11} L {center_x+10} {center_y-7} "
                f"L {center_x+8} {center_y+5} Q {center_x} {center_y+13} "
                f"{center_x-8} {center_y+5} L {center_x-10} {center_y-7} Z",
                stroke=color,
                width=2,
            )
        )
    elif kind == "cpu":
        parts.append(
            rect(
                center_x - 8,
                center_y - 8,
                16,
                16,
                fill="none",
                stroke=color,
                radius=3,
                stroke_width=2,
            )
        )
        for offset in (-10, 10):
            parts.append(
                line(center_x + offset, center_y - 5, center_x + offset, center_y + 5, stroke=color, width=1.6)
            )
            parts.append(
                line(center_x - 5, center_y + offset, center_x + 5, center_y + offset, stroke=color, width=1.6)
            )
    elif kind == "chart":
        parts.extend(
            [
                rect(center_x - 10, center_y + 2, 5, 8, fill=color, stroke=color, radius=1),
                rect(center_x - 2, center_y - 4, 5, 14, fill=color, stroke=color, radius=1),
                rect(center_x + 6, center_y - 10, 5, 20, fill=color, stroke=color, radius=1),
            ]
        )
    elif kind == "database":
        parts.extend(
            [
                f'<ellipse cx="{center_x}" cy="{center_y-7}" rx="10" ry="4" fill="none" stroke="{color}" stroke-width="2"/>',
                path(
                    f"M {center_x-10} {center_y-7} V {center_y+7} C {center_x-10} {center_y+12} "
                    f"{center_x+10} {center_y+12} {center_x+10} {center_y+7} V {center_y-7}",
                    stroke=color,
                    width=2,
                ),
                path(
                    f"M {center_x-10} {center_y} C {center_x-10} {center_y+5} "
                    f"{center_x+10} {center_y+5} {center_x+10} {center_y}",
                    stroke=color,
                    width=1.5,
                ),
            ]
        )
    elif kind == "molecule":
        parts.extend(
            [
                circle(center_x - 9, center_y + 4, 3.5, fill=color, stroke=color),
                circle(center_x + 1, center_y - 7, 3.5, fill=color, stroke=color),
                circle(center_x + 10, center_y + 6, 3.5, fill=color, stroke=color),
                line(center_x - 6, center_y + 1, center_x - 2, center_y - 4, stroke=color, width=2),
                line(center_x + 4, center_y - 4, center_x + 7, center_y + 3, stroke=color, width=2),
            ]
        )
    else:
        parts.append(circle(center_x, center_y, 6, fill=color, stroke=color))


def node_card(
    parts: list[str],
    x: float,
    y: float,
    width: float,
    height: float,
    title_value: str,
    detail: str,
    color: str,
    *,
    icon: str = "flow",
    tag: str | None = None,
    title_size: int = 17,
) -> None:
    parts.append(
        rect(x, y, width, height, fill=SURFACE, stroke=f"{color}66", radius=20, shadow=True)
    )
    parts.append(rect(x, y, 5, height, fill=color, stroke=color, radius=3))
    small_icon(parts, x + 36, y + 38, icon, color)
    parts.append(text(x + 70, y + 43, title_value, size=title_size, weight=750))
    parts.append(
        multiline(
            x + 22,
            y + 82,
            detail,
            width_chars=max(16, int(width / 9.2)),
            size=13,
            fill=MUTED,
            line_height=20,
        )
    )
    if tag:
        parts.append(pill(x + 20, y + height - 40, tag, color, height=24, mono=True))


def footer_gate(parts: list[str], label: str = "SOFTWARE EVIDENCE ≠ ENGINEERING APPROVAL") -> None:
    parts.append(rect(52, 656, 1096, 38, fill="#0A1627", stroke=BORDER, radius=12))
    parts.append(text(76, 681, label, size=12, fill=MUTED, mono=True, weight=650, letter=0.6))
    parts.append(pill(1010, 661, "FAIL-CLOSED", AMBER, height=28, mono=True))


def render_platform() -> str:
    parts = svg_start(
        "TSAO Process Intelligence OS",
        "Four delivered Skills coordinated by a fail-closed process intelligence core.",
    )
    header(
        parts,
        "One operating system, four specialist Skills",
        "A single evidence, modeling, qualification and delivery contract for chemical-process work",
    )
    center_x, center_y = 600, 390
    parts.append(circle(center_x, center_y, 92, fill="#0D2038", stroke=BLUE, width=2))
    small_icon(parts, center_x, center_y - 22, "cpu", BLUE)
    parts.append(text(center_x, center_y + 20, "TSAO CORE", size=20, weight=800, anchor="middle"))
    parts.append(
        text(
            center_x,
            center_y + 44,
            "route · evidence · gates",
            size=12,
            fill=MUTED,
            anchor="middle",
            mono=True,
        )
    )
    cards = [
        (72, 215, "process-general", "14 modules\n6 workflows\nuniversal package", BLUE, "flow"),
        (72, 425, "polymer-general", "DoE · balance\nscale-up · evidence", TEAL, "chart"),
        (880, 215, "EPDM flagship", "active sites · kinetics\nreactor · finishing", CYAN, "molecule"),
        (880, 425, "POE specialist", "P0/P1 kernels\n139-asset lineage", PURPLE, "database"),
    ]
    for x, y, title_value, detail, color, icon in cards:
        node_card(
            parts,
            x,
            y,
            248,
            170,
            title_value,
            detail,
            color,
            icon=icon,
            tag="DELIVERED",
        )
        start_x = x + 248 if x < center_x else x
        end_x = center_x - 94 if x < center_x else center_x + 94
        start_y = y + 85
        parts.append(
            line(
                start_x,
                start_y,
                end_x,
                center_y + (start_y - center_y) * 0.25,
                stroke=DIM,
                width=2,
                arrow=x < center_x,
            )
        )
    parts.append(pill(500, 190, "TRACEABLE", GREEN, width=95))
    parts.append(pill(605, 190, "AUDITABLE", CYAN, width=95))
    parts.append(pill(710, 190, "OPERATIONAL", BLUE, width=108))
    footer_gate(parts)
    return finish(parts)


def render_linear(
    title_value: str,
    subtitle: str,
    stages: list[tuple[str, str, str, str]],
    *,
    footer: str,
    eyebrow: str = "DECISION FLOW",
) -> str:
    parts = svg_start(title_value, subtitle)
    header(parts, title_value, subtitle, eyebrow=eyebrow, accent=CYAN)
    count = len(stages)
    margin = 56
    gap = 18
    card_width = (W - 2 * margin - gap * (count - 1)) / count
    y, height = 228, 308
    for index, (stage_title, detail, color, icon) in enumerate(stages):
        x = margin + index * (card_width + gap)
        node_card(
            parts,
            x,
            y,
            card_width,
            height,
            stage_title,
            detail,
            color,
            icon=icon,
            tag=f"{index+1:02d}",
        )
        if index < count - 1:
            parts.append(
                line(
                    x + card_width,
                    y + height / 2,
                    x + card_width + gap - 2,
                    y + height / 2,
                    stroke=DIM,
                    width=2,
                    arrow=True,
                )
            )
    footer_gate(parts, footer)
    return finish(parts)


def render_layers() -> str:
    parts = svg_start(
        "Layered process-package architecture",
        "A layered scientific and engineering architecture with explicit evidence and approval boundaries.",
    )
    header(
        parts,
        "Layered process-package architecture",
        "Every decision layer is supported by governed models, data and approvals",
        eyebrow="SYSTEM ARCHITECTURE",
    )
    layers = [
        ("Decision & acceptance", "targets · CQAs · trade-offs · Gate state · named approval", BLUE),
        ("Process & equipment", "streams · balances · reactors · separation · utilities · controls", CYAN),
        ("Models & computation", "kinetics · thermo · transport · estimation · uncertainty · simulation", PURPLE),
        ("Evidence & identity", "sources · assumptions · conflicts · manifests · provenance · audit trail", GREEN),
    ]
    y = 210
    widths = [1040, 980, 920, 860]
    for index, (layer_title, detail, color) in enumerate(layers):
        width = widths[index]
        x = (W - width) / 2
        height = 90
        parts.append(rect(x, y, width, height, fill=SURFACE, stroke=f"{color}77", radius=18, shadow=True))
        parts.append(rect(x, y, 7, height, fill=color, stroke=color, radius=3))
        parts.append(text(x + 30, y + 38, layer_title, size=20, weight=780))
        parts.append(text(x + 30, y + 65, detail, size=13, fill=MUTED, mono=True))
        if index < len(layers) - 1:
            parts.append(line(600, y + height, 600, y + height + 25, stroke=DIM, width=2, arrow=True))
        y += 110
    footer_gate(parts)
    return finish(parts)


def render_data_model() -> str:
    parts = svg_start(
        "Universal process-package data model",
        "Connected data entities for decisions, models, equipment, evidence and approvals.",
    )
    header(
        parts,
        "Connected process-package data model",
        "IDs and references turn narrative reports into an auditable engineering graph",
        eyebrow="CONNECTED DATA MODEL",
    )
    center_x, center_y = 600, 392
    parts.append(circle(center_x, center_y, 86, fill="#0E223B", stroke=BLUE, width=2))
    small_icon(parts, center_x, center_y - 26, "database", BLUE)
    parts.append(text(center_x, center_y + 18, "DESIGN BASIS", size=19, weight=800, anchor="middle"))
    parts.append(
        text(
            center_x,
            center_y + 42,
            "scope · units · limits",
            size=11,
            fill=MUTED,
            mono=True,
            anchor="middle",
        )
    )
    nodes = [
        (160, 232, "Streams", "components · flow · state", CYAN, "flow"),
        (160, 468, "Equipment", "duty · capacity · envelope", BLUE, "cpu"),
        (860, 232, "Models", "equations · parameters · domain", PURPLE, "chart"),
        (860, 468, "Controls & HSE", "alarms · trips · safeguards", RED, "shield"),
        (430, 205, "Evidence", "source · condition · uncertainty", GREEN, "database"),
        (650, 525, "Acceptance", "criterion · approver · status", AMBER, "shield"),
    ]
    for x, y, node_title, detail, color, icon in nodes:
        node_card(parts, x, y, 220, 118, node_title, detail, color, icon=icon)
        parts.append(
            line(
                center_x,
                center_y,
                x + 110,
                y + 59,
                stroke=f"{color}88",
                width=1.6,
                arrow=True,
            )
        )
    footer_gate(parts)
    return finish(parts)


def render_integration() -> str:
    parts = svg_start(
        "Simulator-neutral integration contract",
        "Governed inputs and qualified outputs around multiple simulation and automation tools.",
    )
    header(
        parts,
        "Simulator-neutral integration contract",
        "A simulator is a computation engine—not a substitute for design basis, evidence or approval",
        eyebrow="INTEROPERABILITY",
    )
    node_card(
        parts,
        52,
        230,
        250,
        310,
        "Governed inputs",
        "design basis\nstream & equipment IDs\nproperty-method basis\nparameter provenance\nmodel passport",
        BLUE,
        icon="database",
        tag="SOURCE OF TRUTH",
    )
    node_card(
        parts,
        898,
        230,
        250,
        310,
        "Qualified outputs",
        "balances & residuals\napplicability domain\nuncertainty & conflicts\nGate status\nnamed approval",
        GREEN,
        icon="shield",
        tag="DECISION READY",
    )
    tools = [
        (370, 215, "Aspen Plus", BLUE),
        (630, 215, "Aspen HYSYS", CYAN),
        (370, 350, "DWSIM", TEAL),
        (630, 350, "Python / custom", PURPLE),
        (500, 485, "DCS / PLC exchange", AMBER),
    ]
    for x, y, label, color in tools:
        parts.append(rect(x, y, 200, 86, fill=SURFACE, stroke=f"{color}66", radius=18, shadow=True))
        small_icon(parts, x + 38, y + 43, "cpu", color)
        parts.append(text(x + 70, y + 49, label, size=16, weight=750))
        parts.append(line(302, 385, x, y + 43, stroke=DIM, width=1.5, arrow=True))
        parts.append(line(x + 200, y + 43, 898, 385, stroke=DIM, width=1.5, arrow=True))
    footer_gate(parts, "SIMULATOR CONVERGENCE ≠ QUALIFICATION")
    return finish(parts)


def render_network() -> str:
    parts = svg_start(
        "EPDM catalyst-to-architecture network",
        "Reaction network linking active sites, monomers, transfer, deactivation and molecular architecture.",
    )
    header(
        parts,
        "EPDM catalyst → kinetics → architecture",
        "A compact network view of insertion, loss pathways and structure-forming consequences",
        eyebrow="EPDM FLAGSHIP",
    )
    center_x, center_y = 560, 365
    parts.append(circle(center_x, center_y, 74, fill="#0E223B", stroke=CYAN, width=2))
    small_icon(parts, center_x, center_y - 20, "molecule", CYAN)
    parts.append(text(center_x, center_y + 20, "ACTIVE SITE", size=18, weight=800, anchor="middle"))
    monomers = [
        (180, 240, "Ethylene", "E insertion", BLUE),
        (180, 365, "Propylene", "P insertion", TEAL),
        (180, 490, "Diene", "third-monomer topology", PURPLE),
    ]
    for x, y, label, detail, color in monomers:
        node_card(parts, x, y, 230, 92, label, detail, color, icon="molecule")
        parts.append(
            line(
                x + 230,
                y + 46,
                center_x - 75,
                center_y + (y + 46 - center_y) * 0.25,
                stroke=f"{color}AA",
                width=2,
                arrow=True,
                blue_arrow=color == BLUE,
            )
        )
    losses = [
        (790, 235, "Chain transfer", "MWD · chain birth", AMBER),
        (790, 365, "Deactivation", "site lifetime", RED),
        (790, 495, "Poison memory", "recycle impurity risk", ORANGE),
    ]
    for x, y, label, detail, color in losses:
        node_card(parts, x, y, 250, 92, label, detail, color, icon="shield")
        parts.append(
            line(
                center_x + 75,
                center_y + (y + 46 - center_y) * 0.25,
                x,
                y + 46,
                stroke=f"{color}99",
                width=2,
                arrow=True,
            )
        )
    parts.append(rect(430, 565, 340, 58, fill=f"{GREEN}14", stroke=f"{GREEN}77", radius=16))
    parts.append(
        text(
            600,
            592,
            "sequence · MWD/CCD · branching · gel risk",
            size=15,
            fill=GREEN,
            weight=750,
            anchor="middle",
        )
    )
    parts.append(line(center_x, center_y + 74, 600, 565, stroke=GREEN, width=2, arrow=True))
    footer_gate(parts)
    return finish(parts)


def render_reactor_map() -> str:
    parts = svg_start(
        "EPDM reactor-mode decision map",
        "Decision map for semibatch, continuous and multi-reactor EPDM process routes.",
    )
    header(
        parts,
        "EPDM reactor-mode decision map",
        "Choose the operating mode from control objective, heat removal, composition and grade-transition needs",
        eyebrow="REACTOR SYNTHESIS",
    )
    parts.append(rect(430, 195, 340, 78, fill=SURFACE_2, stroke=BLUE, radius=20, shadow=True))
    parts.append(text(600, 230, "What must the reactor preserve?", size=20, weight=800, anchor="middle"))
    parts.append(
        text(
            600,
            253,
            "composition · temperature · site state · residence history",
            size=12,
            fill=MUTED,
            anchor="middle",
            mono=True,
        )
    )
    branches = [
        (75, 355, "Semibatch", "flexible feed policy\nstrong grade agility\nexplicit inventory history", CYAN, "screening / lab / specialty"),
        (450, 355, "Continuous", "steady throughput\nresidence distribution\nrecycle closure", BLUE, "industrial steady state"),
        (825, 355, "Multi-reactor", "sequence shaping\nsplit heat load\nbroader architecture control", PURPLE, "advanced product envelope"),
    ]
    for x, y, label, detail, color, tag in branches:
        node_card(parts, x, y, 300, 220, label, detail, color, icon="flow", tag=tag.upper())
        parts.append(line(600, 273, x + 150, y, stroke=f"{color}88", width=2, arrow=True))
    footer_gate(parts, "MODE SELECTION REQUIRES HEAT, MIXING, PHASE AND OPERABILITY EVIDENCE")
    return finish(parts)


def render_flowsheet() -> str:
    stages = [
        ("Feed & catalyst", "E / P / diene\nsolvent · catalyst\npoison boundary", BLUE, "molecule"),
        ("Polymerization", "active sites\nheat removal\nmixing & residence", CYAN, "cpu"),
        ("Quench & deash", "kill chemistry\nmetal removal\nwash closure", TEAL, "shield"),
        ("Devolatilize", "solvent / monomer\nnon-equilibrium\nresidual target", PURPLE, "flow"),
        ("Recovery", "compression\ncondensation\npurification", GREEN, "database"),
        ("Product", "bale / pellet\nMooney · gel\ncustomer evidence", AMBER, "chart"),
    ]
    return render_linear(
        "EPDM process-package reference flowsheet",
        "Mechanism-aware polymerization connected to finishing, recovery and product evidence",
        stages,
        footer="RECYCLE, PURGE AND EMISSIONS MUST CLOSE",
        eyebrow="PROCESS FLOWSHEET",
    )


def render_recycle() -> str:
    parts = svg_start(
        "EPDM recovery, recycle and impurity-risk loop",
        "Closed recycle loop showing recovery, guard beds, poison memory and purge.",
    )
    header(
        parts,
        "Recovery, recycle and impurity-risk loop",
        "Recycle economics are valid only when impurities and catalyst poisons reach a finite steady state",
        eyebrow="RECYCLE CLOSURE",
    )
    center_x, center_y = 600, 390
    ring = [
        (600, 205, "Devolatilization", PURPLE, "flow"),
        (880, 310, "Recovery", GREEN, "database"),
        (800, 530, "Guard & purge", AMBER, "shield"),
        (400, 560, "Recycle header", CYAN, "flow"),
        (300, 310, "Reactor", BLUE, "molecule"),
    ]
    for x, y, label, color, icon in ring:
        parts.append(circle(x, y, 68, fill=SURFACE, stroke=f"{color}88", width=2))
        small_icon(parts, x, y - 13, icon, color)
        parts.append(text(x, y + 30, label, size=14, weight=750, anchor="middle"))
    rotated = ring[1:] + ring[:1]
    for source, destination in zip(ring, rotated, strict=True):
        x1, y1 = source[0], source[1]
        x2, y2 = destination[0], destination[1]
        parts.append(
            path(
                f"M {x1} {y1} Q {(x1+x2)/2} {(y1+y2)/2-20} {x2} {y2}",
                stroke=DIM,
                width=2,
                arrow=True,
            )
        )
    parts.append(circle(center_x, center_y, 92, fill="#0D2038", stroke=RED, width=2))
    small_icon(parts, center_x, center_y - 22, "shield", RED)
    parts.append(text(center_x, center_y + 15, "POISON MEMORY", size=18, weight=800, anchor="middle"))
    parts.append(
        text(
            center_x,
            center_y + 42,
            "accumulation · finite steady state",
            size=11,
            fill=MUTED,
            mono=True,
            anchor="middle",
        )
    )
    footer_gate(parts, "NO FINITE IMPURITY STEADY STATE → HOLD")
    return finish(parts)


def render_evidence() -> str:
    parts = svg_start(
        "Evidence and qualification gates",
        "Evidence-state ladder separating calculation, inference, proposal and approval.",
    )
    header(
        parts,
        "Evidence and qualification gates",
        "Claims advance only when their source, condition, uncertainty and accountable approval are explicit",
        eyebrow="EVIDENCE OPERATING MODEL",
    )
    states = [
        ("OBSERVED", "measured in project", GREEN),
        ("REPORTED", "external source", CYAN),
        ("CALCULATED", "transparent model", BLUE),
        ("INFERRED", "bounded interpretation", PURPLE),
        ("ASSUMED", "explicit placeholder", AMBER),
        ("PROPOSED", "future action", ORANGE),
        ("APPROVED", "named authority", GREEN),
    ]
    x0, y0 = 70, 235
    width, height, gap = 138, 230, 18
    for index, (state, detail, color) in enumerate(states):
        x = x0 + index * (width + gap)
        parts.append(rect(x, y0, width, height, fill=SURFACE, stroke=f"{color}77", radius=18, shadow=True))
        parts.append(text(x + 18, y0 + 40, f"{index+1:02d}", size=12, fill=color, mono=True, weight=700))
        parts.append(text(x + 18, y0 + 80, state, size=16, fill=TEXT, mono=True, weight=800))
        parts.append(multiline(x + 18, y0 + 116, detail, width_chars=15, size=13, fill=MUTED, line_height=19))
        if index < len(states) - 1:
            parts.append(line(x + width, y0 + height / 2, x + width + gap - 2, y0 + height / 2, stroke=DIM, width=1.7, arrow=True))
    parts.append(rect(155, 515, 890, 78, fill="#0A1627", stroke=BORDER, radius=18))
    parts.append(text(600, 546, "Required metadata", size=14, fill=BLUE, weight=800, anchor="middle", mono=True))
    parts.append(
        text(
            600,
            575,
            "source ID · locator · date · units · method boundary · uncertainty · conflict · reviewer",
            size=14,
            fill=MUTED,
            anchor="middle",
        )
    )
    footer_gate(parts, "MISSING EVIDENCE → HOLD / NOT_EVALUATED")
    return finish(parts)


def render_verification() -> str:
    stages = [
        ("Source identity", "manifest\nversion anchors\nrepository doctor", GREEN, "database"),
        ("Static checks", "compile · Ruff\nschemas · links\n18 SVG rebuild", BLUE, "shield"),
        ("Scientific tests", "pytest · coverage\nknown solutions\nadversarial cases", CYAN, "chart"),
        ("Wheel content", "four-Skill tree\nreports · scripts\nMETADATA", PURPLE, "database"),
        ("Real install", "pip --target\nclean venv\norigin checks", TEAL, "cpu"),
        ("Release Gate", "performance\nsnapshot\nimmutable status", AMBER, "shield"),
    ]
    return render_linear(
        "Verification and release pipeline",
        "Every release is rebuilt, installed and checked from its own declared source identity",
        stages,
        footer="NO TEST OR INSTALL EVIDENCE → NO RELEASE",
        eyebrow="RELEASE QUALIFICATION",
    )


def render_batch_scan() -> str:
    parts = svg_start(
        "EPDM batch parameter-scan data flow",
        "Broadcast arrays pass through validated EPDM screening kernels to decision-ready outputs.",
    )
    header(
        parts,
        "EPDM batch parameter-scan data flow",
        "One boundary validation, NumPy broadcasting and explicit scenario dimensions for large screening studies",
        eyebrow="BATCH COMPUTING",
        accent=TEAL,
    )
    columns = [
        (52, "Scenario arrays", "temperature\nresidence time\nactive-site basis\nactivity multiplier", BLUE, "database"),
        (300, "Shape contract", "broadcast-compatible\nfinite values\npositive domains", CYAN, "shield"),
        (548, "Vectorized kernel", "Arrhenius arrays\nufunc conversions\nno numpy.vectorize", TEAL, "cpu"),
        (796, "Decision outputs", "E/P/diene conversion\nshape metadata\nscenario count", GREEN, "chart"),
    ]
    tags = ["INPUT", "VALIDATE", "COMPUTE", "OUTPUT"]
    for index, (x, label, detail, color, icon) in enumerate(columns):
        node_card(parts, x, 225, 215, 300, label, detail, color, icon=icon, tag=tags[index])
        if index < 3:
            parts.append(line(x + 215, 375, x + 245, 375, stroke=DIM, width=2, arrow=True))
    parts.append(rect(1030, 225, 118, 300, fill="#0D2038", stroke=AMBER, radius=20, shadow=True))
    parts.append(text(1089, 265, "GATE", size=13, fill=AMBER, mono=True, weight=800, anchor="middle"))
    parts.append(text(1089, 335, "≥3× gate", size=22, fill=TEXT, weight=850, anchor="middle"))
    parts.append(text(1089, 364, "1,000 cases", size=11, fill=MUTED, mono=True, anchor="middle"))
    parts.append(pill(1045, 405, "PARITY", GREEN, width=88))
    parts.append(pill(1045, 447, "NO DRIFT", BLUE, width=88))
    footer_gate(parts, "BROADCASTING IS USED ONLY FOR HOMOGENEOUS ARRAY KERNELS")
    return finish(parts)


def render_perf_gate() -> str:
    parts = svg_start(
        "Performance regression qualification gate",
        "Baseline and candidate workloads are compared on timing, memory, scale and numerical identity.",
    )
    header(
        parts,
        "Performance regression qualification gate",
        "Optimization claims survive only when results, memory and scale behavior remain within declared limits",
        eyebrow="PERFORMANCE EVIDENCE",
        accent=AMBER,
    )
    node_card(parts, 52, 225, 210, 300, "Frozen baseline", "same runner\nsame inputs\nsame repeats\nversioned JSON", BLUE, icon="database", tag="ALPHA.10")
    node_card(parts, 300, 225, 210, 300, "Candidate run", "warm-ups\nmedian timing\npeak memory\ncProfile", CYAN, icon="chart", tag="ALPHA.11")
    node_card(parts, 548, 225, 260, 300, "Parity policy", "exact digest\nanalytical tolerance\nsemantic contract\nscale normalization", PURPLE, icon="shield", tag="FAIL-CLOSED")
    parts.append(line(262, 375, 300, 375, stroke=DIM, width=2, arrow=True))
    parts.append(line(510, 375, 548, 375, stroke=DIM, width=2, arrow=True))
    outcomes = [
        (845, 238, "PASS", "speed + parity", GREEN),
        (845, 338, "HOLD", "evidence missing", AMBER),
        (845, 438, "FAIL", "drift / regression", RED),
    ]
    for x, y, label, detail, color in outcomes:
        parts.append(rect(x, y, 303, 75, fill=f"{color}12", stroke=f"{color}88", radius=18, shadow=True))
        small_icon(parts, x + 38, y + 38, "shield", color)
        parts.append(text(x + 72, y + 34, label, size=16, fill=color, weight=850, mono=True))
        parts.append(text(x + 72, y + 56, detail, size=12, fill=MUTED))
        parts.append(line(808, 375, x, y + 38, stroke=f"{color}88", width=1.5, arrow=True))
    footer_gate(parts, "PERFORMANCE PASS ≠ SCIENTIFIC OR INDUSTRIAL APPROVAL")
    return finish(parts)


def render_three_levels() -> str:
    parts = svg_start(
        "Three EPDM model levels",
        "Screening, engineering and detailed-reference model levels with increasing evidence requirements.",
    )
    header(
        parts,
        "Three EPDM model levels",
        "Fidelity increases only when the decision and available evidence justify the added complexity",
        eyebrow="MULTIFIDELITY MODELING",
    )
    cards = [
        (70, 225, "Level 1 · Screening", "active-site normalization\nE/P/diene insertion\nrapid conversions\ninput boundary checks", BLUE, "fast ranking"),
        (450, 225, "Level 2 · Engineering", "Arrhenius correction\nsemibatch balances\nheat & mixing\nrecycle / devolatilization", CYAN, "flowsheet studies"),
        (830, 225, "Level 3 · Detailed", "site families\nchain moments\nbranching / gel\nphase & entropy references", PURPLE, "high-fidelity decision"),
    ]
    icons = ["chart", "cpu", "molecule"]
    for index, (x, y, label, detail, color, tag) in enumerate(cards):
        node_card(parts, x, y, 300, 330, label, detail, color, icon=icons[index], tag=tag.upper(), title_size=19)
        if index < 2:
            parts.append(line(x + 300, y + 165, x + 380, y + 165, stroke=DIM, width=2, arrow=True))
    footer_gate(parts, "ALL LEVELS RETURN CALCULATED_REFERENCE_ONLY")
    return finish(parts)


def render_multiscale() -> str:
    stages = [
        ("Catalyst & sites", "chemistry\nsite families\npoison boundary", BLUE, "molecule"),
        ("Chain events", "insertion\ntransfer\ndeactivation", CYAN, "flow"),
        ("Architecture", "sequence\nMWD / CCD\nbranching / gel", PURPLE, "chart"),
        ("Phase & transport", "solubility\nviscosity\nmixing / heat", TEAL, "cpu"),
        ("Reactor & process", "mode\nresidence\nrecycle / finishing", GREEN, "flow"),
        ("Product evidence", "Mooney\ncompound / cure\ncustomer line", AMBER, "shield"),
    ]
    return render_linear(
        "EPDM multiscale mechanism-to-package chain",
        "A continuous evidence path from catalyst chemistry to process-package acceptance",
        stages,
        footer="BROKEN SCALE LINK → HOLD",
        eyebrow="MULTISCALE CHAIN",
    )


def render_identifiability() -> str:
    stages = [
        ("Data boundary", "conditions · units\nsite basis · covariance", BLUE, "database"),
        ("Sensitivity", "local / global\nobservable response", CYAN, "chart"),
        ("Identifiability", "rank · correlation\nprofile likelihood", PURPLE, "cpu"),
        ("Uncertainty", "parameter / prediction\nscenario propagation", AMBER, "chart"),
        ("Decision Gate", "experiment · model\nscale-up / HOLD", GREEN, "shield"),
    ]
    return render_linear(
        "EPDM parameter identifiability and uncertainty",
        "Model fidelity advances only when experiments distinguish the parameters that drive the decision",
        stages,
        footer="NON-IDENTIFIABLE PARAMETERS REMAIN EXPLICIT",
        eyebrow="MODEL CONFIDENCE",
    )


def render_product_bridge() -> str:
    stages = [
        ("Raw polymer", "composition · MWD\nMooney · gel", BLUE, "molecule"),
        ("Compound", "fixed recipe\nmixing history", CYAN, "flow"),
        ("Cure", "rheometer\ncrosslink state", PURPLE, "chart"),
        ("Part", "geometry\naging · durability", TEAL, "cpu"),
        ("Customer line", "processing window\nquality evidence", GREEN, "database"),
        ("Approval", "named owner\nacceptance record", AMBER, "shield"),
    ]
    return render_linear(
        "EPDM raw-polymer-to-customer evidence bridge",
        "A reactor result becomes a product claim only through controlled formulation and qualification",
        stages,
        footer="REACTOR RESULT ≠ CUSTOMER CLAIM",
        eyebrow="PRODUCT QUALIFICATION",
    )


def render_dependency_lock() -> str:
    stages = [
        ("Dependency intent", "pyproject ranges\nruntime + dev extras", BLUE, "database"),
        ("Deterministic resolver", "Python 3.11\nbacktracking resolver", CYAN, "cpu"),
        ("Exact hashed lock", "name == version\nSHA-256 per artifact", PURPLE, "shield"),
        ("Clean installation", "--require-hashes\nno implicit upgrades", TEAL, "flow"),
        ("Vulnerability audit", "pip-audit\nmachine JSON evidence", AMBER, "chart"),
        ("Release Gate", "lock identity\nsource provenance", GREEN, "shield"),
    ]
    return render_linear(
        "Hashed dependency supply-chain gate",
        "Declared ranges become an exact, auditable and fail-closed installation contract",
        stages,
        footer="UNPINNED, UNHASHED OR VULNERABLE DEPENDENCY → HOLD",
        eyebrow="SOFTWARE SUPPLY CHAIN",
    )


def render_snapshot_self_validation() -> str:
    stages = [
        ("Source manifest", "canonical paths\nSHA-256 + bytes", BLUE, "database"),
        ("Snapshot staging", "manifest + overlay\nruntime support files", CYAN, "flow"),
        ("Identity metadata", "snapshot contract\nrelease SBOM", PURPLE, "database"),
        ("Re-extracted tree", "portable source\nno hidden checkout state", TEAL, "flow"),
        ("Self-validation", "provenance\nmetadata + Doctor", GREEN, "shield"),
        ("Archive digest", "deterministic ZIP\nexternal SHA-256", AMBER, "shield"),
    ]
    return render_linear(
        "Self-validating source snapshot",
        "The exported source must pass the same integrity rules after extraction",
        stages,
        footer="ARCHIVE CREATED ≠ ARCHIVE QUALIFIED",
        eyebrow="REPRODUCIBLE SOURCE DELIVERY",
    )


def render_main_only_delivery() -> str:
    stages = [
        ("main commit", "single authority\nno feature branch", BLUE, "database"),
        ("Qualification matrix", "Windows + Linux\nPython 3.11–3.14", CYAN, "cpu"),
        ("Evidence artifacts", "tests · coverage\nwheel · snapshot", PURPLE, "chart"),
        ("Atomic finalization", "lock + reports\nself-delete workflow", TEAL, "flow"),
        ("Branch cleanup", "delete stale refs\nretain commit history", AMBER, "shield"),
        ("main only", "auditable head\nreproducible release", GREEN, "shield"),
    ]
    return render_linear(
        "Main-only delivery lifecycle",
        "A one-shot release path qualifies the exact tree before removing obsolete branches",
        stages,
        footer="DELETE BRANCHES ONLY AFTER QUALIFICATION PASS",
        eyebrow="REPOSITORY GOVERNANCE",
    )


ASSETS = {
    "tsao-process-intelligence-os.svg": render_platform,
    "universal-process-package.svg": lambda: render_linear(
        "Universal process-package lifecycle",
        "One decision-centered lifecycle from design basis to technology transfer",
        [
            ("Design basis", "scope · targets\ncomponents · units\nacceptance criteria", BLUE, "database"),
            ("Evidence & models", "data boundary\nthermo · kinetics\nuncertainty", CYAN, "chart"),
            ("Process synthesis", "reactor · separation\nutilities · equipment\nbalances", TEAL, "flow"),
            ("Control & HSE", "alarms · interlocks\nabnormal cases\nsafety interfaces", RED, "shield"),
            ("Scale-up & TEA", "similarity breaks\npilot evidence\nCAPEX / OPEX", PURPLE, "chart"),
            ("Package & transfer", "documents · owners\nGate matrix\noperating handover", GREEN, "database"),
        ],
        footer="MISSING EVIDENCE OR APPROVAL → HOLD",
        eyebrow="PROCESS-PACKAGE LIFECYCLE",
    ),
    "process-package-architecture.svg": render_layers,
    "process-package-data-model.svg": render_data_model,
    "control-safety-cause-effect.svg": lambda: render_linear(
        "Control, interlock and process-safety chain",
        "Normal control and independent protection remain connected but explicitly separated",
        [
            ("Measurement", "sensor · analyzer\nmeasurement boundary", BLUE, "chart"),
            ("Regulatory control", "PID · cascade\nconstraint control", CYAN, "cpu"),
            ("Alarm & operator", "priority · response\nabnormal procedure", AMBER, "shield"),
            ("Interlock / SIS", "trip · permissive\nindependent function", RED, "shield"),
            ("Relief & containment", "relief · flare\nsecondary containment", PURPLE, "shield"),
            ("Evidence Gate", "test · approval\nMOC · learning", GREEN, "database"),
        ],
        footer="QUALIFIED TEAMS OWN THE SAFETY DECISION",
        eyebrow="CONTROL & PROCESS SAFETY",
    ),
    "simulation-integration-contract.svg": render_integration,
    "epdm-multiscale-chain.svg": render_multiscale,
    "epdm-catalyst-kinetics-network.svg": render_network,
    "epdm-three-level-models.svg": render_three_levels,
    "epdm-reactor-mode-map.svg": render_reactor_map,
    "epdm-identifiability-uncertainty.svg": render_identifiability,
    "epdm-product-customer-bridge.svg": render_product_bridge,
    "epdm-process-flowsheet.svg": render_flowsheet,
    "recovery-recycle-risk-loop.svg": render_recycle,
    "evidence-gate-system.svg": render_evidence,
    "verification-pipeline.svg": render_verification,
    "batch-parameter-scan.svg": render_batch_scan,
    "performance-regression-gate.svg": render_perf_gate,
    "dependency-lock-supply-chain.svg": render_dependency_lock,
    "source-snapshot-self-validation.svg": render_snapshot_self_validation,
    "main-only-delivery-lifecycle.svg": render_main_only_delivery,
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, renderer in ASSETS.items():
        (OUT / name).write_text(renderer(), encoding="utf-8")
    print(f"generated {len(ASSETS)} UI/UX Pro Max-aligned README assets in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
