from __future__ import annotations

import math
import os
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_flow_mapping(
    label: str, values: Mapping[str, float], *, allow_negative: bool
) -> dict[str, float]:
    if not isinstance(values, Mapping):
        raise TypeError(f"{label} must be a mapping")
    checked: dict[str, float] = {}
    for key, raw_value in values.items():
        if not nonempty(key):
            raise ValueError(f"{label} keys must be non-empty strings")
        if isinstance(raw_value, bool):
            raise ValueError(f"{label}[{key!r}] must be numeric, not a boolean")
        try:
            value = float(raw_value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{label}[{key!r}] must be finite numeric") from exc
        if not math.isfinite(value):
            raise ValueError(f"{label}[{key!r}] must be finite")
        if not allow_negative and value < 0:
            raise ValueError(f"{label}[{key!r}] must be non-negative")
        checked[key] = value
    return checked


def required_or_default_string(data: Mapping[str, Any], key: str, default: str) -> str:
    value = data.get(key, default)
    if not nonempty(value):
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def atomic_write_text(path: Path, text: str) -> None:
    # The temporary belongs to this writer and resides on the target filesystem.
    # A shared `<name>.tmp` lets parallel writers replace or remove each other's data.
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
