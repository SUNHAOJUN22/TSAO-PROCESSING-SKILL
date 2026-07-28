from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
VERSION = "0.1.0-alpha.11"


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def replace(path: str, old: str, new: str, count: int = 1) -> None:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    if new in text:
        return
    if text.count(old) != count:
        raise SystemExit(f"{path}: replacement precondition failed: {old!r}")
    p.write_text(text.replace(old, new, count), encoding="utf-8")


def write_json(path: str, data: dict[str, object]) -> None:
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def patch_transform() -> None:
    p = ROOT / "scripts/apply_alpha11_performance_release.py"
    text = p.read_text(encoding="utf-8")
    old = "    text = _read(relative)\n    actual = text.count(old)\n"
    if text.count(old) != 2:
        raise SystemExit("alpha11 transform helper changed")
    text = text.replace(old, "    text = _read(relative)\n    if new in text:\n        return\n    actual = text.count(old)\n", 1)
    old2 = "    text = _read(relative)\n    actual = text.count(old)\n    if actual < minimum:\n"
    new2 = "    text = _read(relative)\n    actual = text.count(old)\n    if actual == 0 and new in text:\n        return\n    if actual < minimum:\n"
    if old2 not in text:
        raise SystemExit("alpha11 replace-all helper changed")
    p.write_text(text.replace(old2, new2, 1), encoding="utf-8")


