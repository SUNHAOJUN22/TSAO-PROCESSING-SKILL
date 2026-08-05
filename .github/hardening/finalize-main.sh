#!/usr/bin/env bash
set -euo pipefail

cd "${GITHUB_WORKSPACE:?}"
export PYTHONUTF8=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

mapfile -t patch_parts < <(
  find .github/hardening -maxdepth 1 -type f \
    -name 'main-hardening.patch.gz.b64.part-*' | sort
)
test "${#patch_parts[@]}" -eq 13
patch_archive="${RUNNER_TEMP}/main-hardening.patch.gz"
cat "${patch_parts[@]}" | base64 --decode > "${patch_archive}"
echo "a4c9610d8217b374f965fda55c64b302587b724add097e3f9d7cfb7bcd0c554d  ${patch_archive}" \
  | sha256sum --check --strict

test -f .github/hardening/finalize-main.sh
rm "${patch_parts[@]}" \
  .github/hardening/finalize-main.sh \
  .github/workflows/main-only-hardening-finalize-once.yml
gunzip -c "${patch_archive}" > "${RUNNER_TEMP}/main-hardening.patch"
git apply --binary "${RUNNER_TEMP}/main-hardening.patch"

sed -i '/^import sys$/d' scripts/verify_dependency_lock.py

python -m pip install --quiet pip-tools==7.6.0 pip-audit==2.10.1
python -m piptools compile \
  --extra dev \
  --generate-hashes \
  --strip-extras \
  --resolver backtracking \
  --allow-unsafe \
  --output-file requirements.lock \
  pyproject.toml
python scripts/verify_dependency_lock.py requirements.lock \
  --pyproject pyproject.toml \
  --json-out reports/DEPENDENCY_LOCK_QUALIFICATION_2026-08-05.json
python -m pip_audit \
  --require-hashes \
  -r requirements.lock \
  --format json \
  --output reports/PIP_AUDIT_2026-08-05.json
python scripts/update_source_overlay.py --root . \
  requirements.lock \
  reports/DEPENDENCY_LOCK_QUALIFICATION_2026-08-05.json \
  reports/PIP_AUDIT_2026-08-05.json

venv="${RUNNER_TEMP}/tsao-main-hardening-venv"
python -m venv "${venv}"
# shellcheck disable=SC1091
source "${venv}/bin/activate"
python -m pip install --quiet --require-hashes -r requirements.lock
python -m pip install --quiet --no-deps --no-build-isolation -e .
python -m pip check
python -m tsao.cli doctor --root . --profile core

