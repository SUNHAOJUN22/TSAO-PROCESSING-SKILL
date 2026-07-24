from __future__ import annotations

from typing import Any

from .kinetics import (
    EpdmKineticParameters,
    EpdmKineticState,
    active_site_fraction,
    architecture_metrics,
)
from .process import heat_removal_margin, recycle_poison_steady_state

_RECOGNIZED_DIENES = {"ENB", "DCPD", "VNB"}


def validate_epdm_case(case: object) -> dict[str, Any]:
    errors: list[str] = []
    holds: list[str] = []
    metrics: dict[str, Any] = {}
    if not isinstance(case, dict):
        return {
            "status": "FAIL",
            "pass": False,
            "errors": ["EPDM case root must be an object"],
            "holds": [],
            "metrics": {},
        }
    catalyst = case.get("catalyst")
    if not isinstance(catalyst, dict):
        errors.append("catalyst must be an object")
    else:
        family = catalyst.get("family")
        if not isinstance(family, str) or not family.strip():
            errors.append("catalyst.family is required")
        benchmark = catalyst.get("vanadium_benchmark")
        retirement = catalyst.get("benchmark_retirement")
        if benchmark is not True and not (
            isinstance(retirement, dict)
            and retirement.get("status") == "APPROVED"
            and retirement.get("approver")
        ):
            holds.append("vanadium industrial benchmark is missing or not formally retired")
        try:
            metrics["active_site_fraction"] = active_site_fraction(
                catalyst.get("total_metal_mol"), catalyst.get("active_site_mol")
            )
        except ValueError as exc:
            errors.append(str(exc))
        if not catalyst.get("active_site_evidence_ids"):
            holds.append("active-site concentration is not anchored to evidence")
    monomers = case.get("monomers")
    if not isinstance(monomers, dict):
        errors.append("monomers must be an object")
    else:
        diene = monomers.get("diene")
        if diene not in _RECOGNIZED_DIENES:
            holds.append("diene identity is outside the qualified ENB/DCPD/VNB reference set")
        for field in ("ethylene_mol_L", "propylene_mol_L", "diene_mol_L"):
            value = monomers.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                errors.append(f"monomers.{field} must be non-negative numeric")
        if monomers.get("diene_topology_measured") is not True:
            holds.append("diene topology or retained-unsaturation measurement is missing")
    kinetic = case.get("kinetics")
    if isinstance(catalyst, dict) and isinstance(monomers, dict) and isinstance(kinetic, dict):
        try:
            state = EpdmKineticState(
                monomers["ethylene_mol_L"],
                monomers["propylene_mol_L"],
                monomers["diene_mol_L"],
                catalyst["active_site_mol"]
                / max(float(case.get("reactor", {}).get("volume_L", 1.0)), 1e-30),
                float(case.get("impurities", {}).get("poison_mol_L", 0.0)),
            )
            parameters = EpdmKineticParameters(**kinetic["parameters"])
            metrics["architecture"] = architecture_metrics(
                state,
                parameters,
                secondary_diene_insertion_probability=kinetic.get(
                    "secondary_diene_insertion_probability", 0.0
                ),
                branch_efficiency=kinetic.get("branch_efficiency", 0.0),
                gel_critical_branch_index=kinetic.get("gel_critical_branch_index", 1.0),
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"invalid kinetic/architecture case: {exc}")
    else:
        errors.append("kinetics must be an object")
    reactor = case.get("reactor")
    if not isinstance(reactor, dict):
        errors.append("reactor must be an object")
    else:
        try:
            margin = heat_removal_margin(
                reactor.get("heat_generation_kW"), reactor.get("heat_removal_capacity_kW")
            )
            metrics["heat_removal_margin"] = margin
            if margin < 0:
                errors.append("reactor heat removal capacity is below heat generation")
            elif margin < 0.15:
                holds.append("reactor heat-removal margin is below the 15% reference Gate")
        except ValueError as exc:
            errors.append(str(exc))
        if reactor.get("phase_stable") is not True:
            holds.append("polymer-solution phase stability is not demonstrated")
        if reactor.get("mixing_qualified") is not True:
            holds.append("high-viscosity mixing is not qualified")
    recovery = case.get("recovery")
    if not isinstance(recovery, dict):
        errors.append("recovery must be an object")
    else:
        try:
            poison = recycle_poison_steady_state(
                recovery.get("fresh_poison_mol_h"),
                recovery.get("recycle_fraction"),
                recovery.get("purge_fraction"),
                recovery.get("guard_removal_fraction"),
            )
            metrics["steady_poison_mol_h"] = poison
            if poison > float(recovery.get("max_poison_mol_h")):
                errors.append("recycle poison steady state exceeds the declared limit")
        except (TypeError, ValueError) as exc:
            errors.append(f"invalid recovery/poison case: {exc}")
        if recovery.get("non_equilibrium_devolatilization") is not True:
            holds.append(
                "devolatilization is represented without a qualified non-equilibrium basis"
            )
    product_bridge = case.get("product_bridge")
    if not isinstance(product_bridge, dict):
        errors.append("product_bridge must be an object")
    else:
        for stage in ("raw_polymer", "fixed_compound", "cure", "part_durability", "customer_line"):
            record = product_bridge.get(stage)
            if (
                not isinstance(record, dict)
                or record.get("status") != "PASS"
                or not record.get("evidence_ids")
            ):
                holds.append(f"product bridge stage is not qualified: {stage}")
    status = "FAIL" if errors else "HOLD" if holds else "PASS"
    return {
        "status": status,
        "pass": status == "PASS",
        "errors": sorted(set(errors)),
        "holds": sorted(set(holds)),
        "metrics": metrics,
        "scientific_technical_approval": "NOT_EVALUATED",
        "engineering_design_approval": "NOT_EVALUATED",
        "customer_qualification": "NOT_EVALUATED",
    }
