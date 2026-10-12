#!/usr/bin/env node
/** Deterministic bilingual documentation; figures describe contracts, not runs. */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const PROFILE = {
 "slug":"tsao-processing","title":"TSAO Process Intelligence OS",
 "code":["tsao/process_package.py","skills/epdm/kinetics.py","skills/poe/kinetics.py"],
 "readmes":[{"path":"README.md","lang":"en"},{"path":"README.zh-CN.md","lang":"zh"}],
 "zh":{"tagline":"从机理、守恒与自适应积分到可发布工艺包证据","stages":[["工艺包对象","Schema、单位与证据谱系"],["动力学网络","基元反应、链矩与状态量"],["数值积分","DOPRI5、事件与守恒"],["辨识与 UQ","Fisher、灵敏度与适用域"],["受控交付","发布规则与责任边界"]],"boundary":"当前交付是软件参考数值与工艺研发框架；科学、工程、HSE、客户与工业性能批准均保持 NOT_EVALUATED。","strategy":["先核对安装环境、输入结构、单位、有效范围与执行权限。","按上面的源码锚点区分原生实现、解释性合同和外部执行要求。","先运行快速回归和完整质量门，再用固定提交执行长期回归。","逐项保存原始日志、机器报告和限制；任何缺失证据不得写成 PASS。"]},
 "en":{"tagline":"From mechanisms, conservation and adaptive integration to publishable process-package evidence","stages":[["Process package","Schema, units and evidence lineage"],["Kinetic network","Elementary steps, chain moments, states"],["Numerical integration","DOPRI5, events and conservation"],["Identification and UQ","Fisher, sensitivity, applicability"],["Controlled delivery","Distribution rules and authority"]],"boundary":"The deliverable is a software-reference numerical and process-development framework; scientific, engineering, HSE, customer and industrial-performance approvals remain NOT_EVALUATED.","strategy":["Check the installation environment, input structure, units, applicability and execution permissions.","Use the source mappings above to distinguish native implementation, explanatory contracts and external execution requirements.","Run focused regression and full quality gates before long-duration testing of pinned commits.","Preserve original logs, machine-readable reports and limitations; missing evidence must never be reported as PASS."]},
 "math":[
  {"latex":"r=\\sum_i F_{i,\\mathrm{in}}-\\sum_j F_{j,\\mathrm{out}}+\\sum_k G_k","plain":["r = Σ F_in − Σ F_out + Σ G"],"zh":{"name":"有限物料衡算残差","note":"这是通用 `balance_residual` 的符号约定。所有项必须采用相同物理量、时间基准与单位；正 G 表示生成，负 G 表示消耗。残差接近零只是给定账目的闭合检查，不能代替模型机理或工业数据验证。"},"en":{"name":"Finite balance residual","note":"This is the sign convention of balance_residual. All terms need the same physical quantity, time basis and units; positive G means generation and negative G consumption. A near-zero residual checks the supplied balance, not the validity of a mechanism or industrial dataset."},"code":["tsao/science.py"]},
  {"latex":"e=\\max_i\\frac{|y_i^{(5)}-y_i^{(4)}|}{a+r\\max(|y_{n,i}|,|y_i^{(5)}|)}\\le1","plain":["s_i = a + r · max(|y_n,i|, |y⁽⁵⁾_i|)","e = max_i |y⁽⁵⁾_i − y⁽⁴⁾_i| / s_i"],"zh":{"name":"逐分量自适应误差","note":"Dormand–Prince 5(4) 实际实现先逐分量缩放，再取最大值；不能写成两个向量范数之比。接受步还要求状态非负约束和守恒合同成立；达到步数或最小步长边界可能返回 HOLD。不同状态尺度需要在建模与容差设置中明确。"},"en":{"name":"Componentwise error","note":"The Dormand–Prince 5(4) implementation scales each component before taking a maximum; it is not a ratio of two vector norms. Acceptance also respects nonnegative-state and conservation contracts. Step-count or minimum-step limits may return HOLD. State scales must be explicit in model and tolerance design."},"code":["skills/epdm/numerical_integration.py"]},
  {"latex":"\\operatorname{rank}_{\\mathrm{num}}\\!\\left(J/\\max_{ij}|J_{ij}|\\right)=p","plain":["rank_num(J / max |J_ij|) = p"],"zh":{"name":"局部可辨识性检查","note":"非零、有限雅可比先按最大绝对元素缩放，随后检查数值秩是否等于参数列数 p；零矩阵单独处理。满列秩是给定观测与局部线性化条件下的诊断，不证明全局参数唯一性、良好条件数或工程批准。"},"en":{"name":"Local identifiability","note":"A nonzero finite Jacobian is scaled by its largest absolute element before testing numerical rank against parameter-column count p; the zero matrix is handled separately. Full column rank is a local diagnostic under the supplied observables, not proof of global parameter uniqueness, good conditioning or engineering approval."},"code":["tsao/science.py"]}
 ],
 "commands":["python scripts/run_ci.py"],"accent":"#6ee7b7"
};
const START = '<!-- CURRENT_MAIN_ACCEPTANCE_V2:START -->';
const END = '<!-- CURRENT_MAIN_ACCEPTANCE_V2:END -->';
const esc = (value) => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&apos;');
const normalized = (value) => value.normalize('NFC').replaceAll('\r\n', '\n');

