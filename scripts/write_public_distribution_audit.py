from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from tsao.distribution_policy import audit_public_distribution


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="reports/runtime/PUBLIC_DISTRIBUTION_AUDIT.json")
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT"))
    args = parser.parse_args()

    root = Path(args.root).resolve()
    audit = audit_public_distribution(root)
    payload = audit.as_dict()
    payload["allowed"] = audit.status == "PASS"
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(f"allowed={'true' if payload['allowed'] else 'false'}\n")
            handle.write(f"status={audit.status}\n")
            handle.write(f"audit_path={args.output}\n")

    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
