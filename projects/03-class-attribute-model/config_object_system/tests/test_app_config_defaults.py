from __future__ import annotations

from config_object_system import AppConfig, DevelopmentConfig, ProductionConfig


def test_app_config_uses_class_attribute_defaults() -> None:
    config = AppConfig()

    assert config.host == "127.0.0.1"
    assert config.port == 8000
    assert config.debug is False
    assert config.features == ()


def test_constructor_overrides_do_not_modify_class_defaults() -> None:
    config = AppConfig(
        host="example.com",
        port=9000,
        debug=True,
        features=["metrics", "tracing"],
    )

    assert config.host == "example.com"
    assert config.port == 9000
    assert config.debug is True
    assert config.features == ("metrics", "tracing")

    # Class attributes are defaults on the class object, not per-instance state.
    assert AppConfig.default_host == "127.0.0.1"
    assert AppConfig.default_port == 8000
    assert AppConfig.default_debug is False
    assert AppConfig.default_features == ()


def test_features_are_not_shared_between_instances() -> None:
    first = AppConfig(features=["metrics"])
    second = AppConfig(features=["tracing"])

    assert first.features == ("metrics",)
    assert second.features == ("tracing",)


def test_subclass_defaults_come_from_class_attribute_lookup() -> None:
    dev = DevelopmentConfig()
    prod = ProductionConfig()

    assert dev.host == "127.0.0.1"
    assert dev.port == 8000
    assert dev.debug is True
    assert dev.features == ("reload",)

    assert prod.host == "0.0.0.0"
    assert prod.port == 80
    assert prod.debug is False
    assert prod.features == ()

