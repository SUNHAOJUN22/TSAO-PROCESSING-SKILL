# TSAO 化学工艺智能研发操作系统

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.6-orange.svg)](CHANGELOG.md)

**证据 → 实验 → 模型 → 放大 → 工艺包 → 验收 → 现场学习。**

TSAO 把化学工艺问题转化为可追溯、默认拒绝越权的研发程序。文献数值不是装置设定值，模拟收敛不是技术批准，自动生成文件也不代表真实工作已经完成。

[English](README.md) · [执行合同](SKILL.md) · [系统架构](ARCHITECTURE.md) · [能力矩阵](docs/CAPABILITY_MATRIX.md)

## 专业入口

| 子技能 | 当前范围 |
|---|---|
| `process-general` | 反应、物性、反应器、分离循环、控制、HSE、可靠性和放大 |
| `epdm` | EPM/EPDM 催化剂、三元聚合、回收、配混和客户资格 |
| `poe` | POE 溶液聚合 **executable specialist alpha**：139 项资产谱系、12 个模块、参考动力学/物性/case 校验和内容级工艺包审计 |
| `polymer-general` | 其他聚合、改性、配方、反应加工和循环利用路线 |

四个入口统一继承 G0–G18 Gate、14 条工作流、M0–M9 成熟度、证据状态、模型风险和具名人工批准。

## 开始使用

```bash
python -m pip install -e .[dev]
python -m tsao.cli doctor --root . --profile core
python -m tsao.cli route "POE溶液聚合与溶剂回收"
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
```

## POE alpha.6

当前 POE 包已经包含：

- 139/139 项原始资产身份、18/18 项需求和 7 项真实冲突/偏差记录；
- 覆盖产品 CQA、催化剂杂质、动力学、物性、反应器、流程、循环、动态和验收的 12 个模块合同；
- 透明的参考动力学、物性方法资格化和模拟器中立稳态/动态 case 校验；
- 检查 manifest、哈希、正文、交叉引用和审批的工艺包审计器，明确拒绝 placeholder，并可映射中文历史交付物；
- 去标识化合成 fixture 与恶意输入测试，不公开原始 Aspen、MATLAB、Origin、合同或商业敏感文件。

详见 [POE 状态](skills/poe/STATUS.md) 和 [P0 整改报告](reports/poe/POE_ALPHA6_P0_REMEDIATION.md)。

## 验证

```bash
python scripts/run_ci.py
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/verify_wheel_contents.py --wheel-dir wheelhouse
python -m tsao.cli snapshot --root . --out TSAO-source.zip
python -m tsao.cli verify-archive --archive TSAO-source.zip
```

GitHub Actions 完全只读：在 Ubuntu/Python 3.11–3.12、Windows/Python 3.12 和 macOS/Python 3.12 上校验已提交的来源身份，核验 wheel 确实携带 POE Skill，并生成确定性源码快照。只有在有意修改源码后，维护者才显式重建 `reports/SOURCE_CORE_MANIFEST.tsv`、审阅差异并再次运行 `doctor`。

## 来源身份

`doctor --profile core` 只校验已提交的来源身份，不会自行修改仓库。完成有意变更后，按以下方式显式更新：

```bash
python scripts/build_source_asset_manifest.py --root . --out reports/SOURCE_CORE_MANIFEST.tsv
python -m tsao.cli doctor --root . --profile core
```

机器可读身份见：[源码身份政策](reports/ALPHA6_SOURCE_CORE_STATUS.json)、[完整分发参考](reports/COMPLETE_DISTRIBUTION_REFERENCE.json)和[发行身份](reports/RELEASE_IDENTITY.json)。

## 可信边界

POE 开源软件层为 `EXECUTABLE_SPECIALIST_ALPHA`；历史商业模型运行，以及科学、工程、安全、法律、客户和工业批准仍全部保持 **`NOT_EVALUATED`**，直至真实证据和具名合格人员批准。

`main` 是唯一权威开发线。TSAO 原创代码和文档采用 Apache-2.0；继承资产保留各自来源与再分发边界，详见 [NOTICE.md](NOTICE.md)。
