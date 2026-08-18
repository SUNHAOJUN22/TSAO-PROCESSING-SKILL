from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- TSAO_SKILL_NATIVE_V15_START -->"
END = "<!-- TSAO_SKILL_NATIVE_V15_END -->"
OLD = re.compile(r"<!-- TSAO_SKILL_NATIVE_V(?:1[0-4]|[1-9])_START -->.*?<!-- TSAO_SKILL_NATIVE_V(?:1[0-4]|[1-9])_END -->\s*", re.DOTALL)


def clean(value: str) -> str:
    return textwrap.dedent(value).strip() + "\n"


def write(path: str, value: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(clean(value), encoding="utf-8", newline="\n")


def merge(path: str, block: str, title: str) -> None:
    target = ROOT / path
    current = target.read_text(encoding="utf-8") if target.exists() else f"# {title}\n\n"
    current = OLD.sub("", current).rstrip() + "\n\n"
    target.write_text(current + START + "\n" + clean(block) + END + "\n", encoding="utf-8", newline="\n")


skill = r'''
---
name: tsao-processing-skill
description: Process, polymerization, scale-up, equipment, control, and HSE reasoning with dimensioned quantities and evidence-bound acceptance. Use for process-case validation, component and reaction balances, kinetics, utilities, operating windows, and controlled release decisions. Do not publish controlled registries or turn missing engineering/HSE evidence into PASS.
---

# TSAO Processing Skill

## Routing

Use this Skill for deterministic process calculations and evidence-first process decisions. Load only the relevant domain references or scripts; do not treat every request as a full platform workflow.

## Material balance

For component \(j\) on declared basis \(b\):

\[
R_{j,b}=F^{in}_{j,b}-F^{out}_{j,b}+G_{j,b}-C_{j,b}-\frac{dN_{j,b}}{dt}.
\]

Each component must satisfy

\[
|R_{j,b}|\le \varepsilon_{abs,j}+\varepsilon_{rel,j}S_j.
\]

Total-flow closure cannot hide component substitution.

## State lattice

Use the monotone precedence

\[
FAIL > HOLD > CONDITIONAL/NOT\_EVALUATED > PASS.
\]

Software integrity, engineering acceptance, and HSE acceptance are separate tracks.

## Numerical contracts

Use `-expm1(-x)` for \(1-e^{-x}\) at small \(x\). MAPE is `UNDEFINED` when every observed denominator is zero. Scaled adaptive-step error uses a declared norm and scale.

## Distribution boundary

Controlled metadata, evidence classes, or project-controlled licenses block public wheel, sdist, source snapshot, and release generation until a signed owner classification decision is valid.
'''

dod = r'''
# Definition of done

- Mass/molar basis, time unit, composition basis, and reaction stoichiometry are explicit.
- All numeric inputs reject booleans, NaN, and infinity.
- Component balances are evaluated separately and use canonical units.
- Empty controls, utilities, equipment, or HSE evidence do not default to PASS.
- `NOT_APPLICABLE` requires reason, scope, and approval evidence.
- Status aggregation follows the single monotone lattice.
- Public packaging fails closed while controlled classification is unresolved.
- Stable numerical forms are used for small arguments and undefined metrics remain undefined.
- Software PASS cannot issue engineering or HSE approval.
'''

openai_yaml = r'''
interface:
  display_name: "TSAO Processing Skill"
  short_description: "Dimension-safe process calculation and evidence-first qualification"
  default_prompt: "Validate the process case, normalize units and bases, close each component and reaction balance, propagate the status lattice, and preserve controlled-distribution and HSE boundaries."
policy:
  allow_implicit_invocation: true
  truth_boundary: "Software validation never implies engineering/HSE approval or public-release authority."
'''

evals = {"schema": "tsao-processing.skill-routing.v15", "skill": "tsao-processing-skill", "cases": [
    {"id": "en-balance", "language": "en", "prompt": "Build a unit-aware component and reaction balance for this polymerization train.", "expected": "TRIGGER"},
    {"id": "zh-balance", "language": "zh", "prompt": "为该聚合装置建立带单位的逐组分和反应物料衡算。", "expected": "TRIGGER"},
    {"id": "en-hse", "language": "en", "prompt": "Propagate equipment, control, and HSE HOLD states into the overall process decision.", "expected": "TRIGGER"},
    {"id": "zh-hse", "language": "zh", "prompt": "将设备、控制和HSE的HOLD状态传播到总工艺决策。", "expected": "TRIGGER"},
    {"id": "en-negative", "language": "en", "prompt": "Translate this process paragraph into Chinese.", "expected": "NO_TRIGGER"},
    {"id": "zh-negative", "language": "zh", "prompt": "把这段工艺文字翻译成英文。", "expected": "NO_TRIGGER"}
]}

validator = r'''
from __future__ import annotations
import argparse, json
from pathlib import Path
REQUIRED=(".agents/skills/tsao-processing-skill/SKILL.md",".agents/skills/tsao-processing-skill/agents/openai.yaml",".agents/skills/tsao-processing-skill/references/definition-of-done.md",".agents/skills/tsao-processing-skill/evals/evals.json","assets/diagrams/vision-en.svg","assets/diagrams/vision-zh.svg")
BAD=("\x00","\ufffd","Ã","Â","â€")
def main()->int:
 p=argparse.ArgumentParser(); p.add_argument("--root",default="."); p.add_argument("--report",default="artifacts/skill-validation-v15.json"); a=p.parse_args(); r=Path(a.root).resolve(); e=[]
 for x in REQUIRED:
  if not (r/x).is_file(): e.append(f"missing {x}")
 s=r/REQUIRED[0]
 if s.is_file():
  t=s.read_text(encoding="utf-8")
  if not t.startswith("---\n") or "name: tsao-processing-skill" not in t[:800]: e.append("invalid SKILL.md")
  if "Do not publish controlled" not in t[:1200]: e.append("anti-trigger boundary missing")
 for f in r.rglob("*"):
  if f.is_file() and f.suffix.lower() in {".md",".py",".json",".yaml",".yml",".svg"}:
   v=f.read_text(encoding="utf-8")
   if any(m in v for m in BAD): e.append(f"Unicode failure in {f.relative_to(r)}")
 ep=r/REQUIRED[3]
 if ep.is_file():
  c=json.loads(ep.read_text(encoding="utf-8")).get("cases",[])
  if len(c)<6 or {x.get("expected") for x in c}!={"TRIGGER","NO_TRIGGER"}: e.append("routing evals incomplete")
 o={"schema":"tsao-processing.skill-validation.v15","status":"PASS" if not e else "FAIL","errors":e}; q=r/a.report; q.parent.mkdir(parents=True,exist_ok=True); q.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps(o,ensure_ascii=False)); return 0 if not e else 1
if __name__=="__main__": raise SystemExit(main())
'''

contracts = r'''
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from math import expm1, fsum, isfinite
from typing import Mapping, Sequence


class Severity(IntEnum):
    PASS = 0
    NOT_EVALUATED = 1
    CONDITIONAL = 1
    HOLD = 2
    FAIL = 3


@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str
    dimension: str
    scale_to_si: float

    def canonical(self) -> float:
        if isinstance(self.value, bool) or isinstance(self.scale_to_si, bool):
            raise TypeError("quantity values must not be booleans")
        if not isfinite(float(self.value)) or not isfinite(float(self.scale_to_si)):
            raise ValueError("quantity values must be finite")
        if self.scale_to_si <= 0.0 or not self.unit or not self.dimension:
            raise ValueError("positive scale, unit, and dimension are required")
        return float(self.value) * float(self.scale_to_si)


@dataclass(frozen=True)
class BalanceResult:
    status: str
    residuals: Mapping[str, float]
    blocking_paths: tuple[str, ...]


def component_balance(
    inputs: Mapping[str, Quantity], outputs: Mapping[str, Quantity], sources: Mapping[str, Quantity] | None = None,
    *, abs_tolerance_si: float, rel_tolerance: float
) -> BalanceResult:
    src = sources or {}
    quantities = [*inputs.values(), *outputs.values(), *src.values()]
    if not quantities:
        raise ValueError("balance requires at least one quantity")
    if len({q.dimension for q in quantities}) != 1:
        raise ValueError("mixed balance dimensions are invalid")
    if any(isinstance(x, bool) or not isfinite(float(x)) or x < 0.0 for x in (abs_tolerance_si, rel_tolerance)):
        raise ValueError("tolerances must be finite non-negative reals")
    residuals: dict[str, float] = {}
    blocked: list[str] = []
    for component in sorted(set(inputs) | set(outputs) | set(src)):
        vin = inputs[component].canonical() if component in inputs else 0.0
        vout = outputs[component].canonical() if component in outputs else 0.0
        vsrc = src[component].canonical() if component in src else 0.0
        residual = fsum((vin, vsrc, -vout))
        residuals[component] = residual
        scale = max(abs(vin), abs(vout), abs(vsrc), 1.0)
        if abs(residual) > abs_tolerance_si + rel_tolerance * scale:
            blocked.append(f"components.{component}")
    return BalanceResult("PASS" if not blocked else "FAIL", residuals, tuple(blocked))


def aggregate_status(statuses: Sequence[str]) -> str:
    if not statuses:
        return "HOLD"
    aliases = {"PASS": Severity.PASS, "NOT_EVALUATED": Severity.NOT_EVALUATED, "CONDITIONAL": Severity.CONDITIONAL, "HOLD": Severity.HOLD, "FAIL": Severity.FAIL}
    try:
        worst = max(aliases[value] for value in statuses)
    except KeyError as exc:
        raise ValueError(f"unknown status: {exc.args[0]}") from exc
    if worst is Severity.FAIL:
        return "FAIL"
    if worst is Severity.HOLD:
        return "HOLD"
    if worst is Severity.NOT_EVALUATED:
        return "NOT_EVALUATED"
    return "PASS"


def fraction_reacted(x: float) -> float:
    if isinstance(x, bool) or not isfinite(float(x)) or x < 0.0:
        raise ValueError("x must be a finite non-negative real")
    return -expm1(-float(x))


def mape(observed: Sequence[float], predicted: Sequence[float]) -> float | None:
    if not observed or len(observed) != len(predicted):
        raise ValueError("observed and predicted must be non-empty and aligned")
    terms: list[float] = []
    for obs, pred in zip(observed, predicted, strict=True):
        if any(isinstance(v, bool) or not isfinite(float(v)) for v in (obs, pred)):
            raise ValueError("MAPE inputs must be finite non-boolean reals")
        if obs != 0.0:
            terms.append(abs((pred - obs) / obs))
    return None if not terms else 100.0 * fsum(terms) / len(terms)


def public_distribution_status(*, controlled_records: int, signed_owner_decision_valid: bool) -> str:
    if controlled_records < 0:
        raise ValueError("controlled_records must be non-negative")
    if controlled_records and not signed_owner_decision_valid:
        return "BLOCKED_CONTROLLED_METADATA_CLASSIFICATION"
    return "PUBLIC_DISTRIBUTION_ELIGIBLE"
'''

tests = r'''
from __future__ import annotations
import math, unittest
from tsao.scientific_contracts_v15 import Quantity, aggregate_status, component_balance, fraction_reacted, mape, public_distribution_status
class Tests(unittest.TestCase):
 def q(self,v:float)->Quantity: return Quantity(v,"kg/h","mass_flow",1/3600)
 def test_component_substitution_fails(self)->None:
  r=component_balance({"A":self.q(100)},{"B":self.q(100)},abs_tolerance_si=1e-12,rel_tolerance=1e-12); self.assertEqual(r.status,"FAIL"); self.assertEqual(set(r.blocking_paths),{"components.A","components.B"})
 def test_state_lattice(self)->None:
  self.assertEqual(aggregate_status(["PASS","HOLD"]),"HOLD"); self.assertEqual(aggregate_status(["HOLD","FAIL"]),"FAIL"); self.assertEqual(aggregate_status([]),"HOLD")
 def test_expm1_stability(self)->None:
  x=1e-14; self.assertAlmostEqual(fraction_reacted(x),x,places=26); self.assertTrue(math.isfinite(fraction_reacted(x)))
 def test_mape_all_zero_is_undefined(self)->None: self.assertIsNone(mape([0.0,0.0],[0.0,1.0]))
 def test_controlled_distribution_is_blocked(self)->None: self.assertEqual(public_distribution_status(controlled_records=139,signed_owner_decision_valid=False),"BLOCKED_CONTROLLED_METADATA_CLASSIFICATION")
if __name__=="__main__": unittest.main()
'''

workflow = r'''
name: Skill-native portability
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  validate:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-24.04, windows-2025]
    runs-on: ${{ matrix.os }}
    timeout-minutes: 12
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
        with:
          persist-credentials: false
      - run: python scripts/validate_skill.py --root . --report artifacts/skill-validation-v15.json
      - run: python -m unittest tests.test_scientific_contracts_v15 -v
'''

svg_en = r'''
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"><defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="#07162c"/><stop offset=".5" stop-color="#173d5d"/><stop offset="1" stop-color="#071122"/></linearGradient><linearGradient id="c" x2="1" y2="1"><stop stop-color="#1c4d70"/><stop offset="1" stop-color="#10273f"/></linearGradient></defs><rect width="1600" height="900" fill="url(#g)"/><g opacity=".16" stroke="#69dcff"><path d="M0 180H1600M0 360H1600M0 540H1600M0 720H1600"/><path d="M200 0V900M500 0V900M800 0V900M1100 0V900M1400 0V900"/></g><text x="80" y="100" fill="#fff" font-family="Arial" font-size="50" font-weight="700">TSAO Processing Skill · Law-to-Process Evidence Chain</text><text x="85" y="148" fill="#b4eaff" font-family="Arial" font-size="24">Component balance → kinetics → equipment/control → HSE → qualified handoff</text><g transform="translate(75 225)"><rect width="450" height="405" rx="28" fill="url(#c)" stroke="#54d9ff" stroke-width="2"/><text x="35" y="65" fill="#fff" font-family="Arial" font-size="29" font-weight="700">Dimensioned balance</text><text x="35" y="130" fill="#c8efff" font-family="Arial" font-size="23">Rj = Fin,j − Fout,j + Gj − Cj</text><text x="35" y="190" fill="#d9f2ff" font-family="Arial" font-size="21">mass/molar basis · time unit</text><text x="35" y="230" fill="#d9f2ff" font-family="Arial" font-size="21">composition · stoichiometry</text><text x="35" y="315" fill="#75f0bd" font-family="Arial" font-size="21">Every component closes.</text><text x="35" y="352" fill="#75f0bd" font-family="Arial" font-size="21">Cross-component cancellation fails.</text></g><g transform="translate(575 225)"><rect width="450" height="405" rx="28" fill="url(#c)" stroke="#b79cff" stroke-width="2"/><text x="35" y="65" fill="#fff" font-family="Arial" font-size="29" font-weight="700">Monotone decision lattice</text><text x="35" y="130" fill="#e2d9ff" font-family="Arial" font-size="22">FAIL &gt; HOLD &gt; NOT_EVALUATED &gt; PASS</text><text x="35" y="195" fill="#d9f2ff" font-family="Arial" font-size="21">software · engineering · HSE</text><text x="35" y="235" fill="#d9f2ff" font-family="Arial" font-size="21">remain independent tracks</text><text x="35" y="315" fill="#75f0bd" font-family="Arial" font-size="21">Empty evidence never becomes PASS.</text></g><g transform="translate(1075 225)"><rect width="450" height="405" rx="28" fill="url(#c)" stroke="#ffbd65" stroke-width="2"/><text x="35" y="65" fill="#fff" font-family="Arial" font-size="29" font-weight="700">Controlled distribution</text><text x="35" y="130" fill="#ffe0ad" font-family="Arial" font-size="21">registry · evidence class · license</text><text x="35" y="195" fill="#d9f2ff" font-family="Arial" font-size="21">wheel · sdist · snapshot · release</text><text x="35" y="235" fill="#d9f2ff" font-family="Arial" font-size="21">fail closed without owner decision</text><text x="35" y="315" fill="#75f0bd" font-family="Arial" font-size="21">Containment is a correct result.</text></g><rect x="75" y="695" width="1450" height="115" rx="24" fill="#071b34" stroke="#4bcdf2"/><text x="115" y="747" fill="#fff" font-family="Arial" font-size="25" font-weight="700">Stable numerics</text><text x="365" y="747" fill="#c7edff" font-family="Arial" font-size="22">1 − exp(−x) = −expm1(−x)</text><text x="740" y="747" fill="#c7edff" font-family="Arial" font-size="22">all-zero observed MAPE = UNDEFINED</text><text x="115" y="790" fill="#ffcf75" font-family="Arial" font-size="21">Truth boundary: software PASS does not issue engineering, HSE, or public-release authority.</text></svg>
'''

svg_zh = r'''
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"><defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="#07162c"/><stop offset=".5" stop-color="#173d5d"/><stop offset="1" stop-color="#071122"/></linearGradient><linearGradient id="c" x2="1" y2="1"><stop stop-color="#1c4d70"/><stop offset="1" stop-color="#10273f"/></linearGradient></defs><rect width="1600" height="900" fill="url(#g)"/><g opacity=".16" stroke="#69dcff"><path d="M0 180H1600M0 360H1600M0 540H1600M0 720H1600"/><path d="M200 0V900M500 0V900M800 0V900M1100 0V900M1400 0V900"/></g><text x="80" y="100" fill="#fff" font-family="Microsoft YaHei,Arial" font-size="50" font-weight="700">TSAO Processing Skill · 从规律到工艺的证据链</text><text x="85" y="148" fill="#b4eaff" font-family="Microsoft YaHei,Arial" font-size="24">逐组分衡算 → 动力学 → 设备/控制 → HSE → 合格交接</text><g transform="translate(75 225)"><rect width="450" height="405" rx="28" fill="url(#c)" stroke="#54d9ff" stroke-width="2"/><text x="35" y="65" fill="#fff" font-family="Microsoft YaHei,Arial" font-size="29" font-weight="700">带量纲物料衡算</text><text x="35" y="130" fill="#c8efff" font-family="Arial" font-size="23">Rj = Fin,j − Fout,j + Gj − Cj</text><text x="35" y="190" fill="#d9f2ff" font-family="Microsoft YaHei,Arial" font-size="21">质量/摩尔基准 · 时间单位</text><text x="35" y="230" fill="#d9f2ff" font-family="Microsoft YaHei,Arial" font-size="21">组成基准 · 反应计量</text><text x="35" y="315" fill="#75f0bd" font-family="Microsoft YaHei,Arial" font-size="21">每个组分分别闭合</text><text x="35" y="352" fill="#75f0bd" font-family="Microsoft YaHei,Arial" font-size="21">禁止跨组分抵消</text></g><g transform="translate(575 225)"><rect width="450" height="405" rx="28" fill="url(#c)" stroke="#b79cff" stroke-width="2"/><text x="35" y="65" fill="#fff" font-family="Microsoft YaHei,Arial" font-size="29" font-weight="700">单调决策状态格</text><text x="35" y="130" fill="#e2d9ff" font-family="Arial" font-size="22">FAIL &gt; HOLD &gt; NOT_EVALUATED &gt; PASS</text><text x="35" y="195" fill="#d9f2ff" font-family="Microsoft YaHei,Arial" font-size="21">软件 · 工程 · HSE</text><text x="35" y="235" fill="#d9f2ff" font-family="Microsoft YaHei,Arial" font-size="21">保持独立验收轨道</text><text x="35" y="315" fill="#75f0bd" font-family="Microsoft YaHei,Arial" font-size="21">空证据绝不默认为PASS</text></g><g transform="translate(1075 225)"><rect width="450" height="405" rx="28" fill="url(#c)" stroke="#ffbd65" stroke-width="2"/><text x="35" y="65" fill="#fff" font-family="Microsoft YaHei,Arial" font-size="29" font-weight="700">受控分发门</text><text x="35" y="130" fill="#ffe0ad" font-family="Microsoft YaHei,Arial" font-size="21">登记表 · 证据类别 · 许可</text><text x="35" y="195" fill="#d9f2ff" font-family="Microsoft YaHei,Arial" font-size="21">wheel · sdist · snapshot · release</text><text x="35" y="235" fill="#d9f2ff" font-family="Microsoft YaHei,Arial" font-size="21">无权利人决定时全部阻断</text><text x="35" y="315" fill="#75f0bd" font-family="Microsoft YaHei,Arial" font-size="21">阻断是正确结果，不是红叉</text></g><rect x="75" y="695" width="1450" height="115" rx="24" fill="#071b34" stroke="#4bcdf2"/><text x="115" y="747" fill="#fff" font-family="Microsoft YaHei,Arial" font-size="25" font-weight="700">稳定数值</text><text x="365" y="747" fill="#c7edff" font-family="Arial" font-size="22">1 − exp(−x) = −expm1(−x)</text><text x="740" y="747" fill="#c7edff" font-family="Microsoft YaHei,Arial" font-size="22">观测值全零时 MAPE = 未定义</text><text x="115" y="790" fill="#ffcf75" font-family="Microsoft YaHei,Arial" font-size="21">真实性边界：软件通过不能签发工程、HSE或公开分发权限。</text></svg>
'''

readme_en = r'''
## Skill-native process qualification

![TSAO Processing evidence chain](assets/diagrams/vision-en.svg)

The canonical Skill is `.agents/skills/tsao-processing-skill/SKILL.md`. It provides progressive disclosure for process, polymerization, scale-up, equipment, control, and HSE tasks without turning the repository into an unnecessarily complex platform.

For component \(j\), \(R_j=F_{in,j}-F_{out,j}+G_j-C_j-dN_j/dt\); each component must satisfy its own tolerance. Overall status follows `FAIL > HOLD > NOT_EVALUATED > PASS`. Controlled metadata keeps public wheel, sdist, snapshot, and release paths blocked until a signed owner decision exists.

```bash
python scripts/validate_skill.py --root . --report artifacts/skill-validation-v15.json
python -m unittest tests.test_scientific_contracts_v15 -v
```
'''

readme_zh = r'''
## Skill 原生工艺资格层

![TSAO Processing 证据链](assets/diagrams/vision-zh.svg)

规范 Skill 位于 `.agents/skills/tsao-processing-skill/SKILL.md`。它以渐进披露方式服务工艺、聚合、放大、设备、控制和 HSE 任务，不把本质为 Skill 的仓库不必要地堆成复杂平台。

对组分 \(j\)，\(R_j=F_{in,j}-F_{out,j}+G_j-C_j-dN_j/dt\)，每个组分分别满足容差。总状态遵循 `FAIL > HOLD > NOT_EVALUATED > PASS`。受控元数据在取得签名权利人决定前继续阻断公开 wheel、sdist、snapshot 和 release。

```bash
python scripts/validate_skill.py --root . --report artifacts/skill-validation-v15.json
python -m unittest tests.test_scientific_contracts_v15 -v
```
'''

write(".agents/skills/tsao-processing-skill/SKILL.md",skill)
write(".agents/skills/tsao-processing-skill/references/definition-of-done.md",dod)
write(".agents/skills/tsao-processing-skill/agents/openai.yaml",openai_yaml)
write(".agents/skills/tsao-processing-skill/evals/evals.json",json.dumps(evals,ensure_ascii=False,indent=2))
write("scripts/validate_skill.py",validator)
write("tsao/scientific_contracts_v15.py",contracts)
write("tests/test_scientific_contracts_v15.py",tests)
write(".github/workflows/skill-native-ci.yml",workflow)
write("assets/diagrams/vision-en.svg",svg_en)
write("assets/diagrams/vision-zh.svg",svg_zh)
merge("README.md",readme_en,"TSAO Processing Skill")
zh="README.zh-CN.md" if (ROOT/"README.zh-CN.md").exists() else "README_CN.md"; merge(zh,readme_zh,"TSAO Processing Skill 中文说明")
print(json.dumps({"status":"APPLIED","version":"15.0.0"},ensure_ascii=False))
