# TSAO Process Intelligence OS

[English](README.md) · [架构](ARCHITECTURE.md) · [能力矩阵](docs/CAPABILITY_MATRIX.md) · [视觉系统](docs/README_VISUAL_SYSTEM.md)


<!-- CLOSURE_STATUS_START -->
## 当前代码资格与分发边界

- 唯一的 `ci.yml` 在 Windows/Linux、Python 3.11–3.14 上验证源码安装、数值内核、测试、覆盖率、CLI 与性能路径。
- 只要跟踪的 registry 仍为 `CONTROLLED`，公共 wheel 和公共源码快照就必须失败。CI 将这一经验证的 fail-closed 阻断记为 containment 成功，并确保不留下公开工件。
- `artifact_software_qualification=PASS` 不会重新分类源数据，也不等于科学、工程、HSE、客户或工业批准。
- 在权利人/法务/IP/安全部门给出授权决定前，公开分发状态保持 `BLOCKED_CONTROLLED_METADATA_CLASSIFICATION`。
<!-- CLOSURE_STATUS_END -->

**面向化工过程 Skill、受治理数理模型、证据链、来源身份和验收交付的 fail-closed 软件系统。**

<!-- LOCALIZED_VISION_ZH:START -->
## 中文项目愿景图：从反应机理到材料牌号与工艺窗口

<p align="center">
  <img src="docs/localized-vision/process-intelligence-vision-zh.svg" width="100%" alt="TSAO 化工过程智能操作系统中文愿景与数理架构">
</p>

> 图中公式映射当前过程、EPDM、POE 与聚合物通用 Skill 的软件合同；它不是装置标定、客户牌号认证或 HSE 结论。

<!-- LOCALIZED_VISION_ZH:END -->

## 已交付系统

TSAO 安装四个 Skill：`process-general`、`epdm`、`poe` 与 `polymer-general`。受治理的源码检出提供同一组模块、Schema、报告、CLI、测试和 **32 幅确定性 SVG 示意图**。未来可分发 Wheel 必须保持同一清单，但当前公共 Wheel 因受控历史元数据而被有意阻断。`PASS` 只代表软件行为合格；科学、工程、HSE、客户和工业批准继续保持 `NOT_EVALUATED`。

## 验收命令

```bash
python -m pip install -e .[dev]
python -m tsao.cli doctor --root . --profile core
python -m tsao.cli delivery-report --root .
python -m tsao.skillpacks --root .
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit project --root work/demo
python -m tsao.cli epdm validate-v2 --file skills/epdm/fixtures/v2_phase_a2_reference_project.json
python -m tsao.cli epdm canonicalize --file skills/epdm/fixtures/v2_phase_a2_reference_project.json --out work/canonical.json
python -m tsao.cli epdm qualify-acceptance --project skills/epdm/fixtures/v2_phase_a1_reference_project.json --output reports/runtime/EPDM_SOFTWARE_ACCEPTANCE.json --load-samples 7
```

来源身份使用 canonical bytes 的 `SHA256` 绑定。EPDM V2 路径为事务式流程：严格 JSON → 显式版本 → Schema → 冻结 dataclass → 临时 `ContractRegistry` → 跨注册表引用闭合 → 不可变发布。重复键、非有限数、类型混淆、重复 ID 和悬空引用均 fail-closed。

## 受治理数理程式

以下方程是透明的 calculated-reference 软件合同，**不替代合格工艺设计**或完成标定的工业模型。

$$
\frac{d\mathbf{N}}{dt}=F_{in}\mathbf{z}-F_{out}\mathbf{x}+V\boldsymbol{\nu}^{\mathsf T}\mathbf{r}
$$
$$
mC_p\frac{dT}{dt}=\sum F_i h_i-V\sum_j\Delta H_jr_j-UA(T-T_c)
$$
$$
k_j(T)=A_j\exp\!\left(-\frac{E_j}{RT}\right),\qquad r_j=k_j(T)a_s\prod_i C_i^{\alpha_{ij}}
$$
$$
f_m=\frac{r_m}{\sum_n r_n},\qquad \sum_m f_m=1
$$
$$
\mu_k=\sum_{p=0}^{\infty}p^kn_p,\quad M_n\propto\frac{\mu_1}{\mu_0},\quad M_w\propto\frac{\mu_2}{\mu_1},\quad Đ=\frac{\mu_0\mu_2}{\mu_1^2}
$$
$$
\frac{\Delta G_{mix}}{RT}=\frac{\phi_1}{N_1}\ln\phi_1+\frac{\phi_2}{N_2}\ln\phi_2+\chi\phi_1\phi_2
$$
$$
\mathrm{Da}_v=k_v\tau,\qquad \dot S_{gen}=\dot Q\left(\frac1{T_c}-\frac1{T_h}\right)\ge0
$$
$$
e_i=\frac{y_i^{(5)}-y_i^{(4)}}{\mathrm{atol}_i+\mathrm{rtol}_i\max(|y_i|,|y_i^{(5)}|)},\qquad \|\mathbf e\|_2\le1
$$
$$
J(\boldsymbol\theta)=\sum_iw_i[y_i-\hat y_i(\boldsymbol\theta)]^2,\qquad \mathbf{F}=\mathbf{S}^\mathsf{T}\mathbf{W}\mathbf{S}
$$
$$
\operatorname{Cov}(\hat{\boldsymbol\theta})\approx\sigma^2\mathbf F^{-1},\qquad \operatorname{Var}[g]\approx\nabla g^\mathsf T\operatorname{Cov}(\boldsymbol\theta)\nabla g
$$

