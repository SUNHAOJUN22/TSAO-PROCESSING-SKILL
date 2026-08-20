from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "skills" / "poe" / "material_balance.py"
MARKER = "def check_component_rows(rows: Sequence[Mapping[str, object]]) -> dict[str, Any]:"

REPLACEMENT = dedent(
    r'''
    def check_component_rows(rows: Sequence[Mapping[str, object]]) -> dict[str, Any]:
        """Evaluate component rows from the strict CSV adapter.

        Every row declares one basis, amount unit, time unit, all balance terms,
        absolute/relative tolerance, and reference scale. All rows must share one
        basis, but each row may use a different compatible representation unit.
        """

        if not rows:
            raise MaterialBalanceContractError("balance table is empty")
        seen: set[str] = set()
        declared_basis: str | None = None
        component_results: list[ComponentBalance] = []
        for index, row in enumerate(rows, start=2):
            component_raw = row.get("component")
            if not isinstance(component_raw, str) or not component_raw.strip():
                raise MaterialBalanceContractError(f"row {index}: component is required")
            component = component_raw.strip()
            if component in seen:
                raise MaterialBalanceContractError(f"row {index}: duplicate component {component}")
            seen.add(component)

            basis_raw = row.get("quantity_basis")
            if basis_raw not in _ALLOWED_BASES:
                raise MaterialBalanceContractError(
                    f"row {index}: quantity_basis must be mass or molar"
                )
            basis = str(basis_raw)
            if declared_basis is None:
                declared_basis = basis
            elif basis != declared_basis:
                raise MaterialBalanceContractError(
                    f"row {index}: mixed mass/molar basis is not allowed"
                )

            amount_unit = row.get("quantity_unit")
            time_unit = row.get("time_unit")
            if not isinstance(amount_unit, str) or not amount_unit.strip():
                raise MaterialBalanceContractError(f"row {index}: quantity_unit is required")
            if not isinstance(time_unit, str) or not time_unit.strip():
                raise MaterialBalanceContractError(f"row {index}: time_unit is required")
            unit = f"{amount_unit.strip()}/{time_unit.strip()}"
            factor = _unit_factor(basis, unit, f"row {index}")

            def term(name: str, *, non_negative: bool) -> float:
                value = _finite_real(
                    row.get(name), f"row {index} {name}", allow_string=True
                )
                if non_negative and value < 0:
                    raise MaterialBalanceContractError(
                        f"row {index} {name} must be non-negative"
                    )
                converted = value * factor
                if not math.isfinite(converted):
                    raise MaterialBalanceContractError(
                        f"row {index} {name} conversion is non-finite"
                    )
                return converted

            incoming = term("in", non_negative=True)
            outgoing = term("out", non_negative=True)
            generation = term("generation", non_negative=True)
            consumption = term("consumption", non_negative=True)
            accumulation = term("accumulation", non_negative=False)
            absolute_tolerance = term("absolute_tolerance", non_negative=True)
            relative_tolerance = _finite_real(
                row.get("relative_tolerance"),
                f"row {index} relative_tolerance",
                allow_string=True,
            )
            if relative_tolerance < 0 or relative_tolerance > 1:
                raise MaterialBalanceContractError(
                    f"row {index}: relative_tolerance must be in [0, 1]"
                )
            reference_scale = term("reference_scale", non_negative=True)
            if reference_scale <= 0:
                raise MaterialBalanceContractError(
                    f"row {index}: reference_scale must be positive"
                )

            residual = accumulation - (
                incoming - outgoing + generation - consumption
            )
            if not math.isfinite(residual):
                raise MaterialBalanceContractError(
                    f"row {index}: residual is non-finite"
                )
            allowed = absolute_tolerance + relative_tolerance * reference_scale
            if not math.isfinite(allowed):
                raise MaterialBalanceContractError(
                    f"row {index}: allowed residual is non-finite"
                )
            component_results.append(
                ComponentBalance(
                    component=component,
                    basis=basis,
                    canonical_unit=_CANONICAL_UNIT[basis],
                    incoming=incoming,
                    outgoing=outgoing,
                    generation=generation,
                    consumption=consumption,
                    accumulation=accumulation,
                    residual=residual,
                    absolute_residual=abs(residual),
                    absolute_tolerance=absolute_tolerance,
                    relative_tolerance=relative_tolerance,
                    reference_scale=reference_scale,
                    allowed_residual=allowed,
                    component_pass=abs(residual) <= allowed,
                )
            )

        if declared_basis is None:  # guarded by the non-empty rows check
            raise MaterialBalanceContractError("balance basis is missing")

        total_in = math.fsum(item.incoming for item in component_results)
        total_out = math.fsum(item.outgoing for item in component_results)
        total_generation = math.fsum(item.generation for item in component_results)
        total_consumption = math.fsum(item.consumption for item in component_results)
        total_accumulation = math.fsum(item.accumulation for item in component_results)
        total_residual = total_accumulation - (
            total_in - total_out + total_generation - total_consumption
        )
        total_allowed = math.fsum(
            item.absolute_tolerance for item in component_results
        ) + math.fsum(
            item.relative_tolerance * item.reference_scale
            for item in component_results
        )
        total_pass = abs(total_residual) <= total_allowed
        failed_components = tuple(
            item.component for item in component_results if not item.component_pass
        )
        component_pass = not failed_components
        passed = component_pass and total_pass
        reason_codes: list[str] = []
        if not component_pass:
            reason_codes.append("COMPONENT_BALANCE_NOT_CLOSED")
        if not total_pass:
            reason_codes.append("TOTAL_BALANCE_NOT_CLOSED")
        if passed:
            reason_codes.append("BALANCE_CLOSED")

        payload: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "status": "PASS" if passed else "FAIL",
            "pass": passed,
            "basis": declared_basis,
            "canonical_unit": _CANONICAL_UNIT[declared_basis],
            "errors": [],
            "reason_codes": reason_codes,
            "failed_components": list(failed_components),
            "components": [asdict(item) for item in component_results],
            "component_balances_pass": component_pass,
            "total_balance_pass": total_pass,
            "total": {
                "basis": declared_basis,
                "canonical_unit": _CANONICAL_UNIT[declared_basis],
                "incoming": total_in,
                "outgoing": total_out,
                "generation": total_generation,
                "consumption": total_consumption,
                "accumulation": total_accumulation,
                "residual": total_residual,
                "absolute_residual": abs(total_residual),
                "allowed_residual": total_allowed,
                "total_pass": total_pass,
            },
        }
        json.dumps(payload, allow_nan=False)
        return payload
    '''
).lstrip()


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    marker_index = text.find(MARKER)
    if marker_index < 0:
        raise RuntimeError(f"material-balance function marker is missing: {MARKER}")
    prefix = text[:marker_index]
    if "import json\n" not in prefix:
        prefix = prefix.replace("import math\n", "import json\nimport math\n", 1)
    repaired = prefix.rstrip() + "\n\n\n" + REPLACEMENT.rstrip() + "\n"
    compile(repaired, TARGET.as_posix(), "exec")
    TARGET.write_text(repaired, encoding="utf-8", newline="\n")
    print({"repaired": TARGET.relative_to(ROOT).as_posix()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
