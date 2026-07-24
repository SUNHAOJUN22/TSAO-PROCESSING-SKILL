# TSAO 工艺智能操作系统

**面向所有工艺包的一套证据化、可审计、默认失败关闭的操作系统；EPDM 是旗舰专业路线，POE 是证据谱系最完整的专业路线。**

## 三个可执行入口

```bash
python -m pip install -e .[dev]
python -m tsao.cli doctor --root . --profile core
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
python -m tsao.cli package template --family "连续化工过程"
python -m tsao.cli epdm reference-demo
python -m tsao.cli poe reference-demo
```

| 入口 | 当前可执行能力 |
|---|---|
| `tsao package` | 通用设计基础、物流设备、物料能量、控制、HSE、证据、验收和审批审计 |
| `tsao epdm` | EPDM 旗舰：活性位、E/P/二烯三元动力学、结构/凝胶、反应移热、回收、混炼硫化、客户桥接与工艺包审计 |
| `tsao poe` | POE P1 参考内核及 139 项历史资产证据谱系 |

## EPDM 旗舰包

包含 14 个机器可读专业模块和 20 条 Gate 要求，覆盖催化剂工业基准、活性位、三元插入与链转移、MWD/CCD/序列、保留不饱和度、支化/凝胶、高黏反应器、急冷脱灰脱挥、循环毒物、门尼/混炼/硫化、牌号切换、部件耐久、客户线和最终工艺包验收。

## 唯一验证链

```bash
python scripts/run_ci.py
python skills/epdm/scripts/audit_epdm.py
python skills/poe/scripts/audit_p0.py --root .
python skills/poe/scripts/audit_p1.py --root .
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/verify_wheel_contents.py --wheel-dir wheelhouse
python scripts/verify_wheel_runtime.py --wheel-dir wheelhouse
```

软件测试通过不等于科学、工程、HSE、客户或工业批准；这些状态仍为 `NOT_EVALUATED`。唯一权威分支为 `main`。
