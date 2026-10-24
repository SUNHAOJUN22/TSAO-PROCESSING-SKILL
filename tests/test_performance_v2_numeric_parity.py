from __future__ import annotations

import math
from decimal import Decimal, localcontext

import numpy as np

from scripts.benchmark_performance import _poe_dynamic_10k_case
from skills.poe.dynamics import fopdt_response, response_metrics
from skills.poe.estimation import finite_difference_jacobian
from tsao.doctor import diagnose


def _decimal_dynamic_reference(times: np.ndarray) -> np.ndarray:
    """Evaluate the reference model independently from its exact binary64 inputs."""
    with localcontext() as context:
        context.prec = 80
        response = []
        for time in times:
            effective = max(Decimal(0), Decimal.from_float(float(time)) - Decimal(3))
            response.append(float(Decimal(2) * (1 - (-effective / Decimal(12)).exp())))
    return np.array(response)


def test_dynamic_10000_point_response_matches_analytical_formula() -> None:
    times = np.linspace(0.0, 200.0, 10_000)
    response = fopdt_response(
        times,
        gain=2.0,
        time_constant_s=12.0,
        dead_time_s=3.0,
    )
    expected = _decimal_dynamic_reference(times)
    np.testing.assert_allclose(response, expected, rtol=2e-15, atol=0.0)
    metrics = response_metrics(times, response, target=2.0)
    assert metrics["rise_time_s"] is not None
    assert metrics["settling_time_s"] is not None
    assert metrics["overshoot_fraction"] == 0.0
    # Independent scalar composite-trapezoid oracle also runs on NumPy 1.26.
    errors = np.abs(expected - 2.0)
    expected_iae = math.fsum(
        (float(right_t) - float(left_t)) * (float(left_y) + float(right_y)) / 2.0
        for left_t, right_t, left_y, right_y in zip(
            times[:-1], times[1:], errors[:-1], errors[1:], strict=True
        )
    )
    np.testing.assert_allclose(
        metrics["integral_absolute_error"], expected_iae, rtol=2e-15, atol=2e-15
    )


def test_dynamic_benchmark_entry_preserves_named_10000_point_workload() -> None:
    case = _poe_dynamic_10k_case()
    times = np.linspace(0.0, 200.0, 10_000)
    expected_response = _decimal_dynamic_reference(times)

    response = case["response"]
    assert response.shape == (10_000,)
    np.testing.assert_allclose(response, expected_response, rtol=2e-15, atol=0.0)
    assert case["metrics"] == response_metrics(times, response, target=2.0)


def test_finite_difference_jacobian_matches_analytic_derivatives() -> None:
    observations = np.linspace(0.0, 20.0, 200)
    parameters = np.array([1.0, 0.2, 0.1, 0.01, 0.5, 0.3, 0.4, 0.2])

    def model(values: np.ndarray) -> np.ndarray:
        k1, k2, k3, k4, k5, k6, k7, k8 = values
        return (
            k1 * np.exp(-k2 * observations)
            + k3 * observations
            + k4 * observations**2
            + k5 * np.sin(k6 * observations)
            + k7 * np.cos(k8 * observations)
        )

    numeric = finite_difference_jacobian(model, parameters)
    k1, k2, _k3, _k4, k5, k6, k7, k8 = parameters
    analytic = np.column_stack(
        (
            np.exp(-k2 * observations),
            -k1 * observations * np.exp(-k2 * observations),
            observations,
            observations**2,
            np.sin(k6 * observations),
            k5 * observations * np.cos(k6 * observations),
            np.cos(k8 * observations),
            -k7 * observations * np.sin(k8 * observations),
        )
    )
    np.testing.assert_allclose(numeric, analytic, rtol=2e-8, atol=2e-8)


def test_finite_difference_jacobian_supports_reused_model_output_buffer() -> None:
    observations = np.linspace(0.0, 4.0, 32)
    shared_output = np.empty_like(observations)

    def model(values: np.ndarray) -> np.ndarray:
        shared_output[:] = values[0] * observations
        return shared_output

    numeric = finite_difference_jacobian(model, [2.0])
    np.testing.assert_allclose(numeric[:, 0], observations, rtol=1e-9, atol=1e-9)


def test_doctor_semantic_contract_preserves_approval_boundaries() -> None:
    result = diagnose(__import__("pathlib").Path(__file__).resolve().parents[1], profile="core")
    assert result["pass"] is True
    assert result["artifact_software_qualification"] == "PASS"
    assert result["scientific_technical_approval"] == "NOT_EVALUATED"
    assert result["engineering_design_approval"] == "NOT_EVALUATED"
    assert result["customer_qualification"] == "NOT_EVALUATED"
    assert result["industrial_performance_guarantee"] == "NOT_EVALUATED"
