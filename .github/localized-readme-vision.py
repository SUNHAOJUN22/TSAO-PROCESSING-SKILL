from __future__ import annotations

from html import escape
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CONFIG = {'repo': 'TSAO-PROCESSING-SKILL', 'readmes': {'zh': 'README.zh-CN.md', 'en': 'README.md'}, 'paths': {'zh': 'docs/localized-vision/process-intelligence-vision-zh.svg', 'en': 'docs/localized-vision/process-intelligence-vision-en.svg'}, 'anchors': {'zh': '**面向化工过程 Skill、受治理数理模型、证据链、来源身份和验收交付的 fail-closed 软件系统。**', 'en': '**Fail-closed software delivery for chemical-process Skills, governed mathematics, evidence, provenance and acceptance.**'}, 'zh': {'eyebrow': 'TSAO PROCESS INTELLIGENCE OS · 从机理到牌号', 'title': '从反应机理到材料牌号与工艺窗口', 'subtitle': '证据登记 · 动力学/衡算 · 群体矩/形貌 · 可辨识性/UQ · 规范发布', 'vision_label': '项目愿景', 'vision': '构建“基本方程—材料结构—工艺条件—产品牌号”的可解释数字线程', 'vision_note': '软件合同先闭合；工业配方、设备、HSE 和客户批准保持外部责任。', 'formula_label': '核心过程与材料合同', 'formula_rows': ['dN/dt = Fin z − Fout x + Vνᵀr   ·   k(T)=A exp(−E/RT)', 'μₖ=Σ pᵏnₚ   ·   Đ=μ₀μ₂/μ₁²   ·   F=SᵀWS   ·   Var[g]≈∇gᵀCov(θ)∇g'], 'cards': [{'title': '证据与参数', 'subtitle': 'Evidence · Applicability', 'formula': 'θ ↔ source ↔ domain', 'formula_note': '参数不可脱离证据', 'lines': ['来源与版本', '单位/温压范围', '适用域与责任人']}, {'title': '动力学与衡算', 'subtitle': 'Kinetics · Mass · Energy', 'formula': 'rⱼ=kⱼaₛ∏Cᵢᵅⁱʲ', 'formula_note': '先守恒后优化', 'lines': ['反应网络', '物料能量闭合', '热效应与停留时间']}, {'title': '群体与结构', 'subtitle': 'Moments · Morphology', 'formula': 'Mn∝μ₁/μ₀', 'formula_note': '结构到性能桥接', 'lines': ['分子量分布', '序列/支化', '相态与形貌']}, {'title': '可辨识性与UQ', 'subtitle': 'Fisher · Sensitivity', 'formula': 'F=SᵀWS', 'formula_note': '奇异信息返回 HOLD', 'lines': ['参数相关性', '置信域与传播', '下一实验选择']}, {'title': '规范发布', 'subtitle': 'Canonical Contract', 'formula': 'H=SHA256(canonical bytes)', 'formula_note': '来源树与 Wheel 同源', 'lines': ['Schema 闭合', '不可变发布', '验收与交接']}], 'disclaimer': 'AI辅助概念设计 · 非科学数据 · 公式对应软件合同而非运行结果', 'footer': 'TSAO Process Intelligence OS · 中文愿景', 'accessible_title': 'TSAO Process Intelligence OS 中文项目愿景图', 'accessible_desc': '从证据参数、动力学衡算、群体矩结构、可辨识性不确定度到规范发布的中文概念设计图。', 'readme_heading': '中文项目愿景图：从反应机理到材料牌号与工艺窗口', 'readme_alt': 'TSAO 化工过程智能操作系统中文愿景与数理架构', 'readme_note': '图中公式映射当前过程、EPDM、POE 与聚合物通用 Skill 的软件合同；它不是装置标定、客户牌号认证或 HSE 结论。'}, 'en': {'eyebrow': 'TSAO PROCESS INTELLIGENCE OS · FROM MECHANISM TO GRADE', 'title': 'From Reaction Mechanisms to Material Grades and Process Windows', 'subtitle': 'Evidence registration · kinetics/balances · moments/morphology · identifiability/UQ · canonical publication', 'vision_label': 'VISION', 'vision': 'Build an explainable digital thread from governing equations to structure, process and product grade', 'vision_note': 'Software contracts close first; formulation, equipment, HSE and customer approval remain external.', 'formula_label': 'CORE PROCESS AND MATERIAL CONTRACTS', 'formula_rows': ['dN/dt = Fin z − Fout x + Vνᵀr   ·   k(T)=A exp(−E/RT)', 'μₖ=Σ pᵏnₚ   ·   Đ=μ₀μ₂/μ₁²   ·   F=SᵀWS   ·   Var[g]≈∇gᵀCov(θ)∇g'], 'cards': [{'title': 'Evidence & parameters', 'subtitle': 'Evidence · Applicability', 'formula': 'θ ↔ source ↔ domain', 'formula_note': 'parameters retain evidence', 'lines': ['source & version', 'unit/T/P range', 'domain & owner']}, {'title': 'Kinetics & balances', 'subtitle': 'Kinetics · Mass · Energy', 'formula': 'rⱼ=kⱼaₛ∏Cᵢᵅⁱʲ', 'formula_note': 'conservation before optimization', 'lines': ['reaction network', 'mass/energy closure', 'thermal and residence time']}, {'title': 'Population & structure', 'subtitle': 'Moments · Morphology', 'formula': 'Mn∝μ₁/μ₀', 'formula_note': 'structure-performance bridge', 'lines': ['molecular-weight distribution', 'sequence & branching', 'phase and morphology']}, {'title': 'Identifiability & UQ', 'subtitle': 'Fisher · Sensitivity', 'formula': 'F=SᵀWS', 'formula_note': 'singularity returns HOLD', 'lines': ['parameter correlation', 'confidence propagation', 'next-experiment choice']}, {'title': 'Canonical publication', 'subtitle': 'Schema · Provenance', 'formula': 'H=SHA256(canonical bytes)', 'formula_note': 'source and Wheel identity', 'lines': ['reference closure', 'immutable release', 'acceptance handover']}], 'disclaimer': 'AI-ASSISTED CONCEPTUAL DESIGN · NOT SCIENTIFIC DATA', 'footer': 'TSAO Process Intelligence OS · English vision', 'accessible_title': 'TSAO Process Intelligence OS English project vision', 'accessible_desc': 'English conceptual design from evidence and parameters through kinetics, population structure, identifiability and canonical publication.', 'readme_heading': 'Project vision: from reaction mechanisms to grades and process windows', 'readme_alt': 'TSAO Process Intelligence OS English vision and mathematical architecture', 'readme_note': 'The formulas map to the implemented process, EPDM, POE and polymer-general Skill contracts. This is not plant calibration, customer-grade certification or an HSE decision.'}}

