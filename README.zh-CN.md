# TSAO 化学工艺智能研发操作系统

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.7-orange.svg)](CHANGELOG.md)

**证据 → 实验 → 模型 → 放大 → 工艺包 → 验收 → 现场学习。**

TSAO 把化工问题转化为可追溯、默认拒绝越权的研发程序。文献数值不是装置设定值，模拟收敛不是批准，自动生成文件也不等于真实工作已经完成。

[English](README.md) · [执行合同](SKILL.md) · [系统架构](ARCHITECTURE.md) · [能力矩阵](docs/CAPABILITY_MATRIX.md)

## 专业入口

| 入口 | 当前范围 |
|---|---|
| `process-general` | 反应、物性、反应器、分离循环、控制、HSE、可靠性和放大 |
| `epdm` | EPM/EPDM 催化剂、三元聚合、回收、配混和客户资格 |
| `poe` | **带 P1 参考内核的可执行专家 alpha**：139 项资产谱系、十二模块、动力学/估计/物性/反应器/动态/放大参考及证据审计 v2 |
| `polymer-general` | 其他聚合、改性、配方、反应加工和循环利用 |

四个入口统一继承 G0–G18 Gate、十四条专业工作流、M0–M9 成熟度、证据状态、模型风险和具名人工批准。

## 开始

```bash
python -m pip install -e .[dev]
python -m tsao.cli doctor --root . --profile core
python -m tsao.cli route "POE 溶液聚合与溶剂回收"
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
python -m tsao.cli poe status --root .
python -m tsao.cli poe reference-demo
```

## POE alpha.7

当前 POE 包包括：

- 139/139 项受控历史资产、18/18 项需求和 7 项真实冲突/偏差；
- 十二个机器可读专业模块合同；
- 矩模型动力学、有界参数估计与可辨识性、物性/传递、PFR/CSTR、移热、FOPDT 过渡、循环记忆及放大相似性的透明 P0/P1 参考实现；
- 模型资产护照，以及同时核查正文、哈希、结构化记录、证据状态、需求、冲突和审批的工艺包审计 v2；
- 去标识化/合成 fixture 与恶意输入测试，不公开受控 Aspen、MATLAB、Origin、CFD 或合同文件；
- wheel 内容与安装后运行验证。

详见 [POE 状态](skills/poe/STATUS.md) 和 [P1 整改报告](reports/poe/POE_ALPHA7_P1_REMEDIATION.md)。

## 验证

```bash
python scripts/run_ci.py
python skills/poe/scripts/audit_p0.py --root .
python skills/poe/scripts/audit_p1.py --root .
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/verify_wheel_contents.py --wheel-dir wheelhouse
python scripts/verify_wheel_runtime.py --wheel-dir wheelhouse
```

GitHub Actions 在 Ubuntu/Python 3.11–3.12、Windows/Python 3.12 和 macOS/Python 3.12 上运行同一套只读资格门。POE 核心库分支覆盖率门槛不低于 75%，命令行薄封装由端到端测试覆盖。源码身份冻结提交，运行时报告不进入冻结清单。

## 可信边界

POE 开源层状态是 `EXECUTABLE_SPECIALIST_ALPHA_P1_REFERENCE`。历史商业模型以及科学、工程、HSE、法律、客户和工业批准均保持 **`NOT_EVALUATED`**，直至由当前项目证据和具名合格人员批准。

`main` 是唯一权威分支。TSAO 原创代码和文档采用 Apache-2.0；继承资产的来源及再分发边界见 [NOTICE.md](NOTICE.md)。
