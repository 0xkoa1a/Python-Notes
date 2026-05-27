"""Optional command-line entrypoint for manual experimentation."""

from __future__ import annotations

from pathlib import Path

from .io import open_records
from .pipeline import collect_summary, parse_records


def main(path: str) -> dict[str, object]:
    """Run the minimal pipeline and return its summary.

    TODO: You may expand this into a real CLI later. For this chapter project,
    the tests focus on the runtime-model functions, not argument parsing.
    """

    # path_obj is a Path object representing the user-provided filesystem path.
    path_obj = Path(path)

    # lines is the object returned by the context manager's __enter__ method.
    # In the intended implementation it should be an open file object.
    with open_records(path_obj) as lines:
        # records is a generator-like object; it should parse lines lazily.
        records = parse_records(lines)
        return collect_summary(records)

