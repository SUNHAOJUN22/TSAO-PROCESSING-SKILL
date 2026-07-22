# TSAO 化学工艺智能研发操作系统

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.5-orange.svg)](CHANGELOG.md)

**把一个化学工艺问题转化为可追溯的研发程序：证据 → 实验 → 模型 → 放大 → 工艺包 → 验收 → 现场学习。**

TSAO 软件中立、默认拒绝越权。文献、专利、模拟、自动生成文件或测试通过，都不会自动成为装置设定值或技术批准。

[English](README.md) · [执行合同](SKILL.md) · [系统架构](ARCHITECTURE.md) · [能力矩阵](docs/CAPABILITY_MATRIX.md)

## 四个入口

| 子技能 | 适用范围 |
|---|---|
| `process-general` | 反应、物性、反应器、分离循环、控制、安全可靠性和放大 |
| `epdm` | EPM/EPDM 从催化剂到客户线 |
| `poe` | POE 溶液聚合、流程、动态、放大与验收 |
| `polymer-general` | 其他聚合、改性、配方与循环利用路线 |

## 唯一推荐使用路径

```bash
python -m pip install -e .[dev]
python -m tsao.cli doctor --root .
python -m tsao.cli route "连续催化反应器与溶剂回收"
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
```

`tsao init` 会生成 G0–G18、14 条工作流、**266 个 fail-closed 工作包**、M0–M9 成熟度和外部执行状态。

Agent 先读取 `SKILL.md`，再执行 `prompts/TSAO_PROJECT_EXECUTION_PROMPT.md`。

## 自动验证什么

- `tsao doctor` 检查版本、Schema、源码来源、专业子技能和发布边界；
- 正常和恶意负例覆盖 Gate、证据、模型、衡算、科学内核、归档和项目生成；
- 确定性构建与洁净室复验；
- Ubuntu/Python 3.11–3.12，以及 Windows/macOS 可移植性。

## 必须保留的边界

软件资格不等于科学、工程、安全、法律、客户或工业批准。真实实验、商业模拟、泄放设计、HAZOP/LOPA/SIL、FTO、中试、示范和装置保证仍为 `NOT_EVALUATED`，必须由具名合格人员依据真实证据批准。

## 目录

- `SKILL.md`：不可妥协的执行合同
- `tsao/`：可执行核心与 `doctor`
- `skills/`：四个专业子技能
- `schemas/`：数据和批准合同
- `reports/SOURCE_CORE_MANIFEST.tsv`：公开源码身份
- `reports/COMPLETE_DISTRIBUTION_MANIFEST.tsv`：完整发行包身份
- `scripts/`：审计、CI 和发布工具
