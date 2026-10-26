"""Identity of the scientifically corrected POE mass-moment workloads.

Performance identity is separate from scientific validation. The independent
population and analytical integration tests establish the latter; this module
prevents comparison of the old 11-state model with the corrected 13-state model.
"""

from __future__ import annotations

POE_MASS_MOMENT_BASELINE_COMMIT = "a06644431231e5c72362839ac6b37362a48e6218"
MODEL_ID = "POE_CHAIN_MASS_SECOND_MOMENT_13_STATE_V1"
STATE_FIELDS = (
    "monomer_a",
    "monomer_b",
    "dormant_sites",
    "live_chains",
    "live_a_units",
    "live_b_units",
    "live_second_moment",
    "dead_chains",
    "dead_a_units",
    "dead_b_units",
    "dead_second_moment",
    "live_mass_second_moment",
    "dead_mass_second_moment",
)
WORKLOADS = {
    "poe_rk4_400_steps": (20.0, 0.05, True),
    "poe_rk4_10000_steps": (100.0, 0.01, True),
    "poe_rk4_10000_steps_terminal": (100.0, 0.01, False),
}
# Reproduced from the untouched 8719e591 source. The first two also match the
# complete recorded alpha10 results. These identify a historical model, not a
# numerical oracle for the additional mass moments or corrected Mw.
LEGACY_RESULT_DIGESTS = {
    "poe_rk4_400_steps": "5a158478b8fd13c6c7ab77c6255a650f4025d8a5732a947ff2eaed47caf5acf5",
    "poe_rk4_10000_steps": "ce9c3ddbd35226eefab4cc866f8f834091e1ab55935bfb886de39dce971c7223",
    "poe_rk4_10000_steps_terminal": "27d8acb9fe9e88aa8e7ded58e4e23a1013773ef072ab9bb6e25845cf784d4503",
}


def workload_identity(name: str) -> dict[str, object]:
    duration, step, history = WORKLOADS[name]
    return {
        "model_id": MODEL_ID,
        "state_fields": list(STATE_FIELDS),
        "method": "CLASSICAL_RK4",
        "duration_s": duration,
        "step_s": step,
        "store_history": history,
        "initial_monomer_a_mol_L": 1.2,
        "initial_monomer_b_mol_L": 0.8,
        "initial_dormant_sites_mol_L": 0.01,
        "initial_other_states": 0.0,
        "parameters": [0.002, 0.08, 0.05, 0.003, 0.0005, 28.05, 112.22],
        "molecular_metric": "Mw=sum(n*M^2)/sum(n*M)",
        "scientific_approval": "NOT_EVALUATED",
    }


def identity_error(name: str, before: dict[str, object], after: dict[str, object]) -> str | None:
    if name not in WORKLOADS:
        return None
    before_id, after_id = before.get("workload_identity"), after.get("workload_identity")
    if before_id is None and after_id is None:
        # Old report pairs retain the existing exact-result comparison.
        return None
    expected = workload_identity(name)
    if before_id != expected or after_id != expected:
        return "POE model or workload identity is missing or inconsistent"
    return None


def historical_model_change(name: str, before: dict[str, object], after: dict[str, object]) -> bool:
    return (
        name in WORKLOADS
        and before.get("workload_identity") is None
        and before.get("result_sha256") == LEGACY_RESULT_DIGESTS[name]
        and after.get("workload_identity") == workload_identity(name)
    )
