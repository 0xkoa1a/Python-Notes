"""Domain exceptions for the mini pipeline project."""

from __future__ import annotations


class PipelineError(Exception):
    """Base class for errors raised by this project."""


class SourceOpenError(PipelineError):
    """Raised when an input source cannot be opened.

    TODO: Use this exception in open_records(path). Preserve the original
    OSError with `raise SourceOpenError(...) from exc`.
    """


class RecordParseError(PipelineError):
    """Raised when one input line cannot be parsed as a record.

    TODO: Store line_number and raw_line on the exception object.

    line_number should be the 1-based input line number.
    raw_line should be the exact line object received from the input iterator.
    __cause__ should point at the lower-level parsing error when one exists.
    """
    def __init__(self, *, line_number: int, raw_line: str) -> None:
        self.line_number = line_number
        self.raw_line = raw_line

        message = (
            f"Failed to parse record at line {line_number}: "
            f"{raw_line.rstrip()!r}"
        )
        super().__init__(message)