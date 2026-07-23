# TSAO 化学工艺智能操作系统

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.5-orange.svg)](CHANGELOG.md)

**可追溯 · 科学 · 可审计 · 可执行**

TSAO 将工艺任务、资料、实验数据、模型或装置技术包组织成受控研发程序：

`证据 → 化学 → 测量 → 物性/动力学 → 反应器 → 分离循环 → 小试 → 台架 → 中试 → 工业设计 → 控制/HSE → 资格 → 技术包 → 转移 → 现场学习`

它生成可审计工件，不虚构实验、安全、法律或工业批准。

[English](README.md) · [核心 Skill](SKILL.md) · [系统架构](ARCHITECTURE.md) · [能力矩阵](docs/CAPABILITY_MATRIX.md)

## 从这里开始

```bash
python -m pip install -e .[dev]
tsao doctor
tsao init --brief examples/generic-process/brief.yaml --out work/demo
tsao audit --root work/demo
```

`tsao doctor` 是统一体检入口，检查版本、Schema、专业子技能、来源清单、发布元数据、缓存污染和技术批准边界。

## 四条专业路线

| 路线 | 适用任务 |
|---|---|
| `process-general` | 催化、石化、精细化工、生物、电化学、结晶/固体和通用化工过程 |
| `epdm` | EPDM 催化剂、E/P/二烯聚合、回收、配混、产品和客户资格 |
| `poe` | POE 溶液聚合、物性、流程、动态、放大和验收 |
| `polymer-general` | 其他聚合机理、配方、改性和反应加工 |

无论走哪条路线，母层 G0–G18、14 条工作流和 M0–M9 成熟度始终生效。

## 一次初始化真实生成

- G0–G18 Gate 与 266 个 fail-closed 工作包；
- 证据、主张、假设和矛盾记录；
- 实验、模型、放大和外部执行合同；
- 工艺包、验收、转移和现场持续学习结构；
- 所有未被真实证据和实名审批支持的任务均保持 `NOT_EVALUATED`。

## 验证

```bash
python scripts/run_ci.py
python scripts/audit_capabilities.py
python -m tsao.cli verify-archive --archive TSAO-PROCESSING-SKILL.zip
```

完整发行包包含 EPDM v9、SJTU-POE 和通用聚合完整源树，并携带逐文件来源清单；公共分支保存家族级同构台账和准确发行身份。`reports/SOURCE_PARITY_ALPHA5.json` 如实记录公共仓库同步状态，不把部分同步写成完整同构。

## 强制边界

CI 全绿只说明软件工件通过。催化剂合成、物理实验、商业模拟、设备/泄放设计、HAZOP/LOPA/SIL、法律 FTO、客户认证、中试、示范和工业性能保证仍为 **`NOT_EVALUATED`**，必须由项目合格团队以真实证据和实名审批完成。
