from __future__ import annotations

import pytest

from protocol_recordset import RecordSet


def sample_records() -> list[dict[str, object]]:
    return [
        {"name": "Ada", "score": 100},
        {"name": "Lin", "score": 88},
        {"name": "Guido", "score": 95},
    ]


def test_len_bool_and_repr() -> None:
    recordset = RecordSet(sample_records())

    assert len(recordset) == 3
    assert bool(recordset) is True
    assert bool(RecordSet([])) is False

    text = repr(recordset)

    # repr(recordset) should expose enough structure for debugging failures.
    assert "RecordSet" in text
    assert "3" in text
    assert "name" in text
    assert "score" in text


def test_integer_and_negative_index_return_record_copies() -> None:
    recordset = RecordSet(sample_records())

    first = recordset[0]
    last = recordset[-1]

    assert first == {"name": "Ada", "score": 100}
    assert last == {"name": "Guido", "score": 95}

    # first is a copy returned by __getitem__, not the internal dictionary.
    first["score"] = 0
    assert recordset[0] == {"name": "Ada", "score": 100}


def test_slice_returns_new_recordset() -> None:
    recordset = RecordSet(sample_records())

    sliced = recordset[1:]

    assert isinstance(sliced, RecordSet)
    assert len(sliced) == 2
    assert sliced["name"] == ["Lin", "Guido"]


def test_string_key_returns_column_values() -> None:
    recordset = RecordSet(sample_records())

    assert recordset["name"] == ["Ada", "Lin", "Guido"]
    assert recordset["score"] == [100, 88, 95]


def test_missing_field_raises_key_error() -> None:
    recordset = RecordSet(sample_records())

    with pytest.raises(KeyError):
        _ = recordset["missing"]


def test_invalid_key_type_raises_type_error() -> None:
    recordset = RecordSet(sample_records())

    with pytest.raises(TypeError):
        _ = recordset[1.5]  # type: ignore[index]


def test_membership_uses_whole_records() -> None:
    recordset = RecordSet(sample_records())

    assert {"name": "Ada", "score": 100} in recordset
    assert {"name": "Ada", "score": 0} not in recordset

    # Membership is not scalar search inside fields.
    assert "Ada" not in recordset

