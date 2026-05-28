from __future__ import annotations

from collections.abc import Mapping

from protocol_recordset import Field, RecordSet, where


def sample_recordset() -> RecordSet:
    return RecordSet(
        [
            {"name": "Ada", "score": 100},
            {"name": "Lin", "score": 88},
            {"name": "Guido", "score": 95},
        ]
    )


def test_filter_returns_new_recordset_without_mutating_original() -> None:
    recordset = sample_recordset()

    def high_score(record: Mapping[str, object]) -> bool:
        # record is a mapping supplied by RecordSet.filter.
        return int(record["score"]) >= 90

    filtered = recordset.filter(high_score)

    assert isinstance(filtered, RecordSet)
    assert filtered["name"] == ["Ada", "Guido"]
    assert recordset["name"] == ["Ada", "Lin", "Guido"]


def test_call_protocol_delegates_to_filtering() -> None:
    recordset = sample_recordset()

    filtered = recordset(lambda record: str(record["name"]).startswith("A"))

    assert isinstance(filtered, RecordSet)
    assert filtered["name"] == ["Ada"]


def test_where_returns_field_object() -> None:
    field = where("score")

    assert isinstance(field, Field)
    assert field.name == "score"


def test_where_greater_equal_builds_callable_predicate() -> None:
    predicate = where("score") >= 90

    # predicate is a callable object produced by Field.__ge__, not a bool yet.
    assert callable(predicate)
    assert predicate({"name": "Ada", "score": 100}) is True
    assert predicate({"name": "Lin", "score": 88}) is False


def test_where_equal_builds_callable_predicate() -> None:
    predicate = where("name") == "Ada"

    assert callable(predicate)
    assert predicate({"name": "Ada", "score": 100}) is True
    assert predicate({"name": "Lin", "score": 88}) is False


def test_where_predicate_can_filter_recordset() -> None:
    recordset = sample_recordset()

    filtered = recordset(where("score") >= 90)

    assert filtered["name"] == ["Ada", "Guido"]

