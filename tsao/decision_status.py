"""Conservative aggregation: an explicit FAIL always survives aggregation."""

from collections.abc import Iterable

STATES = frozenset({"PASS", "FAIL", "HOLD", "CONDITIONAL", "NOT_EVALUATED"})


def aggregate_status(values: Iterable[str]) -> str:
    values = tuple(values)
    if not values:
        return "NOT_EVALUATED"
    if any(not isinstance(value, str) or value not in STATES for value in values):
        return "FAIL"
    if "FAIL" in values:
        return "FAIL"
    if "HOLD" in values or "CONDITIONAL" in values:
        return "HOLD"
    if "NOT_EVALUATED" in values:
        return "NOT_EVALUATED"
    return "PASS"
