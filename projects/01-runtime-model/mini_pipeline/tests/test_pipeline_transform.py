from __future__ import annotations

from collections.abc import Iterator, Mapping

from mini_pipeline import collect_summary, filter_records, map_records


class TrackingRecords:
    def __init__(self, records: list[dict[str, object]]) -> None:
        # _records is an iterator; each next() call consumes exactly one record object.
        self._records = iter(records)
        self.pulled = 0

    def __iter__(self) -> "TrackingRecords":
        return self

    def __next__(self) -> dict[str, object]:
        self.pulled += 1
        return next(self._records)


def test_filter_records_is_lazy() -> None:
    source = TrackingRecords(
        [
            {"name": "Ada", "score": 100},
            {"name": "Lin", "score": 88},
        ]
    )
    calls: list[str] = []

    def high_score(record: Mapping[str, object]) -> bool:
        # calls records when predicate is executed, not when filter_records is created.
        calls.append(str(record["name"]))
        return int(record["score"]) >= 90

    filtered = filter_records(source, high_score)

    assert source.pulled == 0
    assert calls == []

    assert next(filtered) == {"name": "Ada", "score": 100}
    assert source.pulled == 1
    assert calls == ["Ada"]


def test_filter_records_works_with_closure_predicate() -> None:
    records = [
        {"name": "Ada", "score": 100},
        {"name": "Lin", "score": 88},
        {"name": "Guido", "score": 95},
    ]
    thresholds = [90, 98]
    predicates = []

    for threshold in thresholds:
        # threshold=threshold captures the current object in this function's defaults.
        # Without it, both closures would share the same loop variable binding.
        predicates.append(lambda record, threshold=threshold: int(record["score"]) >= threshold)

    at_least_90 = list(filter_records(records, predicates[0]))
    at_least_98 = list(filter_records(records, predicates[1]))

    assert [record["name"] for record in at_least_90] == ["Ada", "Guido"]
    assert [record["name"] for record in at_least_98] == ["Ada"]


def test_map_records_is_lazy_and_can_create_new_objects() -> None:
    source = TrackingRecords([{"name": "Ada", "score": 100}])
    calls: list[str] = []

    def add_curve(record: Mapping[str, object]) -> dict[str, object]:
        calls.append(str(record["name"]))
        return {**record, "score": int(record["score"]) + 5}

    mapped = map_records(source, add_curve)

    assert source.pulled == 0
    assert calls == []

    assert next(mapped) == {"name": "Ada", "score": 105}
    assert source.pulled == 1
    assert calls == ["Ada"]


def test_collect_summary_consumes_records() -> None:
    def records() -> Iterator[dict[str, object]]:
        yield {"name": "Ada", "score": 100}
        yield {"name": "Lin", "score": 88}
        yield {"name": "Guido", "score": 95}

    assert collect_summary(records()) == {
        "count": 3,
        "total": 283,
        "average": 283 / 3,
        "names": ["Ada", "Lin", "Guido"],
    }


def test_collect_summary_handles_empty_input() -> None:
    assert collect_summary([]) == {
        "count": 0,
        "total": 0,
        "average": None,
        "names": [],
    }


def test_collect_summary_does_not_share_mutable_state_between_calls() -> None:
    first = collect_summary([{"name": "Ada", "score": 100}])
    second = collect_summary([{"name": "Lin", "score": 88}])

    # names must be a fresh list for each call, not a mutable default reused across calls.
    assert first["names"] == ["Ada"]
    assert second["names"] == ["Lin"]
    assert first["names"] is not second["names"]

