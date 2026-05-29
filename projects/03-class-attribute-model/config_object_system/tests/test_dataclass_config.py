from __future__ import annotations

import pytest

from config_object_system import DataclassAppConfig, ValidationError


def test_dataclass_config_defaults_and_to_dict() -> None:
    config = DataclassAppConfig()

    assert config.host == "127.0.0.1"
    assert config.port == 8000
    assert config.debug is False
    assert config.features == ()
    assert config.to_dict() == {
        "host": "127.0.0.1",
        "port": 8000,
        "debug": False,
        "features": [],
    }


def test_dataclass_config_validates_and_copies_features() -> None:
    features = ["metrics"]

    config = DataclassAppConfig(features=features)
    features.append("mutated")

    assert config.features == ("metrics",)


def test_dataclass_config_rejects_invalid_values() -> None:
    with pytest.raises(ValidationError):
        DataclassAppConfig(host="")

    with pytest.raises(ValidationError):
        DataclassAppConfig(port=0)

    with pytest.raises(ValidationError):
        DataclassAppConfig(debug=1)  # type: ignore[arg-type]

    with pytest.raises(ValidationError):
        DataclassAppConfig(features=["valid", 123])  # type: ignore[list-item]


def test_dataclass_slots_prevent_unknown_attributes() -> None:
    config = DataclassAppConfig()

    with pytest.raises(AttributeError):
        config.unknown = "nope"  # type: ignore[attr-defined]

