from __future__ import annotations

from config_object_system import AppConfig, DataclassAppConfig, dump_config


class DuckConfig:
    def __init__(self) -> None:
        self.exported = {"host": "duck.local", "port": 1234}

    def to_dict(self) -> dict[str, object]:
        return dict(self.exported)


def test_dump_config_accepts_hand_written_config() -> None:
    config = AppConfig(host="example.com", port=9000, features=["metrics"])

    assert dump_config(config) == {
        "host": "example.com",
        "port": 9000,
        "debug": False,
        "features": ["metrics"],
    }


def test_dump_config_accepts_dataclass_config() -> None:
    config = DataclassAppConfig(host="dc.local", features=["a"])

    assert dump_config(config) == {
        "host": "dc.local",
        "port": 8000,
        "debug": False,
        "features": ["a"],
    }


def test_dump_config_accepts_duck_object_without_inheritance() -> None:
    duck = DuckConfig()

    exported = dump_config(duck)

    assert exported == {"host": "duck.local", "port": 1234}

    # dump_config should return caller-owned data, not an alias to duck.exported.
    exported["host"] = "mutated"
    assert duck.exported["host"] == "duck.local"

