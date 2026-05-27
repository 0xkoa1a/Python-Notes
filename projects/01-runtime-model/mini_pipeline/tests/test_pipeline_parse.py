from __future__ import annotations

import pytest

from mini_pipeline import RecordParseError, parse_records


class TrackingLines:
    def __init__(self, lines: list[str]) -> None:
        # _lines is a private iterator object; next() advances its internal state.
        self._lines = iter(lines)
        self.pulled = 0

    def __iter__(self) -> "TrackingLines":
        return self

    def __next__(self) -> str:
        self.pulled += 1
        return next(self._lines)


def test_parse_records_is_lazy() -> None:
    lines = TrackingLines(["Ada,100\n", "Guido,95\n"])

    records = parse_records(lines)

    # records is the returned iterator object. Creating it must not consume lines.
    assert lines.pulled == 0

    assert next(records) == {"name": "Ada", "score": 100}
    assert lines.pulled == 1


def test_parse_records_skips_blank_lines_and_comments() -> None:
    lines = [
        "\n",
        "   \n",
        "# comment\n",
        "  # another comment after indentation\n",
        "Ada,100\n",
        " Guido , 95 \n",
    ]

    assert list(parse_records(lines)) == [
        {"name": "Ada", "score": 100},
        {"name": "Guido", "score": 95},
    ]


def test_parse_records_reports_invalid_score_with_context() -> None:
    records = parse_records(["Ada,100\n", "Guido,not-a-number\n"])

    assert next(records) == {"name": "Ada", "score": 100}

    with pytest.raises(RecordParseError) as exc_info:
        next(records)

    error = exc_info.value

    # line_number is the 1-based position in the original input stream.
    assert error.line_number == 2
    assert error.raw_line == "Guido,not-a-number\n"

    # __cause__ should preserve the lower-level score parsing failure.
    assert isinstance(error.__cause__, ValueError)
    assert "not-a-number" in str(error)


def test_parse_records_reports_missing_field_with_context() -> None:
    records = parse_records(["Ada,100\n", "broken-line\n"])

    assert next(records) == {"name": "Ada", "score": 100}

    with pytest.raises(RecordParseError) as exc_info:
        next(records)

    error = exc_info.value
    assert error.line_number == 2
    assert error.raw_line == "broken-line\n"
    assert isinstance(error.__cause__, ValueError)


def test_parse_records_rejects_empty_name() -> None:
    records = parse_records([",100\n"])

    with pytest.raises(RecordParseError) as exc_info:
        next(records)

    error = exc_info.value
    assert error.line_number == 1
    assert error.raw_line == ",100\n"