// Conservative em-width estimates determine wrapping; browser QA checks glyph bounds.
function widthEm(text) {
  return [...text].reduce((sum, char) => sum + (/\p{Script=Han}/u.test(char) ? 1 : /[MW@%]/u.test(char) ? 0.95 : /[il.,:;!| ]/u.test(char) ? 0.34 : 0.65), 0);
}
function lines(text, width, size) {
  const output = []; let line = '';
  for (const word of String(text).match(/\p{Script=Han}|[^\p{Script=Han}\s]+|\s+/gu) ?? []) {
    if (line && widthEm(line + word) * size > width) { output.push(line.trim()); line = ''; }
    if (widthEm(word) * size > width) {
      for (const char of word) {
        if (line && widthEm(line + char) * size > width) { output.push(line.trim()); line = ''; }
        line += char;
      }
    } else line += word;
  }
  if (line.trim()) output.push(line.trim());
  return output;
}
function textBlock(value, x, baseline, width, size, leading, maxLines, color = '#dbeafe', weight = 400) {
  const wrapped = lines(value, width, size);
  if (wrapped.length > maxLines) throw Error(`Text exceeds its layout box: ${value}`);
  return `<text x="${x}" y="${baseline}" font-size="${size}" font-weight="${weight}" fill="${color}" data-box="${x},${baseline - size * 1.3},${width},${leading * maxLines + size * 0.5}">${wrapped.map((line, index) => `<tspan x="${x}" dy="${index ? leading : 0}">${esc(line)}</tspan>`).join('')}</text>`;
}
function visual(lang) {
  const t = PROFILE[lang], zh = lang === 'zh', accent = PROFILE.accent;
  const stages = t.stages.map(([heading, detail], index) => {
    const x = 46 + 307 * index;
    return `<g><rect x="${x}" y="246" width="278" height="220" rx="20" fill="#0f2038" stroke="${accent}" stroke-opacity=".5"/><circle cx="${x + 31}" cy="279" r="15" fill="${accent}" fill-opacity=".16"/><text x="${x + 31}" y="284" text-anchor="middle" font-size="13" fill="${accent}">0${index + 1}</text>${textBlock(heading, x + 20, 326, 237, 23, 28, 2, '#f8fafc', 700)}${textBlock(detail, x + 20, 399, 237, 17, 25, 2)}</g>`;
  }).join('');
  const arrows = [0, 1, 2, 3].map((index) => `<path d="M${327 + 307 * index} 357h21" fill="none" stroke="${accent}" stroke-width="2" marker-end="url(#arrow)"/>`).join('');
  const equations = PROFILE.math.map((formula, index) => {
    const x = 46 + 506 * index;
    return `<g><rect x="${x}" y="510" width="476" height="161" rx="20" fill="#101827" stroke="#64748b" stroke-opacity=".65"/>${textBlock(`${String(index + 1).padStart(2, '0')}  ${formula[lang].name}`, x + 22, 544, 432, 17, 22, 1, accent, 650)}${formula.plain.map((line, row) => textBlock(line, x + 22, 588 + row * 29, 432, 19, 26, 1, '#f8fafc')).join('')}</g>`;
  }).join('');
  const boundary = textBlock(t.boundary, 73, 767, 1440, 18, 27, 2);
  return normalized(`<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" role="img" aria-labelledby="title desc" lang="${zh ? 'zh-CN' : 'en'}">
<title id="title">${esc(PROFILE.title)} — ${zh ? '代码与数学合同' : 'Code and mathematical contracts'}</title>
<desc id="desc">${esc(t.tagline)} ${esc(t.boundary)}</desc>
<defs><linearGradient id="background" x2="1" y2="1"><stop stop-color="#070e1d"/><stop offset="1" stop-color="#172338"/></linearGradient><pattern id="grid" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M44 0H0V44" fill="none" stroke="#cbd5e1" stroke-opacity=".055"/></pattern><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 1L9 5L0 9" fill="none" stroke="${accent}" stroke-width="1.4"/></marker><style>text{font-family:"Noto Sans CJK SC","Microsoft YaHei","PingFang SC","Noto Sans",Arial,sans-serif}</style></defs>
<rect width="1600" height="900" fill="url(#background)"/><rect width="1600" height="900" fill="url(#grid)"/><circle cx="1444" cy="70" r="178" fill="${accent}" opacity=".07"/>
<path d="M1350 26L1480 75L1410 162L1539 203M1480 75L1570 20M1410 162L1310 175" fill="none" stroke="${accent}" stroke-opacity=".22" stroke-width="2"/>
${textBlock(PROFILE.title, 48, 82, 1400, 49, 54, 1, '#f8fafc', 750)}
${textBlock(t.tagline, 49, 130, 1465, 22, 30, 2, accent)}
${textBlock(zh ? '概念架构图 · 非测量数据 · 不代表外部求解已经执行' : 'CONCEPTUAL ARCHITECTURE · NOT MEASURED DATA · NOT PROOF OF EXTERNAL EXECUTION', 49, 214, 1470, 15, 23, 1, '#94a3b8')}
${arrows}${stages}${equations}
<rect x="46" y="712" width="1488" height="111" rx="18" fill="#080f1b" stroke="#334155"/>
${textBlock(zh ? '资格与解释边界' : 'QUALIFICATION AND INTERPRETATION', 73, 741, 1440, 13, 20, 1, accent, 650)}${boundary}
${textBlock(zh ? '固定源码 · 有限数值 · 可复现证据 · 人工审阅' : 'PINNED SOURCE · FINITE NUMERICS · REPRODUCIBLE EVIDENCE · HUMAN REVIEW', 49, 871, 1470, 14, 20, 1, '#94a3b8')}
</svg>
`);
}
function mathSection(lang) {
  return PROFILE.math.map((formula) => {
    const t = formula[lang];
    return `#### ${t.name}\n\n$$\n${formula.latex}\n$$\n\n${t.note}\n\n${lang === 'zh' ? '源码对应' : 'Source mapping'}: ${formula.code.map((path) => `[\`${path}\`](${path})`).join(' · ')}`;
  }).join('\n\n');
}
function section(lang, markers = true) {
  const zh = lang === 'zh', t = PROFILE[lang];
  return [markers ? START : '', `## ${zh ? '当前实现：代码、数学与使用策略' : 'Current implementation: code, mathematics and usage'}`, '',
    `![${zh ? '中文代码与数学合同概念图' : 'English code and mathematical-contract concept'}](docs/current-main/${PROFILE.slug}-current-main-${lang}.svg)`, '',
    `> ${t.boundary}`, '', mathSection(lang), '', `### ${zh ? '使用与验收顺序' : 'Usage and acceptance sequence'}`, '',
    ...t.strategy.map((item, index) => `${index + 1}. ${item}`), '', '```bash', ...PROFILE.commands, '```', '',
    zh ? '每次修复均须绑定新提交重新测试。基线回归、两段各三小时的重复回归、浏览器图形检查和外部工程认证是不同证据，不可互相替代。没有原始回执时，不宣称已完成六小时验收。' : 'Retest every changed commit. Baseline regression, two three-hour regression segments, browser visual checks and external engineering qualification are distinct evidence classes. Without original receipts, no six-hour completion is claimed.', '',
    `${zh ? '源码锚点' : 'Implementation anchors'}: ${PROFILE.code.map((path) => `[\`${path}\`](${path})`).join(' · ')}`, '', markers ? END : '',
  ].join('\n').trim();
}
function inject(original, generated) {
  const start = original.indexOf(START), end = original.indexOf(END);
  if ((start === -1) !== (end === -1) || end < start) throw Error('Unbalanced generated-section markers');
  const text = start === -1 ? `${original.trimEnd()}\n\n${generated}\n` : original.slice(0, start) + generated + original.slice(end + END.length);
  return normalized(text.trimEnd() + '\n');
}
const output = new Map(['zh', 'en'].map((lang) => [`docs/current-main/${PROFILE.slug}-current-main-${lang}.svg`, visual(lang)]));
for (const spec of PROFILE.readmes) {
  const content = spec.lang === 'bi' ? `${START}\n${section('zh', false)}\n\n${section('en', false)}\n${END}` : section(spec.lang);
  output.set(spec.path, inject(readFileSync(join(ROOT, spec.path), 'utf8'), content));
}
output.set('docs/CURRENT_MAIN_ACCEPTANCE.md', `# ${PROFILE.title} — code-backed documentation\n\n${PROFILE.code.map((path) => `- [\`${path}\`](../${path})`).join('\n')}\n\n${PROFILE.zh.boundary}\n\n${PROFILE.en.boundary}\n\nThe equations and diagrams document the declared implementation and its interpretation limits. They are not an execution attestation.\n`);
for (const path of new Set([...PROFILE.code, ...PROFILE.math.flatMap((formula) => formula.code)])) if (!existsSync(join(ROOT, path))) throw Error(`Missing source mapping: ${path}`);
const bad = [String.fromCodePoint(0xfffd), String.fromCodePoint(0x951f, 0x65a4, 0x62f7)];
for (const [path, content] of output) {
  if (bad.some((token) => content.includes(token))) throw Error(`Invalid text: ${path}`);
  if (path.endsWith('.svg') && /<script\b|<foreignObject\b|\son[a-z]+\s*=|javascript:|(?:href|xlink:href)\s*=\s*["'](?:https?:|\/\/|data:)/iu.test(content)) throw Error(`Active or external SVG content: ${path}`);
}
if (process.argv.includes('--write')) for (const [path, content] of output) { mkdirSync(dirname(join(ROOT, path)), { recursive: true }); writeFileSync(join(ROOT, path), content, 'utf8'); }
const stale = [...output].filter(([path, content]) => !existsSync(join(ROOT, path)) || readFileSync(join(ROOT, path), 'utf8') !== content).map(([path]) => path);
if (stale.length) throw Error(`Stale documentation: ${stale.join(', ')}`);
console.log(JSON.stringify({ schemaVersion: 'readme-mathematics-v6', project: PROFILE.title, files: [...output.keys()], status: 'PASS', scope: 'source mapping, deterministic generation and text integrity; not external scientific acceptance' }, null, 2));
