"""Dataclass implementation of the same config idea."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from .config import validate_host, validate_port, validate_debug, validate_features

# dataclass 版本只保证构造后校验，不保证后续赋值校验。这正好展示了 dataclass 和 property 的差异
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

        self.host = validate_host(self.host)
        self.port = validate_port(self.port)
        self.debug = validate_debug(self.debug)
        self.features = validate_features(self.features)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly dictionary representation."""

        return {
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "features": list(self.features),
        }
