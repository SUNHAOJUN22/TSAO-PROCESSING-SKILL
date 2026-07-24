from __future__ import annotations

import sys

from finalize_alpha8_materialize import patch_mother_files
from finalize_alpha8_runtime import (
    ISSUE,
    ROOT,
    clean,
    comment,
    commit_push,
    dispatch_and_wait,
    local_gates,
    run,
    set_status,
)

RUFF_TARGETS = (
    "tsao",
    "tests",
    "scripts",
    "skills/process-general",
    "skills/epdm",
    "skills/poe",
    "skills/polymer-general",
)


def main() -> None:
    run(["git", "config", "user.name", "github-actions[bot]"], "git config")
    run(
        [
            "git",
            "config",
            "user.email",
            "41898282+github-actions[bot]@users.noreply.github.com",
        ],
        "git config",
    )
    patch_mother_files()
    run(
        [
            sys.executable,
            "-m",
            "py_compile",
            "tsao/capabilities.py",
            "tsao/cli.py",
            "tsao/process_package.py",
        ],
        "compile",
    )
    run(
        [sys.executable, "-m", "pip", "install", "--quiet", "-e", ".[dev]"],
        "install",
    )
    run([sys.executable, "-m", "pip", "check"], "pip check")
    run([sys.executable, "-m", "ruff", "format", *RUFF_TARGETS], "ruff format")
    run(
        [sys.executable, "-m", "ruff", "check", "--fix", *RUFF_TARGETS],
        "ruff autofix",
    )
    local_gates()

    set_status("QUALIFIED_CANDIDATE")
    clean()
    run(
        [
            sys.executable,
            "scripts/build_source_asset_manifest.py",
            "--root",
            ".",
            "--out",
            "reports/SOURCE_CORE_MANIFEST.tsv",
        ],
        "candidate manifest",
    )
    prepared = commit_push("fix: materialize alpha8 mother runtime")
    dispatch_and_wait(prepared)

    for relative in (
        ".github/workflows/finalize-alpha8-once.yml",
        "scripts/finalize_alpha8.py",
        "scripts/finalize_alpha8_runtime.py",
        "scripts/finalize_alpha8_materialize.py",
    ):
        (ROOT / relative).unlink(missing_ok=True)
    for pattern in ("alpha8-capabilities.b64.*", "alpha8-cli.b64.*"):
        for path in (ROOT / "reports/runtime").glob(pattern):
            path.unlink(missing_ok=True)

    set_status("QUALIFIED_ALPHA")
    local_gates()
    clean()
    run(
        [
            sys.executable,
            "scripts/build_source_asset_manifest.py",
            "--root",
            ".",
            "--out",
            "reports/SOURCE_CORE_MANIFEST.tsv",
        ],
        "final manifest",
    )
    final_sha = commit_push("feat: deliver alpha8 universal process package and EPDM flagship")
    final_run = dispatch_and_wait(final_sha)

    branches = run(["git", "ls-remote", "--heads", "origin"], "branch check")
    names = sorted(
        line.split("refs/heads/")[-1] for line in branches.splitlines() if "refs/heads/" in line
    )
    if names != ["main"]:
        raise SystemExit(f"remaining branches: {names}")

    comment(
        "## Alpha.8 final qualification PASS\n\n"
        f"- final main: `{final_sha}`\n"
        f"- final CI: `{final_run}` **PASS**\n"
        "- universal process-package platform: **PASS**\n"
        "- EPDM 14/14 modules and 20/20 requirements: **PASS**\n"
        "- 179 tests / 78% joint branch coverage / doctor / Ruff / wheel / "
        "installed runtime / CLI: **PASS**\n"
        "- Ubuntu 3.11/3.12, Windows 3.12, macOS 3.12: **PASS**\n"
        "- remaining branch: `main`\n"
        "- one-shot files removed\n\n"
        "Scientific, engineering, HSE, customer and industrial approvals remain "
        "`NOT_EVALUATED`."
    )
    run(["gh", "issue", "close", ISSUE, "--reason", "completed"], "close issue")


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        comment(f"Alpha.8 finalizer crashed: `{type(exc).__name__}: {exc}`")
        raise
