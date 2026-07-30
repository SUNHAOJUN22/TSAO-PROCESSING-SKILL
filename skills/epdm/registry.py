from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from .contracts import (
    ApplicabilityDomain,
    CatalystPassport,
    DienePassport,
    EvidenceRecord,
    KineticDataset,
    KineticParameter,
    RateLawDefinition,
    ThermoPassport,
    ValidationCriterion,
)

T = TypeVar("T")


class RegistryError(ValueError):
    """Base registry contract failure."""


class DuplicateRegistryIdError(RegistryError):
    pass


class UnresolvedRegistryIdError(RegistryError):
    pass


@dataclass(slots=True)
class IndexedRegistry(Generic[T]):
    label: str
    _items: dict[str, T] = field(default_factory=dict)

    def register(self, identifier: str, item: T) -> None:
        if identifier in self._items:
            raise DuplicateRegistryIdError(f"duplicate {self.label} ID: {identifier}")
        self._items[identifier] = item

    def require(self, identifier: str) -> T:
        try:
            return self._items[identifier]
        except KeyError as exc:
            raise UnresolvedRegistryIdError(
                f"unresolved {self.label} ID: {identifier}"
            ) from exc

    def get(self, identifier: str) -> T | None:
        return self._items.get(identifier)

    def as_mapping(self) -> Mapping[str, T]:
        return dict(self._items)

    def __len__(self) -> int:
        return len(self._items)


@dataclass(slots=True)
class ContractRegistry:
    evidence: IndexedRegistry[EvidenceRecord] = field(
        default_factory=lambda: IndexedRegistry("evidence")
    )
    applicability_domains: IndexedRegistry[ApplicabilityDomain] = field(
        default_factory=lambda: IndexedRegistry("applicability-domain")
    )
    catalysts: IndexedRegistry[CatalystPassport] = field(
        default_factory=lambda: IndexedRegistry("catalyst")
    )
    dienes: IndexedRegistry[DienePassport] = field(
        default_factory=lambda: IndexedRegistry("diene")
    )
    rate_laws: IndexedRegistry[RateLawDefinition] = field(
        default_factory=lambda: IndexedRegistry("rate-law")
    )
    kinetic_parameters: IndexedRegistry[KineticParameter] = field(
        default_factory=lambda: IndexedRegistry("kinetic-parameter")
    )
    thermo_passports: IndexedRegistry[ThermoPassport] = field(
        default_factory=lambda: IndexedRegistry("thermo-passport")
    )
    datasets: IndexedRegistry[KineticDataset] = field(
        default_factory=lambda: IndexedRegistry("dataset")
    )
    criteria: IndexedRegistry[ValidationCriterion] = field(
        default_factory=lambda: IndexedRegistry("criterion")
    )


def registry_from_pairs(label: str, pairs: Iterable[tuple[str, T]]) -> IndexedRegistry[T]:
    registry: IndexedRegistry[T] = IndexedRegistry(label)
    for identifier, item in pairs:
        registry.register(identifier, item)
    return registry
