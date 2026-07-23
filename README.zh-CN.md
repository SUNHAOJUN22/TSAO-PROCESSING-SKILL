# TSAO 化学工艺智能研发操作系统

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.6-orange.svg)](CHANGELOG.md)

**把一个化学工艺问题转化为可审计的研发程序：证据 → 实验 → 模型 → 放大 → 工艺包 → 验收 → 现场学习。**

TSAO 软件中立、默认拒绝越权。文献数值不是装置设定值，模拟收敛不是技术批准，自动生成文件也不代表真实工作已经完成。

[English](README.md) · [执行合同](SKILL.md) · [系统架构](ARCHITECTURE.md) · [能力矩阵](docs/CAPABILITY_MATRIX.md)

## 选择专业入口

| 子技能 | 适用范围 |
|---|---|
| `process-general` | 反应、物性、反应器、分离循环、控制、HSE、可靠性和放大 |
| `epdm` | EPM/EPDM 催化剂、三元聚合、回收、配混和客户资格 |
| `poe` | POE 溶液聚合、物性、流程、动态、放大和验收 |
| `polymer-general` | 其他聚合、改性、配方、反应加工和循环利用路线 |

四个入口统一继承 G0–G18 Gate、14 条专业工作流、M0–M9 成熟度、证据状态、模型风险和具名人工批准。

## 开始使用

```bash
python -m pip install -e .[dev]
python -m tsao.cli doctor --root . --profile core
python -m tsao.cli route "连续催化反应器与溶剂回收"
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
```

`tsao init` 会生成 19 × 14 = **266 个 fail-closed 工作包**、成熟度记录和明确的外部执行状态。

## 验证

```bash
python scripts/run_ci.py
python -m tsao.cli snapshot --root . --out TSAO-source.zip
python -m tsao.cli verify-archive --archive TSAO-source.zip
```

- `doctor --profile core` 校验 GitHub 源码与 `reports/SOURCE_CORE_MANIFEST.tsv`。
- `doctor --profile full` 进一步校验完整分发清单、`FILE_MANIFEST.tsv`、`checksums.sha256` 和 `SBOM.json`。
- GitHub Actions 在 Ubuntu/Python 3.11–3.12、Windows/Python 3.12 和 macOS/Python 3.12 上运行统一资格门，构建 wheel，并发布确定性源码快照。
- 当前机器可读发行记录见 [reports/RELEASE_IDENTITY.json](reports/RELEASE_IDENTITY.json)。

## 仓库地图

- `SKILL.md`：不可妥协的执行合同
- `tsao/`：路由、项目生成、审计、完整性检查和 CLI
- `skills/`：process-general、EPDM、POE 和 polymer-general
- `schemas/`：证据、Gate、工作包、成熟度和批准合同
- `reports/`：源码身份、资格记录和发行记录
- `scripts/`：CI、来源、快照和发行工具

`main` 是唯一权威开发线。公共源码快照与完整资格发行包是两个独立、明确标识的工件，详见[源码一致性说明](docs/SOURCE_PARITY.md)。

## 可信边界

软件资格不等于科学、工程、安全、法律、客户或工业批准。真实实验、商业模拟、设备与泄放设计、HAZOP/LOPA/SIL、FTO、中试与示范、客户验证和装置保证始终保持 **`NOT_EVALUATED`**，直至具名合格人员依据真实证据批准。

TSAO 原创代码和文档采用 Apache-2.0；继承资产保留各自来源与再分发边界，详见 [NOTICE.md](NOTICE.md)。
