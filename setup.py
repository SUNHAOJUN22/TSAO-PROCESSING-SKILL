"""Setuptools command hooks enforcing controlled-metadata containment."""

from __future__ import annotations

from pathlib import Path

from setuptools import setup
from setuptools.command.sdist import sdist as _sdist

from tsao.distribution_policy import assert_public_distribution_allowed


class ControlledSdist(_sdist):
    def run(self) -> None:
        assert_public_distribution_allowed(Path.cwd(), artifact_kind="public sdist")
        super().run()


cmdclass: dict[str, type] = {"sdist": ControlledSdist}

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
except ImportError:  # pragma: no cover - wheel is present in the declared build environment.
    _bdist_wheel = None

if _bdist_wheel is not None:
    class ControlledWheel(_bdist_wheel):  # type: ignore[misc,valid-type]
        def run(self) -> None:
            assert_public_distribution_allowed(Path.cwd(), artifact_kind="public wheel")
            super().run()

    cmdclass["bdist_wheel"] = ControlledWheel

setup(cmdclass=cmdclass)
