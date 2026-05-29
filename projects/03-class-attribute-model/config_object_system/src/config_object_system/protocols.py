"""Structural interfaces for config export."""

from __future__ import annotations

from typing import Protocol
from copy import deepcopy


class SupportsConfigExport(Protocol):
    """Structural interface for objects that can export config data."""

    def to_dict(self) -> dict[str, object]:
        """Return a dictionary representation."""


def dump_config(config: SupportsConfigExport) -> dict[str, object]:
    """Return a serializable config dictionary.

    TODO: Call config.to_dict() and return a fresh dict.

    config does not need to inherit AppConfig. It only needs to have a compatible
    to_dict method, which is what the Protocol expresses.
    """

    return deepcopy(config.to_dict())

