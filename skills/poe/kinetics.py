from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from tsao.numeric_contract import finite_product, finite_sum


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
        for name in _PARAMETER_FIELDS:
            value = getattr(self, name)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
            ):
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
    # Optional only when the corresponding population is empty.  Molar-mass
    # second moments have units (g/mol)^2 mol/L.
    live_mass_second_moment: float | None = None
    dead_mass_second_moment: float | None = None

    def validate(self) -> None:
        for name in _STATE_FIELDS:
            value = getattr(self, name)
            if name in _MASS_MOMENT_FIELDS and value is None:
                continue
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
            ):
                raise ValueError(f"{name} must be finite")
            if value < 0:
                raise ValueError(f"{name} must be non-negative")

        for label, chains, units, mass_moment in (
            (
                "live",
                self.live_chains,
                self.live_a_units + self.live_b_units,
                self.live_mass_second_moment,
            ),
            (
                "dead",
                self.dead_chains,
                self.dead_a_units + self.dead_b_units,
                self.dead_mass_second_moment,
            ),
        ):
            if units > 0 and chains == 0:
                raise ValueError(f"{label} chains are required when polymer units are present")
            if chains > 0 and units == 0:
                raise ValueError(
                    f"{label} polymer units are required when {label} chains are present"
                )
            if chains > 0 and mass_moment is None:
                raise ValueError(
                    f"{label}_mass_second_moment is required when {label} chains are present"
                )
            if chains == 0 and mass_moment not in (None, 0.0):
                raise ValueError(
                    f"{label}_mass_second_moment must be zero when no {label} chains are present"
                )
            if chains > 0 and units > 0 and mass_moment == 0:
                raise ValueError(
                    f"{label}_mass_second_moment must be positive when polymer units are present"
                )


_PARAMETER_FIELDS = tuple(KineticParameters.__dataclass_fields__)
_STATE_FIELDS = tuple(KineticState.__dataclass_fields__)
_MASS_MOMENT_FIELDS = ("live_mass_second_moment", "dead_mass_second_moment")


def _validate_mass_moment_lower_bounds(state: KineticState, params: KineticParameters) -> None:
    """Reject seed moments that violate Cauchy-Schwarz for a chain population."""
    for label, chains, mass_moment in (
        ("live", state.live_chains, state.live_mass_second_moment),
        ("dead", state.dead_chains, state.dead_mass_second_moment),
    ):
        if chains == 0:
            continue
        mass_concentration = finite_sum(
            (
                finite_product(
                    getattr(state, f"{label}_a_units"),
                    params.molar_mass_a,
                    label=f"{label} A polymer mass",
                ),
                finite_product(
                    getattr(state, f"{label}_b_units"),
                    params.molar_mass_b,
                    label=f"{label} B polymer mass",
                ),
            ),
            label=f"{label} polymer mass concentration",
        )
        minimum_mass_moment = finite_product(
            mass_concentration,
            mass_concentration,
            divisor=chains,
            label=f"{label} minimum mass second moment",
        )
        assert mass_moment is not None
        if mass_moment < minimum_mass_moment and not math.isclose(
            mass_moment,
            minimum_mass_moment,
            rel_tol=1e-12,
            abs_tol=8 * math.ulp(minimum_mass_moment),
        ):
            raise ValueError(
                f"{label}_mass_second_moment is below the minimum implied by its polymer mass and chain count"
            )


StateVector = tuple[
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
    float,
]


def _state_vector(state: KineticState) -> StateVector:
    return (
        state.monomer_a,
        state.monomer_b,
        state.dormant_sites,
        state.live_chains,
        state.live_a_units,
        state.live_b_units,
        state.live_second_moment,
        state.dead_chains,
        state.dead_a_units,
        state.dead_b_units,
        state.dead_second_moment,
        state.live_mass_second_moment or 0.0,
        state.dead_mass_second_moment or 0.0,
    )


def _state_from_vector(values: StateVector) -> KineticState:
    return KineticState(*values)


def _state_dict_from_vector(values: StateVector) -> dict[str, float]:
    return dict(zip(_STATE_FIELDS, values, strict=True))


def _state_dict(state: KineticState) -> dict[str, float]:
    return _state_dict_from_vector(_state_vector(state))


def _kinetic_derivative_vector(state: StateVector, params: KineticParameters) -> StateVector:
    (
        a,
        b,
        dormant,
        live_n,
        live_a,
        live_b,
        live_second,
        _dead_n,
        _dead_a,
        _dead_b,
        _dead_second,
        live_mass_second,
        _dead_mass_second,
    ) = state
    live_m1 = live_a + live_b
    avg_live_length = live_m1 / live_n if live_n > 0 else 0.0
    live_mass = live_a * params.molar_mass_a + live_b * params.molar_mass_b
    avg_live_mass = live_mass / live_n if live_n > 0 else 0.0

    r_init = params.k_init * dormant * a
    r_pa = params.k_prop_a * a * live_n
    r_pb = params.k_prop_b * b * live_n
    r_transfer = params.k_transfer * live_n
    r_deact_live = params.k_deactivation * live_n
    r_deact_dormant = params.k_deactivation * dormant
    loss = r_transfer + r_deact_live

    frac_a = live_a / live_m1 if live_m1 > 0 else 0.0
    frac_b = live_b / live_m1 if live_m1 > 0 else 0.0
    loss_a = loss * avg_live_length * frac_a
    loss_b = loss * avg_live_length * frac_b
    loss_m2 = loss * (live_second / live_n if live_n > 0 else 0.0)
    propagation_m2 = (r_pa + r_pb) * (2.0 * avg_live_length + 1.0)
    loss_mass_m2 = loss * (live_mass_second / live_n if live_n > 0 else 0.0)
    propagation_mass_m2 = r_pa * (
        2.0 * params.molar_mass_a * avg_live_mass + params.molar_mass_a**2
    ) + r_pb * (2.0 * params.molar_mass_b * avg_live_mass + params.molar_mass_b**2)
    initiation_mass_m2 = r_init * params.molar_mass_a**2

    return (
        -(r_init + r_pa),
        -r_pb,
        -r_init + r_transfer - r_deact_dormant,
        r_init - loss,
        r_init + r_pa - loss_a,
        r_pb - loss_b,
        r_init + propagation_m2 - loss_m2,
        loss,
        loss_a,
        loss_b,
        loss_m2,
        initiation_mass_m2 + propagation_mass_m2 - loss_mass_m2,
        loss_mass_m2,
    )


def _kinetic_derivative_validated(state: KineticState, params: KineticParameters) -> KineticState:
    return _state_from_vector(_kinetic_derivative_vector(_state_vector(state), params))


def kinetic_derivative(state: KineticState, params: KineticParameters) -> KineticState:
    """Reference moment model, independent of the historical MATLAB program.

    Units contract:
    - concentrations and chain moments use mol/L equivalents;
    - time uses seconds;
    - bimolecular constants use L/(mol s);
    - first-order transfer/deactivation constants use 1/s.

    The mass-moment closure assumes chain-independent propagation, transfer
    and deactivation rates. It is a transparent qualification fixture, not a
    fitted industrial model.
    """
    state.validate()
    params.validate()
    _validate_mass_moment_lower_bounds(state, params)
    derivative = _kinetic_derivative_validated(state, params)
    for name, value in zip(_STATE_FIELDS, _state_vector(derivative), strict=True):
        if not math.isfinite(value):
            raise ValueError(f"kinetic derivative for {name} is non-finite")
    return derivative


def _state_add_vector(state: StateVector, derivative: StateVector, factor: float) -> StateVector:
    values: list[float] = []
    for index, name in enumerate(_STATE_FIELDS):
        value = state[index] + factor * derivative[index]
        # Reject failed arithmetic before positivity clipping: max(0.0, NaN)
        # would otherwise silently turn a failed stage into an all-zero state.
        if not math.isfinite(value):
            raise ValueError(f"integration produced non-finite {name}: {value}")
        if value < -1e-10:
            raise ValueError(f"integration produced materially negative {name}: {value}")
        values.append(value if value > 0.0 else 0.0)
    return tuple(values)  # type: ignore[return-value]


def _rk4_combined_vector(
    k1: StateVector,
    k2: StateVector,
    k3: StateVector,
    k4: StateVector,
) -> StateVector:
    return tuple(
        (value1 + 2.0 * value2 + 2.0 * value3 + value4) / 6.0
        for value1, value2, value3, value4 in zip(k1, k2, k3, k4, strict=True)
    )  # type: ignore[return-value]


def _validated_time_inputs(duration_s: float, step_s: float) -> tuple[float, float]:
    for name, value in (("duration_s", duration_s), ("step_s", step_s)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a finite real number")
    duration = float(duration_s)
    step = float(step_s)
    if not math.isfinite(duration) or duration < 0:
        raise ValueError("duration_s must be finite and non-negative")
    if not math.isfinite(step) or step <= 0:
        raise ValueError("step_s must be finite and positive")
    return duration, step


def _integrate_vectors(
    initial: KineticState,
    params: KineticParameters,
    duration_s: float,
    step_s: float,
    *,
    store_history: bool,
) -> tuple[StateVector, list[dict[str, float]] | None]:
    initial.validate()
    params.validate()
    _validate_mass_moment_lower_bounds(initial, params)
    duration, step = _validated_time_inputs(duration_s, step_s)
    state = _state_vector(initial)
    time_s = 0.0
    history = [{"time_s": 0.0, **_state_dict_from_vector(state)}] if store_history else None
    # Completion is relative to the requested interval, not an absolute number
    # of seconds. An absolute epsilon can discard an entire rescaled problem.
    while time_s < duration:
        h = min(step, duration - time_s)
        next_time = time_s + h
        if next_time <= time_s:
            raise ValueError("integration step cannot advance floating-point time")
        k1 = _kinetic_derivative_vector(state, params)
        k2 = _kinetic_derivative_vector(_state_add_vector(state, k1, h / 2.0), params)
        k3 = _kinetic_derivative_vector(_state_add_vector(state, k2, h / 2.0), params)
        k4 = _kinetic_derivative_vector(_state_add_vector(state, k3, h), params)
        state = _state_add_vector(state, _rk4_combined_vector(k1, k2, k3, k4), h)
        time_s = next_time
        if history is not None:
            history.append({"time_s": time_s, **_state_dict_from_vector(state)})
    return state, history


def simulate_kinetics(
    initial: KineticState,
    params: KineticParameters,
    duration_s: float,
    step_s: float,
) -> dict[str, Any]:
    state_values, history = _integrate_vectors(
        initial, params, duration_s, step_s, store_history=True
    )
    final = _state_from_vector(state_values)
    assert history is not None
    return {
        "status": "CALCULATED_REFERENCE_ONLY",
        "final": _state_dict_from_vector(state_values),
        "metrics": _kinetic_metrics_validated(initial, final, params),
        "history": history,
        "historical_matlab_reused": False,
        "scientific_approval": "NOT_EVALUATED",
    }


def simulate_kinetics_terminal(
    initial: KineticState,
    params: KineticParameters,
    duration_s: float,
    step_s: float,
) -> dict[str, Any]:
    """Run the same RK4 reference model without allocating a time-history list."""
    state_values, _ = _integrate_vectors(initial, params, duration_s, step_s, store_history=False)
    final = _state_from_vector(state_values)
    return {
        "status": "CALCULATED_REFERENCE_ONLY",
        "final": _state_dict_from_vector(state_values),
        "metrics": _kinetic_metrics_validated(initial, final, params),
        "history_stored": False,
        "historical_matlab_reused": False,
        "scientific_approval": "NOT_EVALUATED",
    }


def kinetic_metrics(
    initial: KineticState, final: KineticState, params: KineticParameters
) -> dict[str, float]:
    initial.validate()
    final.validate()
    params.validate()
    _validate_mass_moment_lower_bounds(initial, params)
    _validate_mass_moment_lower_bounds(final, params)
    return _kinetic_metrics_validated(initial, final, params)


def _kinetic_metrics_validated(
    initial: KineticState, final: KineticState, params: KineticParameters
) -> dict[str, float]:
    """Calculate metrics after the input state and parameter contracts are checked."""
    # Preserve the established arithmetic path and its locked reference output
    # whenever it is representable; use checked summation only for overflow cases.
    initial_total_a = initial.live_a_units + initial.dead_a_units
    initial_total_b = initial.live_b_units + initial.dead_b_units
    initial_polymer_units = initial_total_a + initial_total_b
    total_a = final.live_a_units + final.dead_a_units
    total_b = final.live_b_units + final.dead_b_units
    polymer_units = total_a + total_b
    polymer_increment = polymer_units - initial_polymer_units
    consumed = initial.monomer_a + initial.monomer_b - final.monomer_a - final.monomer_b
    balance_residual = consumed - polymer_increment
    chain_count = final.live_chains + final.dead_chains
    polymer_mass = total_a * params.molar_mass_a + total_b * params.molar_mass_b
    mass_second_moment = (final.live_mass_second_moment or 0.0) + (
        final.dead_mass_second_moment or 0.0
    )
    mn = polymer_mass / chain_count if chain_count > 0 else 0.0
    mw = mass_second_moment / polymer_mass if polymer_mass > 0 else 0.0
    legacy_result = {
        "polymer_units_mol_L": polymer_units,
        "monomer_consumed_mol_L": consumed,
        "mass_balance_residual_mol_L": balance_residual,
        "number_average_molar_mass_g_mol": mn,
        "weight_average_molar_mass_g_mol": mw,
        "comonomer_mole_fraction": total_b / polymer_units if polymer_units > 0 else 0.0,
    }
    if all(math.isfinite(value) for value in legacy_result.values()):
        return legacy_result

    initial_total_a = finite_sum(
        (initial.live_a_units, initial.dead_a_units), label="initial A units"
    )
    initial_total_b = finite_sum(
        (initial.live_b_units, initial.dead_b_units), label="initial B units"
    )
    initial_polymer_units = finite_sum(
        (initial_total_a, initial_total_b), label="initial polymer units"
    )
    total_a = finite_sum((final.live_a_units, final.dead_a_units), label="final A units")
    total_b = finite_sum((final.live_b_units, final.dead_b_units), label="final B units")
    polymer_units = finite_sum((total_a, total_b), label="final polymer units")
    polymer_increment = finite_sum(
        (polymer_units, -initial_polymer_units), label="polymer increment"
    )
    consumed_a = finite_sum((initial.monomer_a, -final.monomer_a), label="A monomer consumption")
    consumed_b = finite_sum((initial.monomer_b, -final.monomer_b), label="B monomer consumption")
    consumed = finite_sum((consumed_a, consumed_b), label="total monomer consumption")
    balance_residual = finite_sum((consumed, -polymer_increment), label="mass balance residual")
    chain_count = finite_sum((final.live_chains, final.dead_chains), label="chain count")
    polymer_mass = finite_sum(
        (
            finite_product(total_a, params.molar_mass_a, label="A polymer mass"),
            finite_product(total_b, params.molar_mass_b, label="B polymer mass"),
        ),
        label="polymer mass concentration",
    )
    mn = (
        finite_product(polymer_mass, divisor=chain_count, label="number-average molar mass")
        if chain_count > 0
        else 0.0
    )
    mass_second_moment = finite_sum(
        (final.live_mass_second_moment or 0.0, final.dead_mass_second_moment or 0.0),
        label="polymer molar-mass second moment",
    )
    mw = (
        finite_product(mass_second_moment, divisor=polymer_mass, label="weight-average molar mass")
        if polymer_mass > 0
        else 0.0
    )
    return {
        "polymer_units_mol_L": polymer_units,
        "monomer_consumed_mol_L": consumed,
        "mass_balance_residual_mol_L": balance_residual,
        "number_average_molar_mass_g_mol": mn,
        "weight_average_molar_mass_g_mol": mw,
        "comonomer_mole_fraction": (
            finite_product(total_b, divisor=polymer_units, label="comonomer mole fraction")
            if polymer_units > 0
            else 0.0
        ),
    }
