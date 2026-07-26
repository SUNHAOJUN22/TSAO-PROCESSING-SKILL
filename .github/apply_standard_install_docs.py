from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected text not found in {path}: {old}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def main() -> int:
    replace_once(
        "README.md",
        "2. **installation gate:** performs a real `pip install --target`, imports only from that target, resolves the installed Skillpack root, audits both installed READMEs and runs known-solution universal/EPDM/POE checks.",
        "2. **installation gate:** verifies both `pip install --target` and a standard virtual-environment installation, resolves the Skillpack root from each installation scheme, audits both installed READMEs and runs known-solution universal/EPDM/POE checks.",
    )
    replace_once(
        "README.zh-CN.md",
        "2. **安装门：**真实执行 `pip install --target`，只从安装目录导入代码，解析安装态 Skill 根，审计两份安装态 README，并运行通用工艺包、EPDM 和 POE 已知解检查。",
        "2. **安装门：**同时验证 `pip install --target` 与标准虚拟环境安装，分别解析对应安装 scheme 下的 Skill 根，审计两份安装态 README，并运行通用工艺包、EPDM 和 POE 已知解检查。",
    )
    replace_once(
        "CHANGELOG.md",
        "- Replaced the former Wheel zipimport smoke test with a real `pip install --target` installation test.",
        "- Replaced the former Wheel zipimport smoke test with independent `pip install --target` and standard virtual-environment installation tests.",
    )
    replace_once(
        "reports/FINAL_AUDIT_REPORT.md",
        "2. `verify_wheel_runtime.py` performs a real `pip install --target`, imports only from the installed target, resolves the installed Skillpack root, audits installed README links, validates the four-Skill inventory and runs universal, EPDM and POE known-solution checks.",
        "2. `verify_wheel_runtime.py` independently verifies `pip install --target` and a standard virtual-environment installation, resolves the correct data root for both installation schemes, audits installed README links, validates the four-Skill inventory and runs universal, EPDM and POE known-solution checks.",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
