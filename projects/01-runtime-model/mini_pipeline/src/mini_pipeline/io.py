"""Input resource management for the mini pipeline project."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterator

from .errors import SourceOpenError


@contextmanager
def open_records(path: str | Path) -> Iterator[str]:
    """Open a text file and yield an iterable line object.

    TODO: Implement this as a context manager.

    The object yielded from this generator becomes the value bound after `as`:

        with open_records(path) as lines:
            ...

    In that example, lines should be the open file object. If opening fails,
    raise SourceOpenError from the original OSError so __cause__ is preserved.
    """
    
    try:
        lines = open(path, "r", encoding="utf-8")
    except OSError as e:
        raise SourceOpenError(f"Could not open file: {path}") from e
    
    try:
        yield lines
    finally:
        lines.close()