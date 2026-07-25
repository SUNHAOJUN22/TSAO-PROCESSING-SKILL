from __future__ import annotations

import math
from dataclasses import dataclass

from .kinetics import EpdmKineticParameters, EpdmKineticState, insertion_rates


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
class SemibatchInventory:
    volume_L: float
    ethylene_mol: float
    propylene_mol: float
    diene_mol: float
    polymer_repeat_mol: float
    temperature_K: float
    heat_capacity_kJ_K: float

    def validated(self) -> SemibatchInventory:
        values = {name: _finite(value, name) for name, value in self.__dict__.items()}
        if min(values.values()) < 0:
            raise ValueError("semibatch inventory values must be non-negative")
        if values["volume_L"] <= 0 or values["temperature_K"] <= 0:
            raise ValueError("volume and temperature must be positive")
        if values["heat_capacity_kJ_K"] <= 0:
            raise ValueError("heat capacity must be positive")
        return SemibatchInventory(**values)


@dataclass(frozen=True)
class SemibatchFeed:
    ethylene_mol_s: float
    propylene_mol_s: float
    diene_mol_s: float
    liquid_volume_L_s: float = 0.0

    def validated(self) -> SemibatchFeed:
        values = {name: _finite(value, name) for name, value in self.__dict__.items()}
        if min(values.values()) < 0:
            raise ValueError("semibatch feed values must be non-negative")
        return SemibatchFeed(**values)


def heat_removal_margin(generation_kW: float, removal_capacity_kW: float) -> float:
    generation = _finite(generation_kW, "heat generation")
    capacity = _finite(removal_capacity_kW, "heat removal capacity")
    if generation < 0 or capacity <= 0:
        raise ValueError("generation must be non-negative and capacity positive")
    return (capacity - generation) / capacity


def mixing_reynolds(
    density_kg_m3: float, speed_s: float, diameter_m: float, viscosity_Pa_s: float
) -> float:
    density = _finite(density_kg_m3, "density")
    speed = _finite(speed_s, "speed")
    diameter = _finite(diameter_m, "diameter")
    viscosity = _finite(viscosity_Pa_s, "viscosity")
    if min(density, speed, diameter, viscosity) <= 0:
        raise ValueError("mixing inputs must be positive")
    return density * speed * diameter**2 / viscosity


def recycle_poison_steady_state(
    fresh_poison_mol_h: float,
    recycle_fraction: float,
    purge_fraction: float,
    guard_removal_fraction: float,
) -> float:
    fresh = _finite(fresh_poison_mol_h, "fresh poison")
    recycle = _finite(recycle_fraction, "recycle fraction")
    purge = _finite(purge_fraction, "purge fraction")
    guard = _finite(guard_removal_fraction, "guard removal fraction")
    if fresh < 0 or not 0 <= recycle < 1 or not 0 <= purge <= 1 or not 0 <= guard <= 1:
        raise ValueError("invalid recycle-poison inputs")
    retained = recycle * (1.0 - purge) * (1.0 - guard)
    if retained >= 1.0:
        raise ValueError("recycle poison has no finite steady state")
    return fresh / (1.0 - retained)


def devolatilization_residual(
    initial_mass_fraction: float, rate_s: float, residence_s: float
) -> float:
    initial = _finite(initial_mass_fraction, "initial volatile fraction")
    rate = _finite(rate_s, "devolatilization rate")
    residence = _finite(residence_s, "residence time")
    if not 0 <= initial <= 1 or rate < 0 or residence < 0:
        raise ValueError("invalid devolatilization inputs")
    return initial * math.exp(-rate * residence)


def devolatilization_damkohler(rate_s: float, residence_s: float) -> float:
    rate = _finite(rate_s, "devolatilization rate")
    residence = _finite(residence_s, "residence time")
    if rate < 0 or residence < 0:
        raise ValueError("rate and residence time must be non-negative")
    return rate * residence


def grade_transition_offspec_fraction(residence_s: float, transition_s: float) -> float:
    residence = _finite(residence_s, "residence time")
    transition = _finite(transition_s, "transition time")
    if residence <= 0 or transition < 0:
        raise ValueError("residence time must be positive and transition time non-negative")
    return min(1.0, transition / (transition + residence))


def mooney_reference(mw_kg_mol: float, branch_index: float, oil_phr: float = 0.0) -> float:
    mw = _finite(mw_kg_mol, "molecular weight")
    branch = _finite(branch_index, "branch index")
    oil = _finite(oil_phr, "oil phr")
    if mw <= 0 or branch < 0 or oil < 0:
        raise ValueError("invalid Mooney reference inputs")
    return max(0.0, 8.0 + 18.0 * math.log10(mw) + 12.0 * branch - 0.18 * oil)


