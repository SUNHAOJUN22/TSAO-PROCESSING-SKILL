# TSAO 化学工艺智能研发操作系统

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.4-orange.svg)](CHANGELOG.md)

**把一个化学工艺问题，转化为可追溯、可执行、可验收的研发与工业化程序。**

TSAO = **Traceable（可追溯）· Scientific（科学）· Auditable（可审计）· Operational（可执行）**。它不把文献参数当装置设定值，不把模拟收敛当技术批准，也不把自动生成文件当实验完成。

[English](README.md) · [核心合同](SKILL.md) · [系统架构](ARCHITECTURE.md) · [路线图](ROADMAP.md) · [能力矩阵](docs/CAPABILITY_MATRIX.md)

## 能做什么

- 新工艺、复制国产化、催化剂/路线/产品开发；
- 小试、连续台架、中试、示范和工业放大；
- 技改、脱瓶颈、异常诊断和第三方工艺包审查；
- 聚合、石化、精细化工、生物、电化学、结晶粉体和配方过程。

## 四个专业入口

| 子技能 | 适用任务 | 当前深度 |
|---|---|---|
| `process-general` | 非聚合专属的反应、物性、反应器、分离、控制、安全和放大 | 14 个结构化专业模块 |
| `epdm` | EPM/EPDM 从催化剂到客户线 | 完整继承 v9 资格体系 |
| `poe` | 上海交通大学 POE 溶液聚合与工艺包方法 | 完整保留动力学、流程、动态和验收源树 |
| `polymer-general` | 其他聚合、改性和配方路线 | 机理中立的全生命周期体系 |

## 一次调用实际生成什么

`任务 → 路由 → G0–G18 × 14条工作流 → 证据/假设 → 实验/模型 → 小试/台架/中试/示范 → 工艺包 → 验收/转移`

运行 `tsao init` 会立即生成 **266 个 fail-closed 工作包**、G0–G18 Gate、M0–M9 成熟度记录和外部执行状态，不再只给目录或建议。

## 快速使用

```bash
python -m pip install -e .[dev]
python -m tsao.cli route "连续催化反应器与溶剂回收"
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
python scripts/run_ci.py
```

Agent 先读取 `SKILL.md`，再执行 `prompts/TSAO_PROJECT_EXECUTION_PROMPT.md`。

## 质量门

出现以下任一情况即阻断 Gate：证据过期或矛盾、模型不可辨识或超出适用域、衡算不闭合、放大相似性未说明、外部审查未执行、批准没有证据或实名批准人。

测试同时覆盖正常用例与恶意负例，包括 Gate 越权、证据/模型风险、科学计算、项目生成、专业能力谱系、恶意 ZIP、确定性构建和洁净室复验。

## 必须保留的边界

CI 只证明**软件工件内部一致**。真实化学、设备、控制、泄放设计、HAZOP/LOPA/SIL、FTO、客户认证、中试和工业性能仍保持 `NOT_EVALUATED`，必须由合格团队以真实证据批准。
