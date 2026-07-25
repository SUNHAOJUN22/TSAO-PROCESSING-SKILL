from __future__ import annotations

import math
from dataclasses import dataclass

GAS_CONSTANT_J_MOL_K = 8.31446261815324


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


def _positive_temperature(value: object, label: str) -> float:
    temperature = _finite(value, label)
    if temperature <= 0:
        raise ValueError(f"{label} must be positive")
    return temperature


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
class EpdmActivationEnergies:
    kp_e_J_mol: float
    kp_p_J_mol: float
    kp_d_J_mol: float
    transfer_J_mol: float
    deactivation_J_mol: float
    poison_J_mol: float = 0.0

    def validated(self) -> EpdmActivationEnergies:
        values = {name: _finite(value, name) for name, value in self.__dict__.items()}
        if min(values.values()) < 0:
            raise ValueError("activation energies must be non-negative")
        return EpdmActivationEnergies(**values)


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


def arrhenius_rate_constant(
    reference_rate: float,
    activation_energy_J_mol: float,
    temperature_K: float,
    reference_temperature_K: float = 298.15,
) -> float:
    """Scale a reference rate constant without changing its declared units."""
    rate = _finite(reference_rate, "reference rate")
    activation = _finite(activation_energy_J_mol, "activation energy")
    temperature = _positive_temperature(temperature_K, "temperature")
    reference_temperature = _positive_temperature(
        reference_temperature_K, "reference temperature"
    )
    if rate < 0 or activation < 0:
        raise ValueError("reference rate and activation energy must be non-negative")
    exponent = -(activation / GAS_CONSTANT_J_MOL_K) * (
        1.0 / temperature - 1.0 / reference_temperature
    )
    try:
        return rate * math.exp(exponent)
    except OverflowError as exc:
        raise ValueError("Arrhenius scaling overflowed; check temperatures and energy units") from exc


def temperature_adjusted_parameters(
    parameters: EpdmKineticParameters,
    activation_energies: EpdmActivationEnergies,
    temperature_K: float,
    reference_temperature_K: float = 298.15,
) -> EpdmKineticParameters:
    parameters = parameters.validated()
    activation_energies = activation_energies.validated()
    fields = (
        ("kp_e_L_mol_s", "kp_e_J_mol"),
        ("kp_p_L_mol_s", "kp_p_J_mol"),
        ("kp_d_L_mol_s", "kp_d_J_mol"),
        ("k_transfer_s", "transfer_J_mol"),
        ("k_deactivation_s", "deactivation_J_mol"),
        ("k_poison_L_mol_s", "poison_J_mol"),
    )
    adjusted = {
        rate_name: arrhenius_rate_constant(
            getattr(parameters, rate_name),
            getattr(activation_energies, energy_name),
            temperature_K,
            reference_temperature_K,
        )
        for rate_name, energy_name in fields
    }
    return EpdmKineticParameters(**adjusted)


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


def pseudo_first_order_conversions(
    state: EpdmKineticState,
    parameters: EpdmKineticParameters,
    residence_time_s: float,
) -> dict[str, float]:
    """Constant-active-site screening model for rapid scenario ranking."""
    state = state.validated()
    parameters = parameters.validated()
    residence = _finite(residence_time_s, "residence time")
    if residence < 0:
        raise ValueError("residence time must be non-negative")
    site = state.active_site_mol_L
    return {
        "ethylene": 1.0 - math.exp(-parameters.kp_e_L_mol_s * site * residence),
        "propylene": 1.0 - math.exp(-parameters.kp_p_L_mol_s * site * residence),
        "diene": 1.0 - math.exp(-parameters.kp_d_L_mol_s * site * residence),
    }


