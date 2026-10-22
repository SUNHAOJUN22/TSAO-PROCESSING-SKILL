# TSAO 工艺智能计算与审查工具集

[English](README.md) · [架构](ARCHITECTURE.md) · [能力矩阵](docs/CAPABILITY_MATRIX.md) · [图形说明](docs/README_VISUAL_SYSTEM.md)

![从工艺数量走向可追溯决策——中文功能愿景图](docs/assets/vision-zh.png)

TSAO 是基于 Python 3.11+ 的工艺开发工具集，提供带单位的物料衡算、通用工艺包审查、EPDM/POE 参考模型、证据记录和保守的验收状态判定。`process-general`、`epdm`、`poe`、`polymer-general` 四个技能域共享命令行与来源校验机制。仓库交付的是计算和审查代码；没有独立的受认证 Web 服务，也不直接控制生产装置。

上图表达项目愿景，分子、曲线和光效是概念设计，不是实验测量、已校准预测或工业性能证据。下文公式逐项对应代码，并说明适用条件。

## 已实现的功能

| 功能 | 真实入口 | 输出与边界 |
|---|---|---|
| 通用工艺包审查 | [`validate_process_package`](tsao/process_package.py) | 拓扑、组成、质量/组分/能量残差、状态与证据引用；属于对输入工艺包的软件审查 |
| 带量纲的物料衡算 | [`evaluate_material_balance`](skills/poe/material_balance.py) | 显式质量/摩尔基准、单位转换、反应、积累及分组分容差 |
| 独立决策轨道 | [`derive_decision_tracks_from_root`](skills/poe/acceptance_status.py) | 软件、工程、HSE 分别判定；本地证据文件字节必须匹配声明 SHA-256 |
| EPDM 合同与积分 | [`canonical_loader.py`](skills/epdm/canonical_loader.py)、[`numerical_integration.py`](skills/epdm/numerical_integration.py) | 版本化合同、反应/状态关联及自适应积分 |
| POE 参考动力学 | [`kinetics.py`](skills/poe/kinetics.py)、[`estimation.py`](skills/poe/estimation.py) | RK4 轨迹、单速率常数有界拟合；不是工业参数发布 |
| 来源与交付 | [`provenance.py`](tsao/provenance.py)、[`skillpacks.py`](tsao/skillpacks.py) | 规范化源码身份、四技能清单及发行边界检查 |

### 软件验收与分发边界

`artifact_software_qualification=PASS` 只说明受测源码及软件合同满足对应检查。科学、工程、HSE、客户及工业应用批准各有独立证据要求。SHA-256 相符说明文件身份一致，不能自行证明测量真实或审核人的身份与权限。

仓内历史来源元数据仍属于受控分类。公开 wheel、sdist 和源码快照继续以 `BLOCKED_CONTROLLED_METADATA_CLASSIFICATION` 阻断；本次修复不改变该分类。CI 核验拒绝路径且不得留下可分发工件。权利人、法律/IP/安全分类决定尚未完成时，使用已获授权的源码检出开展软件验证。

## 安装与启动