DOPRI5(4) 只有在缩放误差、守恒、有限性和时间单调 Gate 全部通过时才接受步长。Fisher 信息奇异、证据未闭合或预测点超出适用域时必须返回 `HOLD`，不得制造虚假置信度。

## 已验收性能证据

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

## 使用策略

1. 先把任务路由到最窄的有效 Skill。
2. 参数登记前先登记证据与适用域。
3. 优化前先闭合物料与能量衡算。
4. A2/A3/A4 执行前先发布 canonical contract。
5. 参数拟合与科学资格必须分离。
6. 用不确定度和可辨识性决定下一项实验。
7. 在分类获得授权前持续阻断公共 Wheel 与源码快照；授权后也只能从 exact qualified tree 构建。
8. 只有具名责任人与签署证据才能提升批准状态。

## 验证流程

```bash
python scripts/verify_dependency_lock.py requirements.lock --pyproject pyproject.toml
python scripts/run_ci.py
python skills/epdm/scripts/audit_epdm.py
python skills/poe/scripts/audit_p0.py --root .
python skills/poe/scripts/audit_p1.py --root .
# 当前受控树：以下两条命令必须 fail-closed，且不得留下公开工件。
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/export_source_snapshot.py --root . --out dist/source.zip
# 只有在授权分类允许分发后，才运行 Wheel/运行时验证器。
```

CI 对 Windows 与 Ubuntu 的 Python 3.11–3.14 完整矩阵进行资格验证；安装门同时检查 `pip install --target` 与不继承系统 site-packages 的标准虚拟环境。

视觉系统由历史 21 幅核心图扩展为 32 幅受治理验收图谱。

## 受治理视觉图谱

![acceptance readiness map](docs/assets/readme/acceptance-readiness-map.svg)
![agentic qualification orchestrator](docs/assets/readme/agentic-qualification-orchestrator.svg)
![ai scientific reasoning loop](docs/assets/readme/ai-scientific-reasoning-loop.svg)
![autonomous experiment loop](docs/assets/readme/autonomous-experiment-loop.svg)
![batch parameter scan](docs/assets/readme/batch-parameter-scan.svg)
![control safety cause effect](docs/assets/readme/control-safety-cause-effect.svg)
![dependency lock supply chain](docs/assets/readme/dependency-lock-supply-chain.svg)
![epdm canonical publication pipeline](docs/assets/readme/epdm-canonical-publication-pipeline.svg)
![epdm catalyst kinetics network](docs/assets/readme/epdm-catalyst-kinetics-network.svg)
![epdm identifiability uncertainty](docs/assets/readme/epdm-identifiability-uncertainty.svg)
![epdm multiscale chain](docs/assets/readme/epdm-multiscale-chain.svg)
![epdm process flowsheet](docs/assets/readme/epdm-process-flowsheet.svg)
![epdm product customer bridge](docs/assets/readme/epdm-product-customer-bridge.svg)
![epdm reactor mode map](docs/assets/readme/epdm-reactor-mode-map.svg)
![epdm three level models](docs/assets/readme/epdm-three-level-models.svg)
![evidence gate system](docs/assets/readme/evidence-gate-system.svg)
![governed math stack](docs/assets/readme/governed-math-stack.svg)
![law to grade inverse design](docs/assets/readme/law-to-grade-inverse-design.svg)
![main only delivery lifecycle](docs/assets/readme/main-only-delivery-lifecycle.svg)
![model risk governance](docs/assets/readme/model-risk-governance.svg)
![multiscale digital thread](docs/assets/readme/multiscale-digital-thread.svg)
![performance regression gate](docs/assets/readme/performance-regression-gate.svg)
![process knowledge graph](docs/assets/readme/process-knowledge-graph.svg)
![process package architecture](docs/assets/readme/process-package-architecture.svg)
![process package data model](docs/assets/readme/process-package-data-model.svg)
![recovery recycle risk loop](docs/assets/readme/recovery-recycle-risk-loop.svg)
![simulation integration contract](docs/assets/readme/simulation-integration-contract.svg)
![source snapshot self validation](docs/assets/readme/source-snapshot-self-validation.svg)
![tsao process intelligence os](docs/assets/readme/tsao-process-intelligence-os.svg)
![uncertainty decision landscape](docs/assets/readme/uncertainty-decision-landscape.svg)
![universal process package](docs/assets/readme/universal-process-package.svg)
![verification pipeline](docs/assets/readme/verification-pipeline.svg)

