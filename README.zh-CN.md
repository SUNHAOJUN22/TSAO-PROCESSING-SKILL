# TSAO 化学工艺科研与工业化操作系统

**TSAO-PROCESSING-SKILL 0.1.0-alpha.3** 是一个面向化学工艺全过程开发的开源、软件中立、可追溯、可审计 Agent Skill 项目。

TSAO 表示：**Traceable（可追溯）· Scientific（科学）· Auditable（可审计）· Operational（可执行）**。

它不是“问一句就生成一份看似完整的工艺包”，而是把任务组织为受控工程计划，并要求真实建立项目文件、证据、模型、实验、门禁和验收记录：

`需求 → 证据 → 化学路线 → 分析测量 → 物性 → 动力学 → 反应器 → 分离回收 → 小试 → 连续台架 → 中试 → 示范 → 工业设计 → 控制 → 安全可靠性 → 经济环境知识产权 → 产品资格 → 技术包 → 转移 → 现场持续改进`

## 三层架构

1. **母技能层**：统一 G0–G18、证据、模型风险、保证图、变更传播和技术批准边界。
2. **专业子技能层**：
   - `skills/process-general/`：非聚合通用化工、石化、精细化工、生物、电化学、结晶与固体过程；
   - `skills/epdm/`：EPDM 催化剂—三元聚合—回收—胶料—客户资格；
   - `skills/poe/`：SJTU POE 溶液聚合、稳态/动态、放大与验收；
   - `skills/polymer-general/`：其他聚合机理和加工/改性路线。
3. **保证与工具层**：Schema、模板、科学计算、保证图、数字线程、Gate 状态机、变更传播、发布和洁净室审计。

完整调用必须执行项目分类、资料盘点、研究问题与竞争路线、可证伪实验、模型资格、衡算、放大主张、技术包和验收矩阵；不得只返回泛化建议。

## 使用

```bash
python -m pip install -e .[dev]
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
python scripts/run_ci.py
```

Agent 使用时先读取 `SKILL.md`，再执行 `prompts/TSAO_PROJECT_EXECUTION_PROMPT.md`。

## GitHub 源码与完整发行包

GitHub 分支保存可浏览、可安装和可评审的母层源码及专业合同。独立验证的完整发行包还包含 EPDM v9、SJTU-POE 和通用聚合完整源树及历史发布身份。完整资产进入公共源码树时必须遵守 `docs/VERSIONED_ASSET_INGESTION.md`，不得用不透明 Base64 分片代替源码。

## 强制边界

自动生成项目、模型或报告，不代表真实技术已通过。催化剂合成、高压实验、商业模拟、设备/泄放设计、HAZOP/LOPA/SIL、FTO、客户试验、中试和工业性能保证必须由合格团队真实执行。所有未执行项目保持 `NOT_EVALUATED`。
