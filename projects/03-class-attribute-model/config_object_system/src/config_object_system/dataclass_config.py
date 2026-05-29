"""Dataclass implementation of the same config idea."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass(slots=True)
class DataclassAppConfig:
    """Dataclass version used to compare with the hand-written class."""

    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    features: Iterable[str] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate dataclass fields after generated __init__ runs.

        TODO: Use validation helpers and replace features with a tuple.

        __post_init__ runs after dataclass-generated __init__. It is the place
        to enforce runtime invariants because dataclass annotations do not
        validate values by themselves.
        """

        raise NotImplementedError("Implement DataclassAppConfig.__post_init__")

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly dictionary representation."""

        raise NotImplementedError("Implement DataclassAppConfig.to_dict")

