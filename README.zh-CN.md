# TSAO 工艺智能操作系统

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-2563eb)](pyproject.toml)
[![License](https://img.shields.io/badge/License-Apache--2.0-15803d)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha.8-d97706)](reports/QUALIFICATION_BOUNDARY.md)

**面向全部化工工艺包的可追溯、默认失败关闭 Skill 平台；EPDM 是旗舰专业路线，POE 是证据谱系最完整的专业路线。**

[English](README.md) · [总体架构](ARCHITECTURE.md) · [能力矩阵](docs/CAPABILITY_MATRIX.md) · [科研诚信](docs/RESEARCH_INTEGRITY.md)

![TSAO 工艺智能操作系统总览](docs/assets/readme/tsao-process-intelligence-os.svg)

## 一个平台，三个可执行入口

| 路线 | 当前可执行能力 | 真实边界 |
|---|---|---|
| `tsao package` | 设计基础、物流、设备、物料/能量闭合、控制、HSE、证据、验收和审批审计 | 具体项目数据和工程批准仍需外部完成 |
| `tsao epdm` | 活性位、E/P/二烯动力学、三级模型、结构/凝胶风险、半连续闭合、传热/混合、相稳定、循环毒物与脱挥 | 透明参考计算，不等于工业参数认证 |
| `tsao poe` | P0/P1 科学参考内核及 139 项历史资产受控谱系 | 证据丰富的专业 Alpha |

![通用工艺包生命周期](docs/assets/readme/universal-process-package.svg)

## 通用工艺包平台

通用路线将工艺包视为相互约束的工程系统，而不是一叠互不关联的文件。14 个模块和 6 条工作流覆盖化学、测量、热力学、反应器、传递、分离、循环、公用工程、设备、控制、异常工况、HSE、放大、TEA/LCA 和验收。

![分层工艺包架构](docs/assets/readme/process-package-architecture.svg)

### 连接式数据模型

![通用工艺包数据模型](docs/assets/readme/process-package-data-model.svg)

```text
设计基础
  ├─ 物流与组分
  ├─ 设备与操作窗口
  ├─ 物料 / 组分 / 能量衡算
  ├─ 热力学与模型依据
  ├─ 控制 / 报警 / 联锁 / 异常工况
  ├─ HSE 与验收要求
  └─ 证据台账与具名审批
```

未知或缺少证据的结论必须输出 `HOLD` 或 `FAIL`，不得被静默提升为 `PASS`。

## EPDM 旗舰专业路线

EPDM 在通用平台之上增加“机理—结构—反应器—后处理—客户”的深层链条。

![EPDM 多尺度机理链](docs/assets/readme/epdm-multiscale-chain.svg)

### 催化剂与动力学网络

![EPDM 催化剂—链结构网络](docs/assets/readme/epdm-catalyst-kinetics-network.svg)

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

| 层级 | 已实现的参考计算 | 用途 |
|---|---|---|
| 一级——筛选 | 活性位归一化、三元增长/转移/失活、插入分数和快速转化率 | 排序与输入检查 |
| 二级——工程 | Arrhenius 修正、停留时间、守恒型半连续物料—能量步进、移热/混合、循环毒物和脱挥 Damköhler 数 | 流程研究与实验规划 |
| 三级——详细参考 | 多活性位族、链矩/分散系数、支化/凝胶、Flory–Huggins 稳定性和传热熵产 | 判断是否进入 PBM/CFD/EOS 高保真工作 |

![EPDM 反应器模式决策图](docs/assets/readme/epdm-reactor-mode-map.svg)

所有层级均输出 `CALCULATED_REFERENCE_ONLY`，不冒充已拟合动力学、商业热力学包、合格 CFD、设备设计、HAZOP/LOPA/SIL、客户认证或工业性能保证。

### 聚合、后处理与循环

![EPDM 工艺包参考流程图](docs/assets/readme/epdm-process-flowsheet.svg)

![EPDM 回收循环与杂质风险闭合](docs/assets/readme/recovery-recycle-risk-loop.svg)

当活性位证据、二烯拓扑、移热、高黏混合、相稳定、循环毒物闭合、非平衡脱挥或“生胶—客户线”产品桥接不完整时，EPDM 审计默认失败关闭。

## 安装与运行

```bash
git clone https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL.git
cd TSAO-PROCESSING-SKILL
python -m pip install -e .[dev]
python -m tsao.cli doctor --root . --profile core
```

### 通用工艺包

```bash
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
python -m tsao.cli package template --family "连续化工过程"
```

### EPDM

```bash
python -m tsao.cli epdm status
python -m tsao.cli epdm reference-demo
python -m tsao.cli epdm model-suite --temperature-k 323.15 --residence-s 300
python -m tsao.cli epdm audit
```

### POE

```bash
python -m tsao.cli poe status --root .
python -m tsao.cli poe audit-p0 --root .
python -m tsao.cli poe audit-p1 --root .
python -m tsao.cli poe reference-demo
```

## 证据与资格门

![证据与资格门](docs/assets/readme/evidence-gate-system.svg)

面向决策的结果必须保留来源 ID、条件、单位、方法边界、假设、不确定度、冲突和当前 Gate。软件测试只能证明代码按声明运行，不能替代化学、设备、安全、客户性能或装置经济性的批准。

## 自动验证

![自动验证流水线](docs/assets/readme/verification-pipeline.svg)

```bash
python scripts/generate_readme_assets.py
python scripts/generate_extended_readme_assets.py
python scripts/run_ci.py
python skills/epdm/scripts/audit_epdm.py
python skills/poe/scripts/audit_p0.py --root .
python skills/poe/scripts/audit_p1.py --root .
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/verify_wheel_contents.py --wheel-dir wheelhouse
python scripts/verify_wheel_runtime.py --wheel-dir wheelhouse
```

CI 覆盖 Ubuntu/Python 3.11–3.12、Windows/Python 3.12 和 macOS/Python 3.12，并检查编译、测试、分支覆盖率、合同、溯源、Ruff、EPDM/POE 审计、图像确定性、Wheel 内容、安装后运行和 CLI 冒烟测试。

源文件清单属于发布身份：源文件变化若未同步更新 `reports/SOURCE_CORE_MANIFEST.tsv`，仓库 Doctor 将按设计失败。

## 仓库结构

```text
tsao/                       通用可执行内核与 CLI
skills/process-general/     通用工艺模块与工作流
skills/epdm/                EPDM 旗舰计算、合同与审计
skills/poe/                 POE 专业能力与受控证据谱系
skills/polymer-general/     聚合物规划与衡算工具
schemas/                    跨项目机器可读合同
scripts/                    CI、溯源、打包与图形生成
docs/assets/readme/         可确定性重建的仓库自有 SVG 图谱
reports/                    资格、谱系与分支收敛记录
tests/                      仓库、安全、Schema 与集成测试
```

## 状态语言

| 状态 | 含义 |
|---|---|
| `PASS` | 所声明的软件或证据 Gate 已满足 |
| `HOLD` | 必需证据、资格或审批不完整 |
| `FAIL` | Schema、衡算、不变量、引用或完整性规则被破坏 |
| `NOT_EVALUATED` | 尚未形成合格结论 |
| `CALCULATED_REFERENCE_ONLY` | 透明计算，不是已拟合或批准的工程设计结果 |

## 分支与责任边界

`main` 是唯一权威分支，历史收敛记录见 [reports/BRANCH_CONSOLIDATION_2026-07-23.md](reports/BRANCH_CONSOLIDATION_2026-07-23.md)。本仓库不能替代合格工艺工程、实验研究、设备与泄放设计、HAZOP/LOPA/SIL、法律审查、环保许可、客户试验及装置运行批准。