def chain_moment_reference(
    state: EpdmKineticState,
    parameters: EpdmKineticParameters,
    *,
    site_activity_cv: float = 0.0,
) -> dict[str, float]:
    """Reference chain moments; not a substitute for a fitted population balance."""
    variability = _finite(site_activity_cv, "site activity coefficient of variation")
    if variability < 0:
        raise ValueError("site activity coefficient of variation must be non-negative")
    rates = insertion_rates(state, parameters)
    propagation = sum(rates[name] for name in ("ethylene", "propylene", "diene"))
    chain_loss = rates["transfer"] + rates["deactivation"]
    if propagation <= 0:
        raise ValueError("propagation rate must be positive")
    dp_n = propagation / max(chain_loss, 1e-30)
    dispersity = 2.0 + variability**2
    return {
        "number_average_degree_of_polymerization": dp_n,
        "weight_average_degree_of_polymerization": dp_n * dispersity,
        "reference_dispersity_index": dispersity,
        "chain_birth_rate_mol_L_s": chain_loss,
    }


def three_level_kinetic_suite(
    state: EpdmKineticState,
    parameters: EpdmKineticParameters,
    activation_energies: EpdmActivationEnergies,
    *,
    temperature_K: float,
    residence_time_s: float,
    site_family_fractions: tuple[float, ...] = (1.0,),
    site_activity_multipliers: tuple[float, ...] = (1.0,),
) -> dict[str, object]:
    """Return screening, engineering and heterogeneous-site reference layers."""
    state = state.validated()
    parameters = parameters.validated()
    activation_energies = activation_energies.validated()
    if len(site_family_fractions) != len(site_activity_multipliers):
        raise ValueError("site family fractions and multipliers must have equal length")
    if not site_family_fractions:
        raise ValueError("at least one site family is required")
    fractions = tuple(_finite(value, "site family fraction") for value in site_family_fractions)
    multipliers = tuple(
        _finite(value, "site activity multiplier") for value in site_activity_multipliers
    )
    if min(fractions) < 0 or min(multipliers) < 0 or not math.isclose(
        sum(fractions), 1.0, rel_tol=1e-9, abs_tol=1e-12
    ):
        raise ValueError("site fractions must be non-negative and sum to one")

    adjusted = temperature_adjusted_parameters(
        parameters, activation_energies, temperature_K
    )
    simple = {
        "rates_mol_L_s": insertion_rates(state, parameters),
        "fractions": insertion_fractions(state, parameters),
    }
    engineering = {
        "temperature_K": _positive_temperature(temperature_K, "temperature"),
        "rates_mol_L_s": insertion_rates(state, adjusted),
        "conversions": pseudo_first_order_conversions(
            state, adjusted, residence_time_s
        ),
    }

    family_records: list[dict[str, object]] = []
    weighted_rates = {name: 0.0 for name in ("ethylene", "propylene", "diene")}
    multiplier_mean = sum(
        weight * multiplier
        for weight, multiplier in zip(fractions, multipliers, strict=True)
    )
    multiplier_variance = sum(
        weight * (multiplier - multiplier_mean) ** 2
        for weight, multiplier in zip(fractions, multipliers, strict=True)
    )
    for index, (weight, multiplier) in enumerate(
        zip(fractions, multipliers, strict=True), start=1
    ):
        family_parameters = EpdmKineticParameters(
            adjusted.kp_e_L_mol_s * multiplier,
            adjusted.kp_p_L_mol_s * multiplier,
            adjusted.kp_d_L_mol_s * multiplier,
            adjusted.k_transfer_s,
            adjusted.k_deactivation_s,
            adjusted.k_poison_L_mol_s,
        )
        family_rates = insertion_rates(state, family_parameters)
        for name in weighted_rates:
            weighted_rates[name] += weight * family_rates[name]
        family_records.append(
            {
                "family": index,
                "fraction": weight,
                "activity_multiplier": multiplier,
                "rates_mol_L_s": family_rates,
            }
        )
    site_cv = math.sqrt(multiplier_variance) / max(multiplier_mean, 1e-30)
    detailed = {
        "site_families": family_records,
        "weighted_propagation_rates_mol_L_s": weighted_rates,
        "site_activity_cv": site_cv,
        "chain_moments": chain_moment_reference(
            state, adjusted, site_activity_cv=site_cv
        ),
    }
    return {
        "status": "CALCULATED_REFERENCE_ONLY",
        "simple_screening": simple,
        "engineering_temperature_corrected": engineering,
        "detailed_heterogeneous_site_reference": detailed,
        "scientific_technical_approval": "NOT_EVALUATED",
    }
