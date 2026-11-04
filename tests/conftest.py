"""Pytest configuration and fixtures."""

from collections.abc import Iterator

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest


@pytest.fixture(autouse=True)
def _isolate_matplotlib() -> Iterator[None]:
    """Undo rcParams changes (such as an applied style) and close figures after each test."""
    with matplotlib.rc_context():
        yield
    plt.close("all")
