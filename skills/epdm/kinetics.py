from __future__ import annotations

import math
from dataclasses import dataclass


def _finite(value: object, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


@dataclass(frozen=True)
class EpdmKineticParameters:
    kp_e_L_mol_s: float
    kp_p_L_mol_s: float
    kp_d_L_mol_s: float
    k_transfer_s: float
    k_deactivation_s: float
    k_poison_L_mol_s: float = 0.0

    def validated(self) -> EpdmKineticParameters:
        values = {name: _finite(value, name) for name, value in self.__dict__.items()}
        if min(values.values()) < 0:
            raise ValueError("kinetic parameters must be non-negative")
        return EpdmKineticParameters(**values)


@dataclass(frozen=True)
class EpdmKineticState:
    ethylene_mol_L: float
    propylene_mol_L: float
    diene_mol_L: float
    active_site_mol_L: float
    poison_mol_L: float = 0.0

    def validated(self) -> EpdmKineticState:
        values = {name: _finite(value, name) for name, value in self.__dict__.items()}
        if min(values.values()) < 0:
            raise ValueError("state concentrations must be non-negative")
        return EpdmKineticState(**values)


def active_site_fraction(total_metal_mol: float, active_site_mol: float) -> float:
    total = _finite(total_metal_mol, "total metal")
    active = _finite(active_site_mol, "active site")
    if total <= 0 or active < 0 or active > total:
        raise ValueError("active site must lie between zero and total metal")
    return active / total


def insertion_rates(state: EpdmKineticState, parameters: EpdmKineticParameters) -> dict[str, float]:
    state = state.validated()
    parameters = parameters.validated()
    site = state.active_site_mol_L
    rates = {
        "ethylene": parameters.kp_e_L_mol_s * state.ethylene_mol_L * site,
        "propylene": parameters.kp_p_L_mol_s * state.propylene_mol_L * site,
        "diene": parameters.kp_d_L_mol_s * state.diene_mol_L * site,
    }
    transfer = parameters.k_transfer_s * site
    deactivation = (
        parameters.k_deactivation_s + parameters.k_poison_L_mol_s * state.poison_mol_L
    ) * site
    rates["transfer"] = transfer
    rates["deactivation"] = deactivation
    return rates


def insertion_fractions(
    state: EpdmKineticState, parameters: EpdmKineticParameters
) -> dict[str, float]:
    rates = insertion_rates(state, parameters)
    total = rates["ethylene"] + rates["propylene"] + rates["diene"]
    if total <= 0:
        raise ValueError("total propagation rate must be positive")
    return {name: rates[name] / total for name in ("ethylene", "propylene", "diene")}


def architecture_metrics(
    state: EpdmKineticState,
    parameters: EpdmKineticParameters,
    *,
    secondary_diene_insertion_probability: float,
    branch_efficiency: float,
    gel_critical_branch_index: float,
) -> dict[str, float]:
    fractions = insertion_fractions(state, parameters)
    secondary = _finite(secondary_diene_insertion_probability, "secondary diene insertion")
    efficiency = _finite(branch_efficiency, "branch efficiency")
    critical = _finite(gel_critical_branch_index, "gel critical branch index")
    if not 0 <= secondary <= 1 or not 0 <= efficiency <= 1 or critical <= 0:
        raise ValueError("invalid branching parameters")
    rates = insertion_rates(state, parameters)
    propagation = rates["ethylene"] + rates["propylene"] + rates["diene"]
    termination = rates["transfer"] + rates["deactivation"]
    number_average_dp = propagation / max(termination, 1e-30)
    branch_index = fractions["diene"] * secondary * efficiency * number_average_dp
    gel_risk = min(1.0, branch_index / critical)
    retained_unsaturation = fractions["diene"] * (1.0 - secondary)
    average_e_run = 1.0 / max(1.0 - fractions["ethylene"], 1e-12)
    average_p_run = 1.0 / max(1.0 - fractions["propylene"], 1e-12)
    return {
        **{f"{name}_mole_fraction": value for name, value in fractions.items()},
        "number_average_degree_of_polymerization": number_average_dp,
        "retained_unsaturation_fraction": retained_unsaturation,
        "branch_index": branch_index,
        "gel_risk_index": gel_risk,
        "average_ethylene_run_length": average_e_run,
        "average_propylene_run_length": average_p_run,
    }
