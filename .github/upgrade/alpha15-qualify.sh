#!/usr/bin/env bash
set -euo pipefail
mode="${1:?mode required}"
patch_path="${RUNNER_TEMP:-/tmp}/alpha15.patch"
cat .github/upgrade/alpha15.patch.gz.part-* | base64 --decode | gzip --decompress > "$patch_path"
echo "ab9740e422e238e3758964c2168cb62c8a3638380d7dc2ed95a82844b615b62a  $patch_path" | sha256sum --check --status
git apply --check "$patch_path"
git apply --whitespace=fix "$patch_path"
correction_path="${RUNNER_TEMP:-/tmp}/alpha15-ruff-correction.patch"
cat .github/upgrade/alpha15.correction.gz.part-* | base64 --decode | gzip --decompress > "$correction_path"
echo "c757de81d73858cf6d1cb0ae6bfbc3408cd69befd8bb3ee34b721c9738fc78eb  $correction_path" | sha256sum --check --status
git apply --check "$correction_path"
git apply --whitespace=fix "$correction_path"
performance_path="${RUNNER_TEMP:-/tmp}/alpha15-performance-correction.patch"
cat .github/upgrade/alpha15.performance.gz.part-* | base64 --decode | gzip --decompress > "$performance_path"
echo "67411bf94b5be73155e7c322979247d592cd2ac48f2e109e18a99fadf26c86a8  $performance_path" | sha256sum --check --status
git apply --check "$performance_path"
git apply --whitespace=fix "$performance_path"
python - <<'PY'
from pathlib import Path

path = Path("tsao/process_package.py")
text = path.read_text(encoding="utf-8")
old = '    stream_ids = _unique_ids(streams, "stream_id", "stream", errors)\n'
new = '    _unique_ids(streams, "stream_id", "stream", errors)\n'
if text.count(old) != 1:
    raise SystemExit("alpha15 lint closure target is missing or ambiguous")
with path.open("w", encoding="utf-8", newline="\n") as stream:
    stream.write(text.replace(old, new))
PY
python scripts/update_source_overlay.py --root . tsao/process_package.py
rm -rf .github/upgrade
rm -f .github/workflows/alpha15-pr-qualify-once.yml
git config user.name 'TSAO Qualification Bot'
git config user.email 'actions@users.noreply.github.com'
git add -A
git diff --cached --check
git commit -m 'Alpha15 qualified candidate'
python -m pip install --quiet -e .[dev]
python -m pip check
python -m tsao.cli doctor --root . --profile core
python -m pytest -q -p no:cacheprovider \
  skills/epdm/tests/test_epdm_phase_a0.py \
  skills/epdm/tests/test_epdm_phase_a1.py \
  skills/epdm/tests/test_epdm_phase_a2.py \
  skills/epdm/tests/test_epdm_phase_a3.py \
  skills/epdm/tests/test_epdm_phase_a4_integration.py \
  skills/process-general/tests/test_process_package_runtime.py \
  tests/test_alpha12_false_pass.py \
  tests/test_alpha13_numerical_correctness.py \
  tests/test_alpha14_wheel_contract.py \
  tests/test_alpha15_wheel_contract.py \
  tests/test_performance_v2_reports.py \
  tests/test_release_integrity_alpha6.py \
  tests/test_repository_contracts.py \
  tests/test_wheel_contract.py
python scripts/run_ci.py
python -m coverage erase
python -m coverage run --branch -m pytest -q -p no:cacheprovider skills/epdm/tests/test_epdm_phase_a4_integration.py
python -m coverage report --include='skills/epdm/numerical_integration.py' --fail-under=90 | tee "${RUNNER_TEMP:-/tmp}/alpha15-coverage.txt"
python -c "from pathlib import Path; Path('.coverage').unlink(missing_ok=True)"
rm -rf wheelhouse build dist *.egg-info
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/verify_wheel_contents.py --wheel-dir wheelhouse
python scripts/verify_wheel_runtime.py --wheel-dir wheelhouse
if [[ "${RUN_EXTENDED:-0}" == "1" ]]; then
  python scripts/benchmark_performance_v2.py --repeats 7 --wheel-dir wheelhouse --output reports/runtime/PERFORMANCE_RESULTS_V2.json
  python scripts/compare_performance_v2.py --baseline reports/PERFORMANCE_BASELINE_ALPHA10_EXTENDED.json --current reports/runtime/PERFORMANCE_RESULTS_V2.json --output reports/runtime/PERFORMANCE_COMPARISON_V2.json
  python scripts/export_source_snapshot.py --root . --out "${RUNNER_TEMP:-/tmp}/TSAO-PROCESSING-SKILL-source-alpha.15.zip"
  python - <<'INNERPY'
import zipfile
from pathlib import Path
import os
p=Path(os.environ.get('RUNNER_TEMP','/tmp'))/'TSAO-PROCESSING-SKILL-source-alpha.15.zip'
names=set(zipfile.ZipFile(p).namelist())
required=(
 'skills/epdm/executable_rhs.py',
 'skills/epdm/numerical_integration.py',
 'skills/epdm/schemas/integration-request-a15.schema.json',
 'skills/epdm/schemas/integration-result-a15.schema.json',
 'skills/epdm/tests/test_epdm_phase_a4_integration.py',
 'reports/EPDM_PHASE_A4_QUALIFICATION.json',
)
missing=[item for item in required if not any(name.endswith('/'+item) for name in names)]
if missing:
    raise SystemExit(f'source snapshot missing overlay files: {missing}')
INNERPY
fi
if [[ "$mode" == "promote" ]]; then
  wheel="$(find wheelhouse -maxdepth 1 -name '*.whl' -type f -print -quit)"
  sha256sum "$wheel" > "${RUNNER_TEMP:-/tmp}/alpha15-wheel.sha256"
  cp "$wheel" "${RUNNER_TEMP:-/tmp}/"
  git archive --format=zip --output="${RUNNER_TEMP:-/tmp}/alpha15-qualified-candidate.zip" HEAD
  git push --force origin HEAD:alpha15-qualification
fi