使用标准虚拟环境，**不继承系统 site-packages**。现有 CI 矩阵覆盖 Windows/Ubuntu 与 Python 3.11–3.14；结论只适用于实际受测的提交。

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
python scripts/verify_dependency_lock.py requirements.lock --pyproject pyproject.toml
python -m tsao.cli doctor --root . --profile core
python -m tsao.skillpacks --root .
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit project --root work/demo
```

初始化项目和模板是起始记录。后续操作前读取 `status`、`errors`、`holds` 和 `reason_codes`，不能把成功生成文件解释为设计获批。

```bash
python -m tsao.cli package template --family generic
python -m tsao.cli package audit --file path/to/process-package.json
python -m tsao.cli epdm validate-v2 --file skills/epdm/fixtures/v2_phase_a2_reference_project.json
python -m tsao.cli epdm canonicalize --file skills/epdm/fixtures/v2_phase_a2_reference_project.json --out work/canonical.json
```

`package audit` 对失败或待决工艺包返回非零退出码。重复 JSON 键与非有限 JSON 数值会被拒绝，不允许后一个键静默覆盖前一个证据。默认 `STEADY_PROCESS` 要求非空设备、物流和显式进出边界；`METADATA_ONLY` 可用于文档框架，但输出 `balance_status=NOT_EVALUATED`，不能获得总状态 `PASS`。

## 数理程序与代码映射

### 1. 组成与工艺拓扑

每股物流的质量分数满足：

$$
0\le w_i\le1,\qquad \left|\sum_iw_i-1\right|\le\varepsilon_w,
\qquad \dot m_i=\dot m\,w_i.
$$

物流源端和目的端必须是已声明设备或边界节点；设备进出流引用须与物流方向一致，同一连接不得重复登记。实现见 [`process_package.py`](tsao/process_package.py)。

### 2. 稳态总质量与组分闭合

通用工艺包以 kg/h 表示质量流量，以 kW 表示焓流与热负荷。组分生成/消耗项需要明确的反应依据。

$$
r_m=\sum_{in}\dot m-\sum_{out}\dot m,
\qquad r_i=\sum_{in}\dot m_i+G_i-\sum_{out}\dot m_i-C_i.
$$

代码的相对残差采用规范单位数值基准下的缩放下限 1：

$$
e_m=\frac{|r_m|}{\max(|\dot m_{in}|,|\dot m_{out}|,1)},
\qquad e_i=\frac{|r_i|}{\max(\dot m_{i,in}+G_i,\dot m_{i,out}+C_i,1)}.
$$

此处数值下限是一种残差缩放约定，不是无量纲物理常数。必须按工艺规模选择容差；残差接近零只表示输入之间一致，不说明输入来自准确实验。

### 3. 稳态能量闭合

$$
r_H=\sum_{in}\dot H+Q-\sum_{out}\dot H,
\qquad e_H=\frac{|r_H|}{\max(|\dot H_{in}|+|Q|,|\dot H_{out}|,1)}.
$$

约定正热负荷向系统加热。除非输入焓流已一致包含相应项，参考核不另外计算动能和势能。

### 4. POE 带单位的物料衡算

物料衡算入口接受 `{value, unit, basis}`，质量基准转换到 kg/s，物质的量基准转换到 mol/s。分子量以 g/mol 表示时：

$$
\dot n_i=\frac{1000\dot m_i}{M_i},\qquad
\dot m_i=\frac{M_i\dot n_i}{1000}.
$$

质量基准的反应检查要求输入计量数与分子量一致：

$$
\sum_i\nu_{ij}M_i\approx0,\qquad R_i=\sum_j\nu_{ij}\dot\xi_j.
$$

该检查依据已提供的分子量，并非元素级反应机理证明。缺少跨基准转换所需的分子量时，计算拒绝继续。

$$
r_i=\dot N_{i,acc}-(F_{i,in}-F_{i,out}+G_i-C_i),
\qquad |r_i|\le a_i+r\,s_i.
$$

其中 $a_i$ 与残差具有相同流量单位，$r$ 无量纲，$s_i>0$ 是显式组分参考尺度。必须逐组分通过，不能靠正负误差抵消获得总合格。稳态模式要求明确稳态声明和严格为零的积累；动态模式必须提供与衡算一致的积累量。

### 5. 有限数值与可表示范围

[`numeric_contract.py`](tsao/numeric_contract.py) 检查输入以及和、积、商的计算结果。单个输入有限不意味着聚合结果有限：

$$
\operatorname{isfinite}(x_{input})\ \not\Rightarrow\
\operatorname{isfinite}\!\left(\sum_i x_i\right).
$$

非零单位转换若下溢为零会被拒绝。公开工况/工艺包审计入口返回 `FAIL`，不可用指标保留为 JSON `null`；直接数理函数抛出 `ValueError`，v16 衡算使用其子类 `ContractError`。不可表示的受审衡算不能被替换为物理零或 JSON NaN/Infinity，也不能用非有限容差放行。

公开 [`validate_process_case`](skills/poe/qualification.py) 先检查外部进料、外部产品和声明损失的聚合值，再计算：

$$
e_{case}=\frac{|F_{external}-P_{external}-L_{declared}|}{F_{external}},
\qquad F_{external}>0.
$$

总量或残差不可表示时返回 `FAIL`；有限残差超过声明容差时返回 `HOLD`。POE 工艺包先核对实际文件字节数与 SHA-256，再调用同一数理入口，因此文件完整性通过不能掩盖衡算错误。v16/v17 兼容入口也检查单位换算、残差求和和实际容差；两版已有的规范单位参考尺度下限分别保持 $10^{-30}$ 与 $1$。调用方应按规范单位选择有量纲的绝对容差与无量纲的相对容差；这些工程约定不能直接当作可任意缩放计量系数的守恒检验。

[`process_general.py`](tsao/process_general.py) 提供以下有界参考计算：

$$
A=\frac{\mathrm{MTBF}}{\mathrm{MTBF}+\mathrm{MTTR}},\qquad
X_{CSTR}=\frac{k\tau}{1+k\tau},\qquad
\eta_F=\frac{n z F}{I t},\quad F=96485.33212\ \mathrm{C\,mol^{-1}}.
$$

可用率先缩放时间再相加；CSTR 转化率和法拉第效率避免中间乘积溢出破坏仍可表示的比值。相等的正 MTBF/MTTR 始终给出 $A=0.5$，包括大数值压力用例。最终非零结果若低于浮点可表示范围会被拒绝。CSTR/PFR 在极大正暴露量下的有界转化率可以正确舍入为一，这与把不可表示流量静默变成零有明确区别。法拉第效率仍要求电子数、电流和时间为正，并拒绝超过 $1+10^{-9}$ 的效率；这些函数保留各自模型假设，不能代替设备可靠性或电化学实验认证。

严格 CSV 入口 [`check_balance.py`](skills/polymer-general/scripts/check_balance.py) 对每个组分和总量采用相同的有限换算与求和规则：大数流量抵消时保留小残差，非零 kg/h 换算后若成为零 kg/s 则拒绝继续。运行 `python skills/polymer-general/scripts/check_balance.py your-balance.csv`；非法数值合同退出码为 2，有限但不闭合的衡算输出 `FAIL`，同样退出 2。

[`tests/test_public_numeric_boundaries.py`](tests/test_public_numeric_boundaries.py) 从上述公开入口与真实 CSV 命令回归，包括修改数理工况后重新计算真实文件摘要的 POE 包、大数有限抵消、溢出/下溢拒绝、合法物理零以及既有容差约定。

### 6. 自适应积分与参数拟合

EPDM 的 Dormand–Prince 5(4) 使用逐分量缩放后取最大值：

$$
e=\max_i\frac{|y_i^{(5)}-y_i^{(4)}|}
{a+r\max(|y_{n,i}|,|y_i^{(5)}|)}\le1.
$$

这不是两个向量范数的比。接受步长还受关联、有限状态、非负状态及守恒检查约束；时间/步数预算耗尽可返回 `HOLD`。POE 参考动力学采用经典 RK4：

$$
y_{n+1}=y_n+\frac{h}{6}(k_1+2k_2+2k_3+k_4).
$$

单速率常数参考拟合使用：

$$
X(t;k)=1-e^{-kt}=-\operatorname{expm1}(-kt),\qquad
J(k)=\sum_iw_i[X(t_i;k)-X_i]^2,
\quad k_{min}\le k\le k_{max}.
$$

局部敏感度与信息量诊断为：

$$
S_i=t_i e^{-kt_i},\qquad I=\sum_iw_iS_i^2.
$$

可辨识性取决于所选模型、观测与数值阈值。局部信息量不能证明动力学机理全局唯一，也不能代替独立工业参数确认。

## 状态、证据与使用策略

适用决策项采用一致的保守规则：显式 `FAIL` 必须传播；`HOLD`、`CONDITIONAL`、未知和未评价项不能升级为 `PASS`。输出同时保留声明状态、重新计算状态以及不一致原因。

POE 工程/HSE 轨道需要 `QUALIFIED`、`decision_use=true`、具名审阅者、相对工件路径及匹配的 SHA-256。缺文件、符号链接、路径越界、重复证据 ID、冲突的 `status/result`、非法引用均不能获得资格。没有工件根目录的纯内存声明保持未评价或待决；软件结果的 `status/errors/holds` 与可选布尔 `pass` 也必须一致。真实审核权限仍由外部治理负责。

建议按以下顺序使用：

1. 先登记来源、原始单位、方法、不确定度和适用范围，再输入参数。
2. 选择最小适用技能域与明确流程类型，先解决拓扑和单位转换。
3. 在拟合、筛选或优化前闭合每个组分与能量衡算。
4. 针对可追溯观测拟合，预留独立验证数据，记录参数不确定度。
5. 分开保存软件验证、科学模型验证、工程审查和 HSE 审查结论。
6. 每次代码或数据变更后重新运行门禁，保留实际提交和原始日志。

## 测试与交付

```bash
python scripts/run_ci.py
python skills/epdm/scripts/audit_epdm.py
python skills/poe/scripts/audit_p0.py --root .
python skills/poe/scripts/audit_p1.py --root .
python scripts/sync_readme_visuals.py --check
# 受控历史元数据仍存在时，以下两条必须阻断且不得输出可分发工件：
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/export_source_snapshot.py --root . --out dist/source.zip
```

原 75% 门槛保持不变，衡量的是 `coverage.py` 启用分支跟踪后报告的语句与分支综合覆盖率。[`scripts/run_ci.py`](scripts/run_ci.py) 将统计范围限定为 `skills.poe`、`skills.epdm`、`tsao.process_package` 和 `tsao.skillpacks`，并排除 `skills/poe/scripts/*` 与 `skills/epdm/scripts/*`。新增入口测试涵盖各域非通过状态、空拓扑、溢出/下溢、非法软件结果、证据文件篡改和重复 JSON 键。测试中的历史/新增夹具属于合成软件例，不是实际工程批准。请读取实际提交对应的 CI 结果，不引用旧徽章作为本次验收。

[七仓验收执行 Prompt](https://github.com/SUNHAOJUN22/TsaoSciResearcher/blob/main/docs/SEVEN_REPOSITORY_ACCEPTANCE_PROMPT.md) 规定每仓两段各三小时的成功测试进程时间。本地回归完成不表示已经取得六小时凭证；分段软件回归与连续装置运行、在线服务稳定性和外部求解器认证应分别报告。

## 历史性能参考

以下表格保留已有版本的性能比较，不能当作本次修复的新测量。当前 CI 仍按配置基线在同一运行器重做数值一致性与性能比较，所有阈值保持不变。详情见[性能记录](reports/PERFORMANCE_TECHNOLOGY_REVIEW.md)。

<!-- PERFORMANCE_RESULTS_START -->
| 负载 | 基线中位耗时 | 优化后中位耗时 | 比率 | 峰值内存 | 等价合同 |
|---|---:|---:|---:|---:|---|
| EPDM 三级模型，64 个位点族 | 129.96 µs | 131.24 µs | 0.99× | 37.23 KiB | 精确一致 |
| EPDM 三级模型，512 个位点族 | 937.65 µs | 946.63 µs | 0.99× | 276.29 KiB | 精确一致 |
| EPDM 半连续物料—能量单步 | 13.24 µs | 14.34 µs | 0.92× | 3.12 KiB | 精确一致 |
| EPDM 半连续轨迹，10,000 次公共单步 | 129.11 ms | 142.58 ms | 0.91× | 4.35 MiB | 精确一致 |
| EPDM 筛选，1,000 组标量情景 | 13.50 ms | 13.61 ms | 0.99× | 566.29 KiB | 精确一致 |
| POE RK4，400 步 | 13.93 ms | 6.64 ms | 2.10× | 303.02 KiB | 精确一致 |
| POE RK4，10,000 步 | 345.90 ms | 165.92 ms | 2.08× | 7.26 MiB | 精确一致 |
| POE 有限差分 Jacobian，8 × 200 | 503.52 µs | 493.41 µs | 1.02× | 33.92 KiB | 精确一致 |
| POE 单参数拟合，401 点 | 1.00 ms | 1.01 ms | 0.99× | 31.07 KiB | 精确一致 |
| POE 动态响应，10,000 点 | 241.69 µs | 241.34 µs | 1.00× | 569.67 KiB | 精确一致 |
| 通用工艺包，500 台设备 | 4.43 ms | 4.38 ms | 1.01× | 179.53 KiB | 精确一致 |
| 通用工艺包，5,000 台设备 | 44.28 ms | 44.12 ms | 1.00× | 1.95 MiB | 精确一致 |
| 源身份，300 文件构建与核验 | 25.91 ms | 24.80 ms | 1.04× | 424.10 KiB | 精确一致 |
| 源身份，3,000 文件构建与核验 | 228.88 ms | 229.13 ms | 1.00× | 1.68 MiB | 精确一致 |
| 仓库 Doctor，core 配置 | 126.28 ms | 129.83 ms | 0.97× | 1.29 MiB | 容差 / 语义一致 |
| 四 Skill 库存 | 5.95 ms | 6.35 ms | 0.94× | 137.26 KiB | 容差 / 语义一致 |
| Wheel 内容核验 | 2.93 ms | 3.13 ms | 0.94× | 593.27 KiB | 容差 / 语义一致 |
| EPDM 筛选，1,000 组广播情景 | 13.50 ms | 1.41 ms | 9.56× | 613.93 KiB | 容差 / 语义一致 |
| EPDM 半连续轨迹，一次校验 10,000 步 | 129.11 ms | 47.21 ms | 2.73× | 4.35 MiB | 精确一致 |
| POE RK4 仅终态，10,000 步 | 345.90 ms | 143.77 ms | 2.41× | 5.59 KiB | 容差 / 语义一致 |

| 尺度对 | 归一化耗时比 | 上限 | Gate |
|---|---:|---:|---|
| EPDM 三级模型，64 个位点族 → EPDM 三级模型，512 个位点族 | 0.902 | 1.25 | 通过 |
| 通用工艺包，500 台设备 → 通用工艺包，5,000 台设备 | 1.006 | 1.25 | 通过 |
| 源身份，300 文件构建与核验 → 源身份，3,000 文件构建与核验 | 0.924 | 1.25 | 通过 |
<!-- PERFORMANCE_RESULTS_END -->

## 受控参考图集

保留的 32 张确定性 SVG 是架构与工程合同参考图，与顶部中文 AI 愿景图分开理解；它们不构成真实计算或工业资格证据。

<details>
<summary>展开原有架构与数理合同参考图</summary>

![Acceptance Readiness Map](docs/assets/readme/acceptance-readiness-map.svg)
![Agentic Qualification Orchestrator](docs/assets/readme/agentic-qualification-orchestrator.svg)
![Ai Scientific Reasoning Loop](docs/assets/readme/ai-scientific-reasoning-loop.svg)
![Autonomous Experiment Loop](docs/assets/readme/autonomous-experiment-loop.svg)
![Batch Parameter Scan](docs/assets/readme/batch-parameter-scan.svg)
![Control Safety Cause Effect](docs/assets/readme/control-safety-cause-effect.svg)
![Dependency Lock Supply Chain](docs/assets/readme/dependency-lock-supply-chain.svg)
![Epdm Canonical Publication Pipeline](docs/assets/readme/epdm-canonical-publication-pipeline.svg)
![Epdm Catalyst Kinetics Network](docs/assets/readme/epdm-catalyst-kinetics-network.svg)
![Epdm Identifiability Uncertainty](docs/assets/readme/epdm-identifiability-uncertainty.svg)
![Epdm Multiscale Chain](docs/assets/readme/epdm-multiscale-chain.svg)
![Epdm Process Flowsheet](docs/assets/readme/epdm-process-flowsheet.svg)
![Epdm Product Customer Bridge](docs/assets/readme/epdm-product-customer-bridge.svg)
![Epdm Reactor Mode Map](docs/assets/readme/epdm-reactor-mode-map.svg)
![Epdm Three Level Models](docs/assets/readme/epdm-three-level-models.svg)
![Evidence Gate System](docs/assets/readme/evidence-gate-system.svg)
![Governed Math Stack](docs/assets/readme/governed-math-stack.svg)
![Law To Grade Inverse Design](docs/assets/readme/law-to-grade-inverse-design.svg)
![Main Only Delivery Lifecycle](docs/assets/readme/main-only-delivery-lifecycle.svg)
![Model Risk Governance](docs/assets/readme/model-risk-governance.svg)
![Multiscale Digital Thread](docs/assets/readme/multiscale-digital-thread.svg)
![Performance Regression Gate](docs/assets/readme/performance-regression-gate.svg)
![Process Knowledge Graph](docs/assets/readme/process-knowledge-graph.svg)
![Process Package Architecture](docs/assets/readme/process-package-architecture.svg)
![Process Package Data Model](docs/assets/readme/process-package-data-model.svg)
![Recovery Recycle Risk Loop](docs/assets/readme/recovery-recycle-risk-loop.svg)
![Simulation Integration Contract](docs/assets/readme/simulation-integration-contract.svg)
![Source Snapshot Self Validation](docs/assets/readme/source-snapshot-self-validation.svg)
![Tsao Process Intelligence Os](docs/assets/readme/tsao-process-intelligence-os.svg)
![Uncertainty Decision Landscape](docs/assets/readme/uncertainty-decision-landscape.svg)
![Universal Process Package](docs/assets/readme/universal-process-package.svg)
![Verification Pipeline](docs/assets/readme/verification-pipeline.svg)

</details>

## 责任边界

`main` 是权威分支。本工具支持可复现计算和审查；有资质的工艺工程、外部物性软件、实验、设备/泄放设计、HAZOP/LOPA/SIL、运行批准与客户验收仍须独立完成。
