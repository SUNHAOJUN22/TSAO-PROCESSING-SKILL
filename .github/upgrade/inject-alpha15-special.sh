#!/usr/bin/env bash
set -euo pipefail
python - <<'PY'
from pathlib import Path

path = Path('.github/upgrade/alpha15-qualify.sh')
text = path.read_text(encoding='utf-8')
marker = '''git apply --check "$governance_path"
git apply --whitespace=fix "$governance_path"
rm -rf .github/upgrade
'''
insertion = '''git apply --check "$governance_path"
git apply --whitespace=fix "$governance_path"
special_path="${RUNNER_TEMP:-/tmp}/alpha15-special-path-closure.patch"
cat .github/upgrade/alpha15.special.gz.part-* | base64 --decode | gzip --decompress > "$special_path"
echo "b0f518e94348011d96e308005dde232ecc2d3b5ae973e1194377331669916e8a  $special_path" | sha256sum --check --status
git apply --check "$special_path"
git apply --whitespace=fix "$special_path"
rm -rf .github/upgrade
'''
if text.count(marker) != 1:
    raise SystemExit('alpha15 special closure injection target is missing or ambiguous')
path.write_text(text.replace(marker, insertion), encoding='utf-8', newline='\n')
PY
