"""Lazy data-flow functions for the mini pipeline project."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import TypeAlias
from .errors import RecordParseError

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
    for line_num, line in enumerate(lines, start=1):
        try:
            raw_line = line

            line = line.strip()
            if not line or line.startswith("#"):
                continue

            name, score = map(str.strip, line.split(",", maxsplit=1))
            score = int(score)
            if not name:
                raise ValueError("Name cannot be empty")
            
            yield {"name": name, "score": score}

        except (ValueError, IndexError) as e:
            raise RecordParseError(line_number=line_num, raw_line=raw_line) from e

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
    for record in records:
        if not predicate(record):
            continue
        yield record

def map_records(
    records: Iterable[Mapping[str, object]],
    transform: Callable[[Mapping[str, object]], Mapping[str, object]],
) -> Iterator[Mapping[str, object]]:
    """Apply transform to each record lazily.

    TODO: Return a lazy iterator. transform should be called only when the
    returned iterator is consumed.
    """
    for record in records:
        yield transform(record)


def collect_summary(records: Iterable[Mapping[str, object]]) -> Summary:
    """Consume records and return count, total, average, and names.

    TODO: Create fresh local state inside each call. Do not use a mutable
    default parameter to store names or running totals.
    """

    count = 0
    total = 0
    names = []
    for record in records:
        name, score = record["name"], record["score"]
        count = count + 1
        total = total + score
        names.append(name)
    return {
        "count": count,
        "total": total,
        "average": total / count if count != 0 else None,
        "names": names        
    }
