from __future__ import annotations

import pytest

from mini_pipeline import PipelineError, SourceOpenError, open_records


def test_source_open_error_is_project_error() -> None:
    assert issubclass(SourceOpenError, PipelineError)


def test_open_records_yields_lines_and_closes_file(tmp_path) -> None:
    source = tmp_path / "scores.txt"
    source.write_text("Ada,100\nGuido,95\n", encoding="utf-8")

    with open_records(source) as lines:
        # lines should be the resource returned by __enter__.
        # For the intended solution, it is the open file object.
        assert lines.closed is False
        assert next(lines) == "Ada,100\n"
        captured_lines_object = lines

    assert captured_lines_object.closed is True


def test_open_records_missing_file_preserves_cause(tmp_path) -> None:
    missing = tmp_path / "missing.txt"

    with pytest.raises(SourceOpenError) as exc_info:
        with open_records(missing):
            pass

    error = exc_info.value

    # __cause__ is set by `raise SourceOpenError(...) from exc`.
    assert isinstance(error.__cause__, OSError)
    assert str(missing) in str(error)

