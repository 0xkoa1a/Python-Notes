from __future__ import annotations

import pytest

from config_object_system import AppConfig, ConfigError, ValidationError


def test_validation_error_is_config_error() -> None:
    assert issubclass(ValidationError, ConfigError)


@pytest.mark.parametrize("host", ["", "   ", 123])
def test_host_must_be_non_empty_string(host: object) -> None:
    with pytest.raises(ValidationError):
        AppConfig(host=host)  # type: ignore[arg-type]


@pytest.mark.parametrize("port", [0, -1, 65536, "8000"])
def test_port_must_be_integer_in_valid_range(port: object) -> None:
    with pytest.raises(ValidationError):
        AppConfig(port=port)  # type: ignore[arg-type]


@pytest.mark.parametrize("debug", [1, 0, "true", None])
def test_debug_must_be_bool_when_explicitly_provided(debug: object) -> None:
    with pytest.raises(ValidationError):
        AppConfig(debug=debug)  # type: ignore[arg-type]


def test_features_must_be_strings() -> None:
    with pytest.raises(ValidationError):
        AppConfig(features=["metrics", 123])  # type: ignore[list-item]


def test_property_setters_validate_later_assignment() -> None:
    config = AppConfig()

    with pytest.raises(ValidationError):
        config.host = ""

    with pytest.raises(ValidationError):
        config.port = 70000

    with pytest.raises(ValidationError):
        config.debug = 1  # type: ignore[assignment]

    with pytest.raises(ValidationError):
        config.features = ["valid", object()]  # type: ignore[list-item]


def test_slots_prevent_unknown_instance_attributes() -> None:
    config = AppConfig()

    with pytest.raises(AttributeError):
        config.unknown = "nope"  # type: ignore[attr-defined]

