# TSAO 工艺智能操作系统

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-2563eb)](pyproject.toml)
[![License](https://img.shields.io/badge/License-Apache--2.0-15803d)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha.8-d97706)](reports/QUALIFICATION_BOUNDARY.md)

**面向化工工艺包构建与审计的可追溯、默认失败关闭操作系统；EPDM 是旗舰专业路线，POE 是证据谱系最完整的专业路线。**

[English](README.md) · [总体架构](ARCHITECTURE.md) · [能力矩阵](docs/CAPABILITY_MATRIX.md) · [科研诚信](docs/RESEARCH_INTEGRITY.md)

![TSAO 工艺智能操作系统总览](docs/assets/readme/tsao-process-intelligence-os.svg)

## TSAO 是什么

TSAO 将工艺研发任务书转化为受控项目工作区、机器可读工艺包和可审计证据链。它首先暴露证据缺口，再允许结论进入设备、控制、安全、客户或投资决策，避免把未经验证的假设包装成“完整工艺包”。

当前仓库提供三个可执行入口：

| 路线 | 已实现的可执行范围 | 当前边界 |
|---|---|---|
| `tsao package` | 通用设计基础、物流、设备、物料/能量衡算、控制、HSE、证据、验收与审批审计 | 可执行 Alpha 框架；具体项目工程数据仍需补充和批准 |
| `tsao epdm` | 活性位、E/P/二烯动力学、三级模型、结构/凝胶风险、半连续闭合、传热/混合、相稳定、循环毒物、脱挥与工艺包审计 | 透明参考计算；不包含工业参数标定与装置认证 |
| `tsao poe` | POE P0/P1 参考内核、动力学/性质/反应器/动态/放大及 139 项资产证据谱系 | 证据丰富的专业 Alpha；历史资产仍按受控证据处理 |

![通用工艺包生命周期](docs/assets/readme/universal-process-package.svg)

## 通用工艺包平台

通用路线抽象工艺包中反复出现的结构，而不是把某一个技术路线写死。14 个通用工艺模块与 6 条工作流覆盖：

- 化学与反应基础、测量与数据质量、热力学方法选择；
- 反应器、传递、分离、循环、公用工程和物料/能量闭合；
- 设备记录、控制、可操作性、异常工况与 HSE；
- 放大与中试逻辑、TEA/LCA/供应链接口及工艺包验收；
- 生物过程、电化学、固体/结晶、精细间歇和石油化工扩展；
- 证据 ID、状态门、审批记录与确定性归档交付。

![分层工艺包架构](docs/assets/readme/process-package-architecture.svg)

### 工艺包对象模型

TSAO 将工艺包作为相互约束的整体审计，而不是若干互不关联的文档：

```text
设计基础
  ├─ 物流与组分
  ├─ 设备与操作窗口
  ├─ 物料 / 能量衡算
  ├─ 热力学与模型依据
  ├─ 控制 / 联锁 / 异常工况
  ├─ HSE 与验收要求
  └─ 证据台账与具名审批
```

未知或缺少证据的结论必须输出 `HOLD` 或 `FAIL`，不得被静默提升为 `PASS`。

## EPDM 旗舰专业路线

EPDM 在通用工艺包之上增加更深的“机理—结构—反应器—后处理—客户”链条。

![EPDM 多尺度机理链](docs/assets/readme/epdm-multiscale-chain.svg)

强制主线为：

```text
应用 / CQA
→ 催化剂工业基准与活性位证据
→ E/P/二烯插入、链转移、失活与毒物记忆
→ 序列、MWD/CCD、保留不饱和度、支化与凝胶风险
→ 相稳定、黏度、混合、停留时间与移热
→ 淬灭、脱灰、脱挥、溶剂/单体回收与排放
→ 生胶、固定配方、硫化、部件耐久与客户线证据
→ 工艺包验收
```

### 三级动力学与过程模型

![EPDM 三级模型](docs/assets/readme/epdm-three-level-models.svg)

| 层级 | 已实现的参考计算 | 合理用途 |
|---|---|---|
| 一级——简化筛选 | 活性位归一化、三元插入/链转移/失活、插入分数、拟一级转化率 | 快速排序与输入合理性检查 |
| 二级——工程模型 | Arrhenius 温度修正、停留时间转化、守恒型半连续物料—能量步进、移热裕量、搅拌雷诺数、循环毒物闭合、脱挥 Damköhler 数 | 在明确假设下进行流程研究与实验规划 |
| 三级——复杂参考 | 多活性位族、链矩与分散系数参考、支化/凝胶风险、Flory–Huggins 旋节线裕量、传热熵产 | 判断是否值得进入 PBM/CFD/EOS 等高保真工作 |

所有层级均明确输出 `CALCULATED_REFERENCE_ONLY`，不冒充已拟合动力学、商业热力学包、合格 CFD、设备设计、HAZOP/LOPA/SIL、客户认证或工业性能保证。

### EPDM 工艺包流程图

![EPDM 工艺包参考流程图](docs/assets/readme/epdm-process-flowsheet.svg)

出现以下任一情况时，EPDM 审计默认失败关闭：

- 缺少工业催化剂基准，且没有批准的基准退出记录；
- 活性位浓度或二烯拓扑没有证据锚点；
- 移热、高黏混合或聚合物溶液相稳定性尚未验证；
- 循环杂质/毒物累积没有有限稳态闭合；
- 脱挥计算没有非平衡依据；
- 从生胶到客户线的产品桥接不完整；
- EPDM 引用的证据 ID 不存在于工艺包证据台账。

## 安装与运行

```bash
git clone https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL.git
cd TSAO-PROCESSING-SKILL
python -m pip install -e .[dev]
```

### 仓库与源文件身份检查

```bash
python -m tsao.cli doctor --root . --profile core
```

### 创建并审计通用工艺项目

```bash
python -m tsao.cli init \
  --brief examples/generic-process/brief.yaml \
  --out work/demo
python -m tsao.cli audit --root work/demo
python -m tsao.cli package template --family "连续化工过程"
```

### 运行 EPDM 参考模型

```bash
python -m tsao.cli epdm status
python -m tsao.cli epdm reference-demo
python -m tsao.cli epdm model-suite --temperature-k 323.15 --residence-s 300
python -m tsao.cli epdm audit
```

`model-suite` 输出三级动力学、守恒型半连续步进、摩尔闭合残差、相稳定裕量、脱挥 Damköhler 数以及不可逆传热熵产。

### 运行 POE 参考能力

```bash
python -m tsao.cli poe status --root .
python -m tsao.cli poe audit-p0 --root .
python -m tsao.cli poe audit-p1 --root .
python -m tsao.cli poe reference-demo
```

## 证据与质量门

![证据与质量门](docs/assets/readme/evidence-gate-system.svg)

所有面向决策的结果应保留：

1. 来源或数据集 ID；
2. 测试/模型条件与单位；
3. 方程、方法和适用边界；
4. 假设、不确定度与冲突记录；
5. 当前 Gate 状态，以及存在审批时的具名审批人。

软件测试只能证明代码按声明运行，不能证明某一真实项目的化学、设备、安全、客户性能或装置经济性正确。

## 自动验证

![自动验证流水线](docs/assets/readme/verification-pipeline.svg)

运行统一的本地质量链：

```bash
python scripts/run_ci.py
python skills/epdm/scripts/audit_epdm.py
python skills/poe/scripts/audit_p0.py --root .
python skills/poe/scripts/audit_p1.py --root .
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/verify_wheel_contents.py --wheel-dir wheelhouse
python scripts/verify_wheel_runtime.py --wheel-dir wheelhouse
```

GitHub Actions 覆盖 Ubuntu/Python 3.11–3.12、Windows/Python 3.12 和 macOS/Python 3.12，检查编译、单元/集成测试、分支覆盖率、能力合同、证据与源文件身份、Ruff、EPDM/POE 审计、Wheel 内容、安装后运行、CLI 冒烟测试和 README 图形确定性。

源文件清单属于发布身份：任何源文件变化若未同步重建 `reports/SOURCE_CORE_MANIFEST.tsv`，仓库 Doctor 将按设计失败。

## 仓库结构

```text
tsao/                       通用可执行内核与 CLI
skills/process-general/     14 个通用工艺模块与工作流
skills/epdm/                EPDM 旗舰计算、合同与审计
skills/poe/                 POE 专业能力与受控证据谱系
skills/polymer-general/     可复用聚合物规划与衡算工具
schemas/                    跨项目机器可读合同
examples/                   可复现实例任务书
scripts/                    CI、溯源、打包与图形生成
docs/assets/readme/         仓库自有原创 AI 生成 SVG 科研示意图
reports/                    资格、谱系与分支收敛记录
tests/                      仓库、安全、Schema 与集成测试
```

确定性重建 README 图形：

```bash
python scripts/generate_readme_assets.py
```

## 状态语言

| 状态 | 含义 |
|---|---|
| `PASS` | 所声明的软件或证据 Gate 已满足 |
| `HOLD` | 必需证据、资格或审批不完整 |
| `FAIL` | Schema、守恒、不变量、引用或完整性规则被破坏 |
| `NOT_EVALUATED` | 尚未形成合格结论 |
| `CALCULATED_REFERENCE_ONLY` | 透明示例计算，不是已拟合或批准的工程设计结果 |

## 分支策略

`main` 是唯一权威分支。历史分支收敛记录见 `reports/BRANCH_CONSOLIDATION_2026-07-23.md`。后续开发必须保护源文件身份、测试和证据边界，不应再创建相互平行、悄然分叉的“更完整版本”。

## 许可与责任边界

代码采用 Apache-2.0 许可。使用本仓库不能替代合格工艺工程、实验研究、设备与泄放设计、HAZOP/LOPA/SIL、法律审查、环保许可、客户试验及装置运行批准。
