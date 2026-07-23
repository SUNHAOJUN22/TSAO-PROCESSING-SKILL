from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class KineticParameters:
    k_init: float
    k_prop_a: float
    k_prop_b: float
    k_transfer: float
    k_deactivation: float
    molar_mass_a: float = 28.05
    molar_mass_b: float = 112.22

    def validate(self) -> None:
        values = asdict(self)
        for name, value in values.items():
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise ValueError(f"{name} must be finite")
            if value < 0:
                raise ValueError(f"{name} must be non-negative")
        if self.molar_mass_a <= 0 or self.molar_mass_b <= 0:
            raise ValueError("monomer molar masses must be positive")


@dataclass(frozen=True)
class KineticState:
    monomer_a: float
    monomer_b: float
    dormant_sites: float
    live_chains: float = 0.0
    live_a_units: float = 0.0
    live_b_units: float = 0.0
    live_second_moment: float = 0.0
    dead_chains: float = 0.0
    dead_a_units: float = 0.0
    dead_b_units: float = 0.0
    dead_second_moment: float = 0.0

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise ValueError(f"{name} must be finite")
            if value < 0:
                raise ValueError(f"{name} must be non-negative")


_STATE_FIELDS = tuple(KineticState.__dataclass_fields__)


def kinetic_derivative(state: KineticState, params: KineticParameters) -> KineticState:
    """Reference moment model, independent of the historical MATLAB program.

    Units contract:
    - concentrations and chain moments use mol/L equivalents;
    - time uses seconds;
    - bimolecular constants use L/(mol s);
    - first-order transfer/deactivation constants use 1/s.

    It is a transparent qualification fixture, not a fitted industrial model.
    """
    state.validate()
    params.validate()
    a = state.monomer_a
    b = state.monomer_b
    dormant = state.dormant_sites
    live_n = state.live_chains
    live_m1 = state.live_a_units + state.live_b_units
    avg_live_length = live_m1 / live_n if live_n > 0 else 0.0

    r_init = params.k_init * dormant * a
    r_pa = params.k_prop_a * a * live_n
    r_pb = params.k_prop_b * b * live_n
    r_transfer = params.k_transfer * live_n
    r_deact_live = params.k_deactivation * live_n
    r_deact_dormant = params.k_deactivation * dormant
    loss = r_transfer + r_deact_live

    frac_a = state.live_a_units / live_m1 if live_m1 > 0 else 0.0
    frac_b = state.live_b_units / live_m1 if live_m1 > 0 else 0.0
    loss_a = loss * avg_live_length * frac_a
    loss_b = loss * avg_live_length * frac_b
    loss_m2 = loss * (state.live_second_moment / live_n if live_n > 0 else 0.0)
    propagation_m2 = (r_pa + r_pb) * (2.0 * avg_live_length + 1.0)

    return KineticState(
        monomer_a=-(r_init + r_pa),
        monomer_b=-r_pb,
        dormant_sites=-r_init + r_transfer - r_deact_dormant,
        live_chains=r_init - loss,
        live_a_units=r_init + r_pa - loss_a,
        live_b_units=r_pb - loss_b,
        live_second_moment=r_init + propagation_m2 - loss_m2,
        dead_chains=loss,
        dead_a_units=loss_a,
        dead_b_units=loss_b,
        dead_second_moment=loss_m2,
    )


def _state_add(state: KineticState, derivative: KineticState, factor: float) -> KineticState:
    values = {}
    for name in _STATE_FIELDS:
        value = getattr(state, name) + factor * getattr(derivative, name)
        if value < -1e-10:
            raise ValueError(f"integration produced materially negative {name}: {value}")
        values[name] = max(0.0, value)
    return KineticState(**values)


def simulate_kinetics(
    initial: KineticState,
    params: KineticParameters,
    duration_s: float,
    step_s: float,
) -> dict[str, Any]:
    initial.validate()
    params.validate()
    if not math.isfinite(duration_s) or duration_s < 0:
        raise ValueError("duration_s must be finite and non-negative")
    if not math.isfinite(step_s) or step_s <= 0:
        raise ValueError("step_s must be finite and positive")
    state = initial
    time_s = 0.0
    history = [{"time_s": 0.0, **asdict(state)}]
    while time_s < duration_s - 1e-15:
        h = min(step_s, duration_s - time_s)
        k1 = kinetic_derivative(state, params)
        k2 = kinetic_derivative(_state_add(state, k1, h / 2.0), params)
        k3 = kinetic_derivative(_state_add(state, k2, h / 2.0), params)
        k4 = kinetic_derivative(_state_add(state, k3, h), params)
        combined = KineticState(
            **{
                name: (
                    getattr(k1, name)
                    + 2.0 * getattr(k2, name)
                    + 2.0 * getattr(k3, name)
                    + getattr(k4, name)
                )
                / 6.0
                for name in _STATE_FIELDS
            }
        )
        state = _state_add(state, combined, h)
        time_s += h
        history.append({"time_s": time_s, **asdict(state)})
    return {
        "status": "CALCULATED_REFERENCE_ONLY",
        "final": asdict(state),
        "metrics": kinetic_metrics(initial, state, params),
        "history": history,
        "historical_matlab_reused": False,
        "scientific_approval": "NOT_EVALUATED",
    }


def kinetic_metrics(
    initial: KineticState, final: KineticState, params: KineticParameters
) -> dict[str, float]:
    total_a = final.live_a_units + final.dead_a_units
    total_b = final.live_b_units + final.dead_b_units
    polymer_units = total_a + total_b
    consumed = initial.monomer_a + initial.monomer_b - final.monomer_a - final.monomer_b
    balance_residual = consumed - polymer_units
    chain_count = final.live_chains + final.dead_chains
    second_moment = final.live_second_moment + final.dead_second_moment
    avg_monomer_mass = (
        (total_a * params.molar_mass_a + total_b * params.molar_mass_b) / polymer_units
        if polymer_units > 0
        else 0.0
    )
    mn = avg_monomer_mass * polymer_units / chain_count if chain_count > 0 else 0.0
    mw = avg_monomer_mass * second_moment / polymer_units if polymer_units > 0 else 0.0
    return {
        "polymer_units_mol_L": polymer_units,
        "monomer_consumed_mol_L": consumed,
        "mass_balance_residual_mol_L": balance_residual,
        "number_average_molar_mass_g_mol": mn,
        "weight_average_molar_mass_g_mol": mw,
        "comonomer_mole_fraction": total_b / polymer_units if polymer_units > 0 else 0.0,
    }