## 责任边界

`main` 是唯一权威分支。TSAO 不替代实验数据、商业物性包、设备与泄放设计、HAZOP/LOPA/SIL、法律与环保审查、客户试验或生产运行批准。

<!-- CURRENT_MAIN_ACCEPTANCE_V2:START -->
## 当前实现：代码、数学与使用策略

![中文代码与数学合同概念图](docs/current-main/tsao-processing-current-main-zh.svg)

> 当前交付是软件参考数值与工艺研发框架；科学、工程、HSE、客户与工业性能批准均保持 NOT_EVALUATED。

#### 有限物料衡算残差

$$
r=\sum_i F_{i,\mathrm{in}}-\sum_j F_{j,\mathrm{out}}+\sum_k G_k
$$

这是通用 `balance_residual` 的符号约定。所有项必须采用相同物理量、时间基准与单位；正 G 表示生成，负 G 表示消耗。残差接近零只是给定账目的闭合检查，不能代替模型机理或工业数据验证。

源码对应: [`tsao/science.py`](tsao/science.py)

#### 逐分量自适应误差

$$
e=\max_i\frac{|y_i^{(5)}-y_i^{(4)}|}{a+r\max(|y_{n,i}|,|y_i^{(5)}|)}\le1
$$

Dormand–Prince 5(4) 实际实现先逐分量缩放，再取最大值；不能写成两个向量范数之比。接受步还要求状态非负约束和守恒合同成立；达到步数或最小步长边界可能返回 HOLD。不同状态尺度需要在建模与容差设置中明确。

源码对应: [`skills/epdm/numerical_integration.py`](skills/epdm/numerical_integration.py)

#### 局部可辨识性检查

$$
\operatorname{rank}_{\mathrm{num}}\!\left(J/\max_{ij}|J_{ij}|\right)=p
$$

非零、有限雅可比先按最大绝对元素缩放，随后检查数值秩是否等于参数列数 p；零矩阵单独处理。满列秩是给定观测与局部线性化条件下的诊断，不证明全局参数唯一性、良好条件数或工程批准。

源码对应: [`tsao/science.py`](tsao/science.py)

### 使用与验收顺序

1. 先核对安装环境、输入结构、单位、有效范围与执行权限。
2. 按上面的源码锚点区分原生实现、解释性合同和外部执行要求。
3. 先运行快速回归和完整质量门，再用固定提交执行长期回归。
4. 逐项保存原始日志、机器报告和限制；任何缺失证据不得写成 PASS。

```bash
python scripts/run_ci.py
```

每次修复均须绑定新提交重新测试。基线回归、两段各三小时的重复回归、浏览器图形检查和外部工程认证是不同证据，不可互相替代。没有原始回执时，不宣称已完成六小时验收。

源码锚点: [`tsao/process_package.py`](tsao/process_package.py) · [`skills/epdm/kinetics.py`](skills/epdm/kinetics.py) · [`skills/poe/kinetics.py`](skills/poe/kinetics.py)

<!-- CURRENT_MAIN_ACCEPTANCE_V2:END -->


## 历史性能资格边界

当前具有阻断效力的性能资格，在同一运行器和同一 Python 解释器上，将当前源码树与 alpha.14 父基线比较。数值等价、同路径耗时、优化路径收益保持率、规模扩展检查以及所有非预期缺失工作负载仍然保持 fail-closed。

alpha.10 的 `wheel_content_verification` 计时仅在该历史工作负载缺失时记为 `NOT_APPLICABLE`，因为公共 wheel 生成已被 `BLOCKED_CONTROLLED_METADATA_CLASSIFICATION` 明确阻断。当前由源码资格与分发封闭回归替代这一已退役的公共制品工作负载。该例外不允许生成 wheel 或源码快照，不放宽任何当前性能阈值，也不把软件资格扩大解释为科学、工程、HSE、客户或工业批准。


<!-- closure:qualification-boundary -->
## 软件资格与受控分发边界

性能门通过经过测试、失败封闭的注释器记录仓库尺度工作量，再比较同一工作合同下的结果。缺失、非有限、为零或身份不一致的工作量元数据会被拒绝，不能被转换成有利的性能结论。

软件资格绑定到精确源码树。测试、doctor、覆盖率或性能门通过，均不构成公开 wheel、sdist 或源码快照的授权。只要受控历史元数据仍被标记为项目受控，公共制品就必须继续以 `BLOCKED_CONTROLLED_METADATA_CLASSIFICATION` 失败封闭，并且不得留下可分发制品。
