from __future__ import annotations

from protocol_recordset import RecordSet


def test_constructor_copies_input_records() -> None:
    source = [{"name": "Ada", "score": 100}]

    recordset = RecordSet(source)

    # source[0] is caller-owned. Mutating it after construction must not change
    # the RecordSet's internal state.
    source[0]["score"] = 0

    assert recordset[0] == {"name": "Ada", "score": 100}


def test_iteration_returns_record_copies() -> None:
    recordset = RecordSet([{"name": "Ada", "score": 100}])

    yielded = next(iter(recordset))

    # yielded is the object produced by __iter__. It should be a copy.
    yielded["score"] = 0

    assert recordset[0] == {"name": "Ada", "score": 100}


def test_each_iter_call_returns_fresh_iterator() -> None:
    recordset = RecordSet(
        [
            {"name": "Ada", "score": 100},
            {"name": "Lin", "score": 88},
        ]
    )

    first_pass = list(recordset)
    second_pass = list(recordset)

    assert first_pass == second_pass == [
        {"name": "Ada", "score": 100},
        {"name": "Lin", "score": 88},
    ]

    assert first_pass[0] is not second_pass[0]

