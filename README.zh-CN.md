# TSAO 化学工艺智能研发操作系统

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.5-orange.svg)](CHANGELOG.md)

**把一个化学工艺问题转化为可追溯的研发程序：证据 → 实验 → 模型 → 放大 → 工艺包 → 验收 → 现场学习。**

TSAO 软件中立、默认拒绝越权。文献、专利、模拟、自动生成文件或软件测试通过，都不会自动成为装置设定值或技术批准。

[English](README.md) · [执行合同](SKILL.md) · [系统架构](ARCHITECTURE.md) · [能力矩阵](docs/CAPABILITY_MATRIX.md)

## 选择一个入口

| 子技能 | 适用范围 |
|---|---|
| `process-general` | 反应、物性、反应器、分离循环、控制、安全可靠性和放大 |
| `epdm` | EPM/EPDM 从催化剂到客户的完整生命周期 |
| `poe` | POE 溶液聚合动力学、流程、动态、放大与验收 |
| `polymer-general` | 其他聚合、改性、配方与循环利用路线 |

四个入口统一继承 G0–G18 Gate、证据状态、模型风险、不确定度和人工批准边界。

## 从这里开始

```bash
python -m pip install -e .[dev]
python -m tsao.cli doctor --root .
python -m tsao.cli route "连续催化反应器与溶剂回收"
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
```

`tsao init` 会生成 G0–G18、14 条专业工作流、**266 个 fail-closed 工作包**、M0–M9 成熟度记录和明确的外部执行状态。

AI Agent 先读取 `SKILL.md`，再执行 `prompts/TSAO_PROJECT_EXECUTION_PROMPT.md`。

## 一键验证仓库

本地运行与托管 CI 一致的核心资格门：

```bash
python scripts/run_ci.py
```

该命令会编译源码，执行母层与全部专业子技能测试，审计能力完整性，通过 `tsao doctor` 核验仓库与来源清单，并执行 Ruff。GitHub Actions 还会在 Ubuntu/Python 3.11–3.12、Windows/Python 3.12 和 macOS/Python 3.12 上重复验证，随后构建 wheel 并运行 CLI 冒烟测试。

## 仓库内容

- `SKILL.md`：不可妥协的执行合同
- `tsao/`：可执行核心、路由、项目生成、审计与 `doctor`
- `skills/`：process-general、EPDM、POE 和 polymer-general 专业子技能
- `schemas/`：证据、Gate、工作包、成熟度与批准状态的数据合同
- `reports/SOURCE_CORE_MANIFEST.tsv`：公开源码身份
- `reports/COMPLETE_DISTRIBUTION_MANIFEST.tsv`：完整合格发行包身份
- `scripts/`：本地 CI、能力与来源核验工具

`main` 是唯一权威开发线；版本身份、源码谱系和继承资产边界通过清单与文档保留，不依赖额外分支。

## 可信边界

软件资格不等于科学、工程、安全、法律、客户或工业批准。真实实验、商业模拟、设备与泄放设计、HAZOP/LOPA/SIL、FTO、中试与示范、客户验证和装置保证仍为 `NOT_EVALUATED`，必须由具名合格人员依据真实证据批准。

TSAO 原创代码与文档采用 Apache-2.0。继承资产归属与发行边界见 [NOTICE.md](NOTICE.md) 和 [源码一致性说明](docs/SOURCE_PARITY.md)。
