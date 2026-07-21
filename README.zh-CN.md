# TSAO 化学工艺科研与工业化操作系统

**TSAO-PROCESSING-SKILL** 是一个面向化学工艺全过程开发的开源、软件中立、可追溯、可审计 Agent Skill 项目。

TSAO 表示：**Traceable（可追溯）· Scientific（科学）· Auditable（可审计）· Operational（可执行）**。

它不是“问一句就生成一份看似完整的工艺包”，而是把任务组织为受控工程计划：

`需求 → 证据 → 化学路线 → 分析测量 → 物性 → 动力学 → 反应器 → 分离回收 → 小试 → 连续台架 → 中试 → 示范 → 工业设计 → 控制 → 安全可靠性 → 经济环境知识产权 → 产品资格 → 技术包 → 转移 → 现场持续改进`

## 三层架构

1. **母技能层**：适用于聚合、石油化工、精细化工、催化、生物、电化学、无机、固体和配方过程。
2. **专业子技能层**：`skills/epdm/`、`skills/poe/`、`skills/polymer-general/`。
3. **保证与工具层**：Schema、模板、科学计算、保证图、数字线程、Gate 状态机、变更传播、发布和洁净室审计。

## 使用

```bash
python -m pip install -e .[dev]
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
python scripts/run_ci.py
```

Agent 使用时先读取 `SKILL.md`，再执行 `prompts/TSAO_PROJECT_EXECUTION_PROMPT.md`。

## 强制边界

自动生成项目、模型或报告，不代表真实技术已通过。催化剂合成、高压实验、商业模拟、HAZOP/LOPA/SIL、FTO、客户试验、中试和工业性能保证必须由合格团队真实执行。所有未执行项目保持 `NOT_EVALUATED`。