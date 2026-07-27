from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts/compare_performance_v2.py"
OLD = '''PARITY_POLICIES = {
    "doctor_core_repository": "repository semantic contract: PASS and approval boundaries",
    "wheel_content_verification": "wheel semantic contract: identity and required-member tests",
    "poe_dynamic_response_10000_points": "analytical response and metric tolerance contract",
    "poe_finite_difference_jacobian_8x200": "analytical Jacobian tolerance contract",
}
'''
NEW = '''PARITY_POLICIES = {
    "doctor_core_repository": "repository semantic contract: PASS and approval boundaries",
    "skillpack_inventory": (
        "skillpack semantic contract: four Skills, 14/6/6 inventory, "
        "README assets and approval boundaries"
    ),
    "wheel_content_verification": "wheel semantic contract: identity and required-member tests",
    "poe_dynamic_response_10000_points": "analytical response and metric tolerance contract",
    "poe_finite_difference_jacobian_8x200": "analytical Jacobian tolerance contract",
}
'''


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if NEW in text:
        return 0
    if text.count(OLD) != 1:
        raise SystemExit("performance comparison parity-policy block changed unexpectedly")
    TARGET.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
