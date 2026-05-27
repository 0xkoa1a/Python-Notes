"""Lazy data-flow functions for the mini pipeline project."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import TypeAlias

Record: TypeAlias = dict[str, object]
Summary: TypeAlias = dict[str, object]


def parse_records(lines: Iterable[str]) -> Iterator[Record]:
    """Parse text lines into record dictionaries.

    TODO: Return a lazy iterator. Calling this function should not consume lines.

    Each yielded record should look like:

        {"name": "Ada", "score": 100}

    When parsing fails, raise RecordParseError with line_number and raw_line,
    and use `raise ... from exc` to preserve the underlying cause.
    """

    raise NotImplementedError("Implement parse_records(lines)")

    # This unreachable yield keeps the skeleton shaped like a generator.
    # Your implementation should yield one parsed record at a time.
    yield {}


def filter_records(
    records: Iterable[Mapping[str, object]],
    predicate: Callable[[Mapping[str, object]], bool],
) -> Iterator[Mapping[str, object]]:
    """Yield only records accepted by predicate.

    TODO: Return a lazy iterator. predicate should be called only when the
    returned iterator is consumed.

    predicate is a function object supplied by the caller. It may close over
    names from an outer scope, so this function should simply call it for each
    record instead of trying to inspect or cache its result.
    """

    raise NotImplementedError("Implement filter_records(records, predicate)")

    # This unreachable yield keeps the skeleton shaped like a lazy iterator.
    # Your implementation should yield records only when predicate(record) is true.
    yield {}


def map_records(
    records: Iterable[Mapping[str, object]],
    transform: Callable[[Mapping[str, object]], Mapping[str, object]],
) -> Iterator[Mapping[str, object]]:
    """Apply transform to each record lazily.

    TODO: Return a lazy iterator. transform should be called only when the
    returned iterator is consumed.
    """

    raise NotImplementedError("Implement map_records(records, transform)")

    # This unreachable yield keeps the skeleton shaped like a lazy iterator.
    # Your implementation should yield transform(record) for each input record.
    yield {}


def collect_summary(records: Iterable[Mapping[str, object]]) -> Summary:
    """Consume records and return count, total, average, and names.

    TODO: Create fresh local state inside each call. Do not use a mutable
    default parameter to store names or running totals.
    """

    raise NotImplementedError("Implement collect_summary(records)")