def flory_huggins_stability_margin(
    polymer_volume_fraction: float,
    polymerization_degree: float,
    interaction_parameter: float,
) -> float:
    """Positive values are locally stable against binary spinodal decomposition."""
    phi = _finite(polymer_volume_fraction, "polymer volume fraction")
    degree = _finite(polymerization_degree, "polymerization degree")
    chi = _finite(interaction_parameter, "interaction parameter")
    if not 0 < phi < 1 or degree <= 0:
        raise ValueError("volume fraction must be in (0, 1) and degree must be positive")
    return 1.0 / (degree * phi) + 1.0 / (1.0 - phi) - 2.0 * chi


def entropy_generation_heat_transfer_kW_K(
    heat_duty_kW: float,
    hot_temperature_K: float,
    cold_temperature_K: float,
) -> float:
    duty = _finite(heat_duty_kW, "heat duty")
    hot = _finite(hot_temperature_K, "hot temperature")
    cold = _finite(cold_temperature_K, "cold temperature")
    if duty < 0 or cold <= 0 or hot <= cold:
        raise ValueError("duty must be non-negative and hot temperature must exceed cold")
    return duty * (1.0 / cold - 1.0 / hot)


def semibatch_material_energy_step(
    inventory: SemibatchInventory,
    feed: SemibatchFeed,
    parameters: EpdmKineticParameters,
    *,
    active_site_mol_L: float,
    poison_mol_L: float,
    step_s: float,
    reaction_enthalpy_kJ_mol: float,
    heat_removal_kW: float,
) -> dict[str, object]:
    """One conservative semibatch reference step with explicit heat accounting."""
    inventory = inventory.validated()
    feed = feed.validated()
    parameters = parameters.validated()
    active_site = _finite(active_site_mol_L, "active site concentration")
    poison = _finite(poison_mol_L, "poison concentration")
    duration = _finite(step_s, "step duration")
    reaction_enthalpy = _finite(reaction_enthalpy_kJ_mol, "reaction enthalpy")
    heat_removal = _finite(heat_removal_kW, "heat removal")
    if min(active_site, poison, duration, reaction_enthalpy, heat_removal) < 0:
        raise ValueError("semibatch operating inputs must be non-negative")

    volume = inventory.volume_L + feed.liquid_volume_L_s * duration
    available = {
        "ethylene": inventory.ethylene_mol + feed.ethylene_mol_s * duration,
        "propylene": inventory.propylene_mol + feed.propylene_mol_s * duration,
        "diene": inventory.diene_mol + feed.diene_mol_s * duration,
    }
    state = EpdmKineticState(
        available["ethylene"] / volume,
        available["propylene"] / volume,
        available["diene"] / volume,
        active_site,
        poison,
    )
    rates = insertion_rates(state, parameters)
    consumed = {
        name: min(available[name], rates[name] * volume * duration)
        for name in ("ethylene", "propylene", "diene")
    }
    remaining = {name: available[name] - consumed[name] for name in available}
    polymer_increment = sum(consumed.values())
    heat_generated_kJ = polymer_increment * reaction_enthalpy
    heat_removed_kJ = heat_removal * duration
    temperature = inventory.temperature_K + (
        heat_generated_kJ - heat_removed_kJ
    ) / inventory.heat_capacity_kJ_K
    if temperature <= 0:
        raise ValueError("calculated temperature is non-physical")
    feed_total = duration * (
        feed.ethylene_mol_s + feed.propylene_mol_s + feed.diene_mol_s
    )
    monomer_before = inventory.ethylene_mol + inventory.propylene_mol + inventory.diene_mol
    closure = monomer_before + feed_total - sum(remaining.values()) - polymer_increment
    return {
        "inventory": {
            "volume_L": volume,
            "ethylene_mol": remaining["ethylene"],
            "propylene_mol": remaining["propylene"],
            "diene_mol": remaining["diene"],
            "polymer_repeat_mol": inventory.polymer_repeat_mol + polymer_increment,
            "temperature_K": temperature,
            "heat_capacity_kJ_K": inventory.heat_capacity_kJ_K,
        },
        "rates_mol_L_s": rates,
        "consumed_mol": consumed,
        "polymer_increment_mol": polymer_increment,
        "heat_generated_kJ": heat_generated_kJ,
        "heat_removed_kJ": heat_removed_kJ,
        "molar_closure_residual": closure,
        "status": "CALCULATED_REFERENCE_ONLY",
    }
