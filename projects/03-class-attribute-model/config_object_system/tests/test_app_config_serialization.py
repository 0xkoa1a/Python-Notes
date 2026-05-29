from __future__ import annotations

from config_object_system import AppConfig, DevelopmentConfig, ProductionConfig


def test_to_dict_returns_serializable_fresh_data() -> None:
    config = AppConfig(host="example.com", port=9000, debug=True, features=["a", "b"])

    data = config.to_dict()

    assert data == {
        "host": "example.com",
        "port": 9000,
        "debug": True,
        "features": ["a", "b"],
    }

    # data is caller-owned. Mutating it must not mutate the config instance.
    data["features"].append("mutated")  # type: ignore[union-attr]
    assert config.features == ("a", "b")


def test_from_dict_uses_cls_and_returns_subclass_instance() -> None:
    data = {"host": "dev.local", "port": 8100, "debug": True, "features": ["reload"]}

    config = DevelopmentConfig.from_dict(data)

    assert isinstance(config, DevelopmentConfig)
    assert config.host == "dev.local"
    assert config.port == 8100
    assert config.debug is True
    assert config.features == ("reload",)


def test_with_overrides_preserves_runtime_subclass_type() -> None:
    prod = ProductionConfig()

    changed = prod.with_overrides(port=8080, features=["blue-green"])

    assert isinstance(changed, ProductionConfig)
    assert changed.host == "0.0.0.0"
    assert changed.port == 8080
    assert changed.debug is False
    assert changed.features == ("blue-green",)

    # with_overrides returns a new object instead of mutating the original.
    assert prod.port == 80
    assert prod.features == ()