FONT = "Inter,'Noto Sans SC','Noto Sans CJK SC','Microsoft YaHei','PingFang SC','WenQuanYi Micro Hei','Segoe UI',Arial,sans-serif"
MATH_FONT = "'STIX Two Math','Cambria Math','Noto Sans Math','Noto Sans SC',serif"


def text(value: object) -> str:
    return escape(str(value), quote=True)


def render_svg(spec: dict[str, object]) -> str:
    cards = list(spec['cards'])
    colors = ['#22d3ee', '#818cf8', '#c084fc', '#34d399', '#fbbf24']
    x_positions = [78, 370, 662, 954, 1246]
    card_markup: list[str] = []
    for index, card in enumerate(cards):
        x = x_positions[index]
        color = colors[index]
        lines = list(card['lines'])
        formula = card['formula']
        card_markup.append(f'''<g transform="translate({x} 250)" filter="url(#shadow)">
  <rect width="250" height="390" rx="26" fill="#0d2034" stroke="{color}" stroke-width="2"/>
  <circle cx="42" cy="42" r="23" fill="{color}"/><text x="42" y="48" text-anchor="middle" class="step">{index + 1}</text>
  <text x="24" y="93" class="card-title">{text(card['title'])}</text>
  <text x="24" y="124" class="card-sub">{text(card['subtitle'])}</text>
  <rect x="20" y="151" width="210" height="76" rx="15" fill="#081522" stroke="#334155"/>
  <text x="125" y="184" text-anchor="middle" class="formula-small">{text(formula)}</text>
  <text x="125" y="207" text-anchor="middle" class="micro">{text(card['formula_note'])}</text>
  <circle cx="34" cy="274" r="6" fill="{color}"/><text x="51" y="280" class="body">{text(lines[0])}</text>
  <circle cx="34" cy="316" r="6" fill="{color}"/><text x="51" y="322" class="body">{text(lines[1])}</text>
  <circle cx="34" cy="358" r="6" fill="{color}"/><text x="51" y="364" class="body">{text(lines[2])}</text>
</g>''')
    arrows = []
    for x in [330, 622, 914, 1206]:
        arrows.append(f'<path d="M{x} 445h28" stroke="#94a3b8" stroke-width="4"/><path d="M{x+28} 445l-12-8v16z" fill="#94a3b8"/>')
    formula_rows = list(spec['formula_rows'])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" role="img" aria-labelledby="title desc">
