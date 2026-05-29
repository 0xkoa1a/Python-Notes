"""Hand-written configuration classes for practicing class attributes."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Self

from .errors import ValidationError


class AppConfig:
    """A hand-written configuration object with validated properties."""

    __slots__ = ("_host", "_port", "_debug", "_features")

    default_host = "127.0.0.1"
    default_port = 8000
    default_debug = False
    default_features: tuple[str, ...] = ()

    def __init__(
        self,
        *,
        host: str | None = None,
        port: int | None = None,
        debug: bool | None = None,
        features: Iterable[str] | None = None,
    ) -> None:
        """Initialize instance state from arguments or class defaults.

        TODO: Use property setters so validation is shared by construction and
        later assignment.

        self is the new instance object. type(self) may be a subclass, so
        default values should be read through self.default_* instead of hard-coded.
        """

        raise NotImplementedError("Implement AppConfig.__init__")

    @property
    def host(self) -> str:
        """Validated host string."""

        raise NotImplementedError("Implement AppConfig.host getter")

    @host.setter
    def host(self, value: str) -> None:
        """Validate and store host.

        This setter is called by `config.host = value` and can also be reused by
        __init__.
        """

        raise NotImplementedError("Implement AppConfig.host setter")

    @property
    def port(self) -> int:
        """Validated TCP port."""

        raise NotImplementedError("Implement AppConfig.port getter")

    @port.setter
    def port(self, value: int) -> None:
        """Validate and store port."""

        raise NotImplementedError("Implement AppConfig.port setter")

    @property
    def debug(self) -> bool:
        """Whether debug mode is enabled."""

        raise NotImplementedError("Implement AppConfig.debug getter")

    @debug.setter
    def debug(self, value: bool) -> None:
        """Validate and store debug flag."""

        raise NotImplementedError("Implement AppConfig.debug setter")

    @property
    def features(self) -> tuple[str, ...]:
        """Enabled feature names as an immutable tuple."""

        raise NotImplementedError("Implement AppConfig.features getter")

    @features.setter
    def features(self, value: Iterable[str]) -> None:
        """Validate and store features as a tuple.

        value may be any iterable of strings. Store a tuple so caller-owned
        mutable lists cannot become shared instance state.
        """

        raise NotImplementedError("Implement AppConfig.features setter")

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly dictionary representation.

        TODO: Return fresh container objects. Mutating the returned dict or list
        should not mutate this AppConfig instance.
        """

        raise NotImplementedError("Implement AppConfig.to_dict")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Build a config object from a dictionary.

        TODO: Call cls(...), not AppConfig(...).

        cls is the class object used for this call. If DevelopmentConfig calls
        this method, cls should be DevelopmentConfig.
        """

        raise NotImplementedError("Implement AppConfig.from_dict")

    def with_overrides(self, **changes: object) -> Self:
        """Return a new config object with selected fields replaced.

        TODO: Start from self.to_dict(), apply changes, then call type(self)(...).

        type(self) is the runtime class of this instance. Using it preserves
        subclass type when a DevelopmentConfig or ProductionConfig is overridden.
        """

        raise NotImplementedError("Implement AppConfig.with_overrides")


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

    raise ValidationError("Implement validate_host")


def validate_port(value: object) -> int:
    """Validate port and return normalized value."""

    raise ValidationError("Implement validate_port")


def validate_debug(value: object) -> bool:
    """Validate debug and return normalized value."""

    raise ValidationError("Implement validate_debug")


def validate_features(value: Iterable[object]) -> tuple[str, ...]:
    """Validate features and return an immutable tuple."""

    raise ValidationError("Implement validate_features")

