from __future__ import annotations

import math


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


def heat_removal_margin(generation_kW: float, removal_capacity_kW: float) -> float:
    generation = _finite(generation_kW, "heat generation")
    capacity = _finite(removal_capacity_kW, "heat removal capacity")
    if generation < 0 or capacity <= 0:
        raise ValueError("generation must be non-negative and capacity positive")
    return (capacity - generation) / capacity


def mixing_reynolds(density_kg_m3: float, speed_s: float, diameter_m: float, viscosity_Pa_s: float) -> float:
    density = _finite(density_kg_m3, "density")
    speed = _finite(speed_s, "speed")
    diameter = _finite(diameter_m, "diameter")
    viscosity = _finite(viscosity_Pa_s, "viscosity")
    if min(density, speed, diameter, viscosity) <= 0:
        raise ValueError("mixing inputs must be positive")
    return density * speed * diameter**2 / viscosity


def recycle_poison_steady_state(fresh_poison_mol_h: float, recycle_fraction: float, purge_fraction: float, guard_removal_fraction: float) -> float:
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


def devolatilization_residual(initial_mass_fraction: float, rate_s: float, residence_s: float) -> float:
    initial = _finite(initial_mass_fraction, "initial volatile fraction")
    rate = _finite(rate_s, "devolatilization rate")
    residence = _finite(residence_s, "residence time")
    if not 0 <= initial <= 1 or rate < 0 or residence < 0:
        raise ValueError("invalid devolatilization inputs")
    return initial * math.exp(-rate * residence)


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
