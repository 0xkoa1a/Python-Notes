"""Input resource management for the mini pipeline project."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, TextIO

from .errors import SourceOpenError


@contextmanager
def open_records(path: str | Path) -> Iterator[TextIO]:
    """Open a text file and yield an iterable line object.

    TODO: Implement this as a context manager.

    The object yielded from this generator becomes the value bound after `as`:

        with open_records(path) as lines:
            ...

    In that example, lines should be the open file object. If opening fails,
    raise SourceOpenError from the original OSError so __cause__ is preserved.
    """

    raise NotImplementedError("Implement open_records(path)")

    # This unreachable yield keeps the skeleton shaped like a generator-based
    # context manager. Your implementation should yield the opened file object.
    yield
