from __future__ import annotations

import pytest

from protocol_recordset import RecordSet


def test_recordsets_compare_by_ordered_record_content() -> None:
    left = RecordSet(
        [
            {"name": "Ada", "score": 100},
            {"name": "Lin", "score": 88},
        ]
    )
    right = RecordSet(
        [
            {"name": "Ada", "score": 100},
            {"name": "Lin", "score": 88},
        ]
    )
    different_order = RecordSet(
        [
            {"name": "Lin", "score": 88},
            {"name": "Ada", "score": 100},
        ]
    )

    assert left == right
    assert left != different_order


def test_eq_returns_not_implemented_for_unrelated_types() -> None:
    recordset = RecordSet([{"name": "Ada", "score": 100}])

    # Directly calling __eq__ lets us inspect the protocol response.
    # The == operator would turn NotImplemented into a final False result.
    assert RecordSet.__eq__(recordset, object()) is NotImplemented


def test_recordset_is_unhashable() -> None:
    recordset = RecordSet([{"name": "Ada", "score": 100}])

    with pytest.raises(TypeError):
        hash(recordset)

