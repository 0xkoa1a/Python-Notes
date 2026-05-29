"""Hand-written configuration classes for practicing class attributes."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Self
from copy import deepcopy

from .errors import ValidationError

_FIELDS = ("host", "port", "debug", "features")

class AppConfig:
    """A hand-written configuration object with validated properties."""

    __slots__ = ("_host", "_port", "_debug", "_features")

    default_host = "127.0.0.1"
    default_port = 8000
    default_debug = False
    default_features: tuple[str, ...] = ()

    def __init__(self, **overrides: object) -> None:
        """Initialize instance state from arguments or class defaults.

        TODO: Use property setters so validation is shared by construction and
        later assignment.

        self is the new instance object. type(self) may be a subclass, so
        default values should be read through self.default_* instead of hard-coded.
        """

        unknown = set(overrides) - set(_FIELDS)
        if unknown:
            names = ", ".join(sorted(unknown))
            raise TypeError(f"unknown config field: {names}")
        
        for name in _FIELDS:
            value = overrides[name] if name in overrides else getattr(type(self), f"default_{name}")
            setattr(self, name, value)

    @property
    def host(self) -> str:
        """Validated host string."""

        return self._host

    @host.setter
    def host(self, value: str) -> None:
        """Validate and store host.

        This setter is called by `config.host = value` and can also be reused by
        __init__.
        """

        self._host = validate_host(value)

    @property
    def port(self) -> int:
        """Validated TCP port."""

        return self._port

    @port.setter
    def port(self, value: int) -> None:
        """Validate and store port."""

        self._port = validate_port(value)

    @property
    def debug(self) -> bool:
        """Whether debug mode is enabled."""

        return self._debug

    @debug.setter
    def debug(self, value: bool) -> None:
        """Validate and store debug flag."""

        self._debug = validate_debug(value)

    @property
    def features(self) -> tuple[str, ...]:
        """Enabled feature names as an immutable tuple."""

        return self._features

    @features.setter
    def features(self, value: Iterable[str]) -> None:
        """Validate and store features as a tuple.

        value may be any iterable of strings. Store a tuple so caller-owned
        mutable lists cannot become shared instance state.
        """

        self._features = validate_features(value)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly dictionary representation.

        TODO: Return fresh container objects. Mutating the returned dict or list
        should not mutate this AppConfig instance.
        """

        return deepcopy({
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "features": list(self.features)
        })

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Build a config object from a dictionary.

        TODO: Call cls(...), not AppConfig(...).

        cls is the class object used for this call. If DevelopmentConfig calls
        this method, cls should be DevelopmentConfig.
        """

        return cls(**data)

    def with_overrides(self, **changes: object) -> Self:
        """Return a new config object with selected fields replaced.

        TODO: Start from self.to_dict(), apply changes, then call type(self)(...).

        type(self) is the runtime class of this instance. Using it preserves
        subclass type when a DevelopmentConfig or ProductionConfig is overridden.
        """

        d = self.to_dict()
        d.update(changes)
        return type(self).from_dict(d)


class DevelopmentConfig(AppConfig):
    """Development defaults expressed through class attributes."""

    default_debug = True
    default_features = ("reload",)


class ProductionConfig(AppConfig):
    """Production defaults expressed through class attributes."""

    default_host = "0.0.0.0"
    default_port = 80
    default_debug = False
    default_features: tuple[str, ...] = ()


def validate_host(value: object) -> str:
    """Validate host and return normalized value.

    TODO: Use this helper from AppConfig and DataclassAppConfig.
    """

    if type(value) is not str or not value.strip():
        raise ValidationError("Invalid host")
    return value.strip()


def validate_port(value: object) -> int:
    """Validate port and return normalized value."""

    if type(value) is not int:
        raise ValidationError("Port must be an integer")
    if value < 1 or value > 65535:
        raise ValidationError("Port must be in 1...65536")

    return int(value)


def validate_debug(value: object) -> bool:
    """Validate debug and return normalized value."""

    if type(value) is not bool:
        raise ValidationError("Debug must be a boolean value")
    return bool(value)


def validate_features(value: Iterable[object]) -> tuple[str, ...]:
    """Validate features and return an immutable tuple."""

    if not isinstance(value, Iterable):
        raise ValidationError("features must be an iterable of strings")
    
    if isinstance(value, str | bytes):
        raise ValidationError("features must be an iterable of feature names")

    features = tuple(value)

    if not all(isinstance(item, str) for item in features):
        raise ValidationError("features must contain only strings")

    return features