<title id="title">{text(spec['accessible_title'])}</title>
<desc id="desc">{text(spec['accessible_desc'])}</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#06121f"/><stop offset="0.55" stop-color="#10233f"/><stop offset="1" stop-color="#1f2554"/></linearGradient>
  <radialGradient id="halo" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="#22d3ee" stop-opacity=".30"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></radialGradient>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#020617" flood-opacity=".42"/></filter>
  <pattern id="grid" width="38" height="38" patternUnits="userSpaceOnUse"><path d="M38 0H0V38" fill="none" stroke="#dbeafe" stroke-opacity=".055"/></pattern>
  <style>
    text{{font-family:{FONT}}}
    .eyebrow{{font-size:17px;letter-spacing:3.5px;font-weight:800;fill:#67e8f9}}
    .title{{font-size:50px;font-weight:850;fill:#f8fafc}}
    .subtitle{{font-size:21px;fill:#cbd5e1}}
    .vision{{font-size:18px;font-weight:700;fill:#dbeafe}}
    .card-title{{font-size:23px;font-weight:800;fill:#f8fafc}}
    .card-sub{{font-size:15px;fill:#9fb1c8}}
    .body{{font-size:15px;fill:#d5deea}}
    .micro{{font-size:12px;fill:#8ea2ba}}
    .step{{font-size:15px;font-weight:900;fill:#07111f}}
    .formula{{font-family:{MATH_FONT};font-size:22px;fill:#e0f2fe}}
    .formula-small{{font-family:{MATH_FONT};font-size:17px;fill:#f0f9ff}}
    .disclaimer{{font-size:12px;font-weight:850;letter-spacing:1.1px;fill:#111827}}
  </style>
</defs>
<rect width="1600" height="900" fill="url(#bg)"/>
<rect width="1600" height="900" fill="url(#grid)"/>
<ellipse cx="800" cy="188" rx="610" ry="190" fill="url(#halo)"/>
<g transform="translate(78 54)"><text class="eyebrow">{text(spec['eyebrow'])}</text><text class="title" y="63">{text(spec['title'])}</text><text class="subtitle" y="105">{text(spec['subtitle'])}</text></g>
<g transform="translate(1030 68)" filter="url(#shadow)"><rect width="490" height="104" rx="24" fill="#0a1829" stroke="#334155"/><text x="24" y="36" class="vision">{text(spec['vision_label'])}</text><text x="24" y="70" class="formula-small">{text(spec['vision'])}</text><text x="24" y="92" class="micro">{text(spec['vision_note'])}</text></g>
{''.join(card_markup)}
{''.join(arrows)}
<g transform="translate(78 686)" filter="url(#shadow)"><rect width="1444" height="128" rx="25" fill="#091827" stroke="#334155"/><text x="24" y="34" class="vision">{text(spec['formula_label'])}</text><text x="24" y="68" class="formula">{text(formula_rows[0])}</text><text x="24" y="100" class="formula">{text(formula_rows[1])}</text></g>
<g transform="translate(78 842)"><rect width="640" height="28" rx="14" fill="#f8fafc" opacity=".95"/><text x="320" y="19" text-anchor="middle" class="disclaimer">{text(spec['disclaimer'])}</text><text x="1440" y="20" text-anchor="end" class="micro">{text(spec['footer'])}</text></g>
</svg>'''


def localized_block(language: str, image_path: str, spec: dict[str, object]) -> str:
    marker = f'LOCALIZED_VISION_{language.upper()}'
    return f'''<!-- {marker}:START -->
## {spec['readme_heading']}

<p align="center">
  <img src="{image_path}" width="100%" alt="{spec['readme_alt']}">
</p>

> {spec['readme_note']}

<!-- {marker}:END -->'''


def replace_or_insert(path: Path, language: str, image_path: str, spec: dict[str, object], anchor: str) -> None:
    content = path.read_text(encoding='utf-8')
    marker = f'LOCALIZED_VISION_{language.upper()}'
    pattern = re.compile(rf'<!-- {re.escape(marker)}:START -->.*?<!-- {re.escape(marker)}:END -->', flags=re.DOTALL)
    block = localized_block(language, image_path, spec)
    if pattern.search(content):
        content = pattern.sub(block, content, count=1)
    elif anchor and anchor in content:
        content = content.replace(anchor, anchor + '\n\n' + block, 1)
    elif '</div>' in content[:5000]:
        content = content.replace('</div>', '</div>\n\n' + block, 1)
    else:
        first_break = content.find('\n\n')
        if first_break < 0:
            raise RuntimeError(f'{path}: no safe insertion point')
        content = content[:first_break] + '\n\n' + block + content[first_break:]
    path.write_text(content, encoding='utf-8', newline='\n')


def main() -> None:
    for language in ('zh', 'en'):
        svg_path = ROOT / CONFIG['paths'][language]
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        svg_path.write_text(render_svg(CONFIG[language]), encoding='utf-8', newline='\n')
        parsed = ET.parse(svg_path).getroot()
        if not parsed.tag.endswith('svg') or not parsed.attrib.get('viewBox'):
            raise RuntimeError(f'{svg_path}: invalid SVG root/viewBox')
        raw = svg_path.read_text(encoding='utf-8')
        if '\ufffd' in raw or '<script' in raw.lower() or 'javascript:' in raw.lower():
            raise RuntimeError(f'{svg_path}: unsafe or corrupted content')
    replace_or_insert(ROOT / CONFIG['readmes']['zh'], 'zh', CONFIG['paths']['zh'], CONFIG['zh'], CONFIG['anchors']['zh'])
    replace_or_insert(ROOT / CONFIG['readmes']['en'], 'en', CONFIG['paths']['en'], CONFIG['en'], CONFIG['anchors']['en'])
    for language in ('zh', 'en'):
        target = ROOT / CONFIG['readmes'][language]
        if CONFIG['paths'][language] not in target.read_text(encoding='utf-8'):
            raise RuntimeError(f'{target}: localized image reference missing')
    print(f"localized README vision generated for {CONFIG['repo']}")


if __name__ == '__main__':
    main()