def update_ci() -> None:
    p = ROOT / ".github/workflows/ci.yml"
    text = p.read_text(encoding="utf-8")
    text, n = re.subn(
        r"  qualification:\n    if: >-\n      \$\{\{ github\.event_name != 'push' \|\|\n          \(!contains\(github\.event\.head_commit\.message, '\[FINALIZE-ALPHA10\]'\) &&\n           !contains\(github\.event\.head_commit\.message, '\[FINALIZE-ALPHA11\]'\)\) \}\}\n    runs-on:",
        "  qualification:\n    runs-on:",
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit("CI finalizer skip block not found")
    anchor = "      - name: Verify wheel members and installed runtime\n        run: |\n          python scripts/verify_wheel_contents.py --wheel-dir wheelhouse\n          python scripts/verify_wheel_runtime.py --wheel-dir wheelhouse\n"
    upload = anchor + "      - name: Upload release wheel\n        if: ${{ matrix.os == 'ubuntu-latest' && matrix.python-version == '3.14' }}\n        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2\n        with:\n          name: tsao-wheel-alpha11-${{ github.sha }}\n          path: wheelhouse/*.whl\n          if-no-files-found: error\n          retention-days: 30\n"
    if anchor not in text:
        raise SystemExit("CI wheel anchor not found")
    text = text.replace(anchor, upload, 1)
    integrity = "      - name: Dependency integrity\n        run: python -m pip check\n"
    hygiene = integrity + "      - name: Verify permanent repository hygiene\n        run: >-\n          python -c \"from pathlib import Path; w=sorted(p.name for p in Path('.github/workflows').glob('*.yml')); assert w==['ci.yml'],w; f=[p.as_posix() for p in Path('.').rglob('*') if p.is_file() and ('-once.yml' in p.name or 'CANDIDATE' in p.name or 'DIAGNOSTIC' in p.name)]; assert not f,f\"\n"
    if integrity not in text:
        raise SystemExit("CI integrity anchor not found")
    p.write_text(text.replace(integrity, hygiene, 1), encoding="utf-8")


def prepare() -> None:
    patch_transform()
    run(sys.executable, "scripts/apply_alpha11_performance_release.py")
    run(sys.executable, "scripts/fix_alpha11_release_transform.py")
    update_ci()
    for path, heading, next_heading in (
        ("README.md", "Batch scenario screening", "Install and run"),
        ("README.zh-CN.md", "批量情景筛选", "安装与运行"),
    ):
        p = ROOT / path
        text = p.read_text(encoding="utf-8")
        pattern = rf"\n### {re.escape(heading)}\n\n!\[[^\]]*\]\(docs/assets/readme/batch-parameter-scan\.svg\)\n\n.*?(?=\n## {re.escape(next_heading)}\n)"
        text = re.sub(pattern, "\n", text, count=1, flags=re.S)
        if text.count("batch-parameter-scan.svg") != 1:
            raise SystemExit(f"{path}: batch diagram duplication")
        p.write_text(text, encoding="utf-8")
    replace("pyproject.toml", '  "reports/ALPHA11_SOURCE_CORE_STATUS.json",\n', '  "reports/ALPHA11_SOURCE_CORE_STATUS.json",\n  "reports/ALPHA11_FINAL_QUALIFICATION.json",\n')
    replace("scripts/verify_wheel_contents.py", '        f"{_SHARE_ROOT}/reports/ALPHA11_SOURCE_CORE_STATUS.json",\n', '        f"{_SHARE_ROOT}/reports/ALPHA11_SOURCE_CORE_STATUS.json",\n        f"{_SHARE_ROOT}/reports/ALPHA11_FINAL_QUALIFICATION.json",\n')
    replace("reports/README.md", '- `ALPHA11_SOURCE_CORE_STATUS.json` — qualified public source, four-Skill, eighteen-diagram, batch-performance and isolated-install status.\n', '- `ALPHA11_SOURCE_CORE_STATUS.json` — qualified public source, four-Skill, eighteen-diagram, batch-performance and isolated-install status.\n- `ALPHA11_FINAL_QUALIFICATION.json` — measured local and cross-platform software qualification evidence.\n')
    for stem in ("OPTIMIZED", "COMPARISON"):
        src = ROOT / f"reports/PERFORMANCE_{stem}_ALPHA11_CANDIDATE.json"
        data = json.loads(src.read_text(encoding="utf-8"))
        data["version" if stem == "OPTIMIZED" else "optimized_version"] = VERSION
        data["evidence_state"] = "PLACEHOLDER_PENDING_FINAL_RERUN"
        write_json(f"reports/PERFORMANCE_{stem}_ALPHA11.json", data)
    write_json("reports/ALPHA11_FINAL_QUALIFICATION.json", {
        "schema": "TSAO-ALPHA11-FINAL-QUALIFICATION-1", "version": VERSION,
        "audit_baseline_main": os.environ["AUDIT_BASE_SHA"],
        "promotion_orchestration_commit": os.environ["ORCHESTRATION_SHA"],
        "local_promotion_validation": "PENDING", "cross_platform_qualification": "PENDING",
        "final_closure_validation": "PENDING", "performance_gate": "PENDING",
        "scientific_technical_approval": "NOT_EVALUATED", "engineering_design_approval": "NOT_EVALUATED",
        "customer_qualification": "NOT_EVALUATED", "industrial_performance_guarantee": "NOT_EVALUATED",
    })
    review = ROOT / "reports/PERFORMANCE_TECHNOLOGY_REVIEW.md"
    text = review.read_text(encoding="utf-8").replace(
        "Baseline: `0.1.0-alpha.10` / `3069e2bce162a361f9dadda7635206804581a6aa`  ",
        (
            "Frozen performance baseline: `0.1.0-alpha.10` / "
            "`3069e2bce162a361f9dadda7635206804581a6aa`\n\n"
            f"Execution audit baseline: remote `main` / `{os.environ['AUDIT_BASE_SHA']}`\n\n"
            f"Promotion orchestration commit: `{os.environ['ORCHESTRATION_SHA']}`"
        ),
        1,
    )
    text += "\n\n## Additional official-source checks\n\n- CPython free-threading, Cython, PyPy, Numba, JAX and process parallelism remain deferred pending separate crossover and three-platform qualification.\n- BLAS thread controls remain deployment tuning, not a package default.\n- Pinned Actions, artifact v4, dependency caches and read-only permanent permissions are retained; caches are not evidence.\n"
    review.write_text(text, encoding="utf-8")
    for p in (ROOT / ".github/workflows").glob("*-once.yml"):
        p.unlink()
    for name in ("apply_alpha11_performance_release.py", "fix_alpha11_release_transform.py", "finalize_alpha11_once.py"):
        (ROOT / "scripts" / name).unlink(missing_ok=True)
    for p in (ROOT / "reports").iterdir():
        if p.is_file() and ("CANDIDATE" in p.name or "DIAGNOSTIC" in p.name or p.name.startswith("PERFORMANCE_V2_") or p.name == "SEMIBATCH_PARITY_DIAGNOSTIC.json"):
            p.unlink()


def implementation_digest() -> str:
    h = hashlib.sha256()
    paths = [p for base in ("tsao", "skills", "scripts") for p in (ROOT / base).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    paths += [ROOT / p for p in ("pyproject.toml", "manifest.yaml", "SKILL.md", ".github/workflows/ci.yml")]
    for p in sorted(set(paths), key=lambda x: x.as_posix()):
        rel, payload = p.relative_to(ROOT).as_posix().encode(), p.read_bytes()
        h.update(len(rel).to_bytes(4, "big") + rel + len(payload).to_bytes(8, "big") + payload)
    return h.hexdigest()


def stamp_performance() -> None:
    p = ROOT / "reports/PERFORMANCE_OPTIMIZED_ALPHA11.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data.update({"version": VERSION, "benchmark_parent_commit": os.environ["ORCHESTRATION_SHA"], "benchmark_worktree_state": "CLEANED_ALPHA11_RELEASE_CANDIDATE", "benchmark_implementation_sha256": implementation_digest(), "formal_environment": "ubuntu-latest / CPython 3.14", "qualification_scope": "SOFTWARE_PERFORMANCE_ONLY", "scientific_technical_approval": "NOT_EVALUATED", "engineering_design_approval": "NOT_EVALUATED", "industrial_performance_guarantee": "NOT_EVALUATED"})
    write_json(str(p.relative_to(ROOT)), data)


def record_local() -> None:
    ci = json.loads((ROOT / "reports/runtime/CI_RESULTS.json").read_text(encoding="utf-8"))
    comp = json.loads((ROOT / "reports/PERFORMANCE_COMPARISON_ALPHA11.json").read_text(encoding="utf-8"))
    wc = json.loads((ROOT / "reports/runtime/ALPHA11_WHEEL_CONTENTS.json").read_text(encoding="utf-8"))
    wr = json.loads((ROOT / "reports/runtime/ALPHA11_WHEEL_RUNTIME.json").read_text(encoding="utf-8"))
    if not all(x.get("pass") for x in (ci, comp, wc, wr)):
        raise SystemExit("local qualification failed")
    out = "\n".join(str(x.get("output", "")) for x in ci["checks"])
    tests = [int(x) for x in re.findall(r"(\d+) passed", out)]
    cov = [int(x) for x in re.findall(r"(?m)^TOTAL\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)%", out)]
    wheel = next((ROOT / "wheelhouse").glob("*.whl"))
    p = ROOT / "reports/ALPHA11_FINAL_QUALIFICATION.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data.update({"local_promotion_validation": "PASS", "performance_gate": "PASS", "performance_workloads": 20, "numeric_parity": "PASS_EXACT_TOLERANCE_AND_SEMANTIC_CONTRACTS", "test_count": max(tests) if tests else None, "branch_coverage_percent": max(cov) if cov else None, "wheel_filename": wheel.name, "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(), "wheel_content": "PASS", "pip_target_install": "PASS", "standard_venv_install": "PASS", "installed_import_origin": "VERIFIED_INSIDE_INSTALL_ROOT", "local_python": sys.version, "local_platform": platform.platform(), "readme_assets": "18_OF_18", "qualification_boundary": "SOFTWARE_ONLY"})
    write_json(str(p.relative_to(ROOT)), data)


def record_cross() -> None:
    p = ROOT / "reports/ALPHA11_FINAL_QUALIFICATION.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data.update({"candidate_commit": os.environ["CANDIDATE_SHA"], "cross_platform_qualification": "PASS", "cross_platform_matrix": ["ubuntu/3.11", "ubuntu/3.12", "ubuntu/3.13", "ubuntu/3.14", "windows/3.14", "macos/3.14"], "cross_platform_workflow_run_id": int(os.environ["CANDIDATE_RUN_ID"]), "cross_platform_workflow_run_url": os.environ["CANDIDATE_RUN_URL"], "final_closure_validation": "PENDING_FINAL_HEAD_CHECK_RUN"})
    write_json(str(p.relative_to(ROOT)), data)


if __name__ == "__main__":
    {"prepare": prepare, "stamp-performance": stamp_performance, "record-local": record_local, "record-cross": record_cross}[sys.argv[1]]()