sha256sum README.md README.zh-CN.md docs/assets/readme/*.svg \
  > "${RUNNER_TEMP}/readme-visuals.before.sha256"
python scripts/generate_readme_assets.py
python scripts/generate_extended_readme_assets.py
python scripts/generate_decision_readme_assets.py
python scripts/generate_performance_readme_assets.py
python scripts/generate_uiux_readme_assets.py
python scripts/harden_readme_svg_accessibility.py
python scripts/verify_readme_visual_accessibility.py
python scripts/sync_readme_visuals.py --check
sha256sum README.md README.zh-CN.md docs/assets/readme/*.svg \
  > "${RUNNER_TEMP}/readme-visuals.after.sha256"
diff -u "${RUNNER_TEMP}/readme-visuals.before.sha256" \
  "${RUNNER_TEMP}/readme-visuals.after.sha256"

python scripts/run_ci.py
python -m pip wheel --quiet --no-deps --no-build-isolation . -w wheelhouse
python scripts/verify_wheel_contents.py --wheel-dir wheelhouse \
  > "${RUNNER_TEMP}/WHEEL_CONTENT_VERIFICATION.json"
python scripts/verify_wheel_runtime.py --wheel-dir wheelhouse \
  > "${RUNNER_TEMP}/WHEEL_RUNTIME_VERIFICATION.json"

snapshot="${RUNNER_TEMP}/TSAO-PROCESSING-SKILL-source-main-hardening.zip"
python scripts/export_source_snapshot.py --root . --out "${snapshot}" \
  > "${RUNNER_TEMP}/SOURCE_SNAPSHOT_VERIFICATION.json"
rm -rf "${RUNNER_TEMP}/source-extracted"
mkdir -p "${RUNNER_TEMP}/source-extracted"
python - <<'PY'
import os
import zipfile
from pathlib import Path

archive = Path(os.environ["RUNNER_TEMP"]) / "TSAO-PROCESSING-SKILL-source-main-hardening.zip"
target = Path(os.environ["RUNNER_TEMP"]) / "source-extracted"
with zipfile.ZipFile(archive) as stream:
    stream.extractall(target)
roots = [path for path in target.iterdir() if path.is_dir()]
if len(roots) != 1:
    raise SystemExit(f"expected one extracted root, found {len(roots)}")
(Path(os.environ["RUNNER_TEMP"]) / "source-root.txt").write_text(
    str(roots[0]), encoding="utf-8"
)
PY
source_root="$(cat "${RUNNER_TEMP}/source-root.txt")"
python -m tsao.cli doctor --root "${source_root}" --profile core

evidence_dir="${RUNNER_TEMP}/main-hardening-evidence"
mkdir -p "${evidence_dir}"
cp wheelhouse/*.whl "${evidence_dir}/"
cp "${snapshot}" "${evidence_dir}/"
cp "${RUNNER_TEMP}/WHEEL_CONTENT_VERIFICATION.json" "${evidence_dir}/"
cp "${RUNNER_TEMP}/WHEEL_RUNTIME_VERIFICATION.json" "${evidence_dir}/"
cp "${RUNNER_TEMP}/SOURCE_SNAPSHOT_VERIFICATION.json" "${evidence_dir}/"

rm -rf wheelhouse build dist .pytest_cache htmlcov .coverage .mypy_cache .ruff_cache
find . -maxdepth 1 -type d -name '*.egg-info' -exec rm -rf {} +
rm -f reports/runtime/*.json reports/runtime/*.tmp
python -m tsao.cli doctor --root . --profile core

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -A
python - <<'PY'
import subprocess

expected = {
    *{f".github/hardening/main-hardening.patch.gz.b64.part-{index:02d}" for index in range(13)},
    ".github/hardening/finalize-main.sh",
    ".github/workflows/ci.yml",
    ".github/workflows/main-only-hardening-finalize-once.yml",
    "README.md",
    "README.zh-CN.md",
    "docs/CAPABILITY_MATRIX.md",
    "docs/README_VISUAL_SYSTEM.md",
    "docs/SUPPLY_CHAIN_REPRODUCIBILITY.md",
    "docs/assets/readme/dependency-lock-supply-chain.svg",
    "docs/assets/readme/main-only-delivery-lifecycle.svg",
    "docs/assets/readme/source-snapshot-self-validation.svg",
    "manifest.yaml",
    "reports/DEPENDENCY_LOCK_QUALIFICATION_2026-08-05.json",
    "reports/PIP_AUDIT_2026-08-05.json",
    "reports/SOURCE_CORE_OVERLAY.tsv",
    "reports/SOURCE_SNAPSHOT_SELF_VALIDATION_2026-08-05.md",
    "requirements.lock",
    "scripts/generate_uiux_readme_assets.py",
    "scripts/sync_readme_visuals.py",
    "scripts/verify_dependency_lock.py",
    "scripts/verify_wheel_contents.py",
    "scripts/verify_wheel_runtime.py",
    "tests/test_alpha14_wheel_contract.py",
    "tests/test_dependency_lock.py",
    "tests/test_readme_assets.py",
    "tests/test_readme_visual_accessibility.py",
    "tests/test_release_convergence.py",
    "tests/test_release_integrity_alpha6.py",
    "tests/test_repository_contracts.py",
    "tests/test_skillpack_delivery.py",
    "tests/test_wheel_contract.py",
    "tsao/provenance.py",
    "tsao/skillpacks.py",
    "tsao/snapshot.py",
}
actual = set(
    subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).splitlines()
)
if actual != expected:
    raise SystemExit(f"unexpected staged paths: {sorted(actual ^ expected)}")
PY
git diff --cached --check
git commit -m "chore: finalize main-only supply-chain hardening"
git push origin HEAD:main
final_sha="$(git rev-parse HEAD)"

mapfile -t branches < <(
  git ls-remote --heads origin \
    | awk '{sub("refs/heads/", "", $2); print $2}' \
    | grep -v '^main$' || true
)
for branch in "${branches[@]}"; do
  git push origin --delete "${branch}"
done
remaining="$(
  git ls-remote --heads origin \
    | awk '{sub("refs/heads/", "", $2); print $2}' \
    | grep -v '^main$' || true
)"
if [[ -n "${remaining}" ]]; then
  printf 'non-main branches remain:\n%s\n' "${remaining}" >&2
  exit 1
fi

lock_sha="$(sha256sum requirements.lock | awk '{print $1}')"
comment="${RUNNER_TEMP}/main-hardening-comment.md"
cat > "${comment}" <<EOF
Main-only hardening completed in commit \`${final_sha}\`.

- exact Python 3.11 dependency lock: \`${lock_sha}\`;
- lock structure and SHA-256 policy: PASS;
- pip-audit vulnerability gate: PASS;
- full repository qualification, 21-figure visual determinism, Wheel content/runtime and extracted source snapshot: PASS;
- all non-\`main\` remote branches deleted;
- scientific, engineering, HSE, customer and industrial approvals remain \`NOT_EVALUATED\`.
EOF
for issue in 67 68; do
  gh issue comment "${issue}" --repo "${GITHUB_REPOSITORY}" --body-file "${comment}"
  gh issue close "${issue}" --repo "${GITHUB_REPOSITORY}" --reason completed
done

printf 'FINAL_SHA=%s\nLOCK_SHA=%s\n' "${final_sha}" "${lock_sha}" \
  | tee "${evidence_dir}/FINALIZATION_RESULT.txt"
