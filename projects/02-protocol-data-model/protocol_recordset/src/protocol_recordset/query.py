"""Small query objects for RecordSet filtering."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TypeAlias

Record: TypeAlias = Mapping[str, object]


@dataclass(frozen=True)
class FieldPredicate:
    """Callable predicate produced by comparing a Field with a value."""

    field_name: str
    operator: str
    expected: object

    def __call__(self, record: Record) -> bool:
        """Return whether record matches this predicate.

        TODO: Implement the calling protocol.

        record is the mapping object supplied by RecordSet.filter or user code.
        Calling this predicate should read record[self.field_name] and compare it
        with self.expected according to self.operator.
        """

        raise NotImplementedError("Implement FieldPredicate.__call__")


@dataclass(frozen=True)
class Field:
    """A lightweight object representing a field name in a record."""

    name: str

    def __eq__(self, expected: object) -> FieldPredicate:  # type: ignore[override]
        """Build an equality predicate instead of comparing Field objects.

        TODO: Return a FieldPredicate.

        The expression where("name") == "Ada" calls this method. The returned
        object should be callable later with one record.
        """

        raise NotImplementedError("Implement Field.__eq__")

    def __ne__(self, expected: object) -> FieldPredicate:  # type: ignore[override]
        """Build a not-equal predicate."""

        raise NotImplementedError("Implement Field.__ne__")

    def __lt__(self, expected: object) -> FieldPredicate:
        """Build a less-than predicate."""

        raise NotImplementedError("Implement Field.__lt__")

    def __le__(self, expected: object) -> FieldPredicate:
        """Build a less-than-or-equal predicate."""

        raise NotImplementedError("Implement Field.__le__")

    def __gt__(self, expected: object) -> FieldPredicate:
        """Build a greater-than predicate."""

        raise NotImplementedError("Implement Field.__gt__")

    def __ge__(self, expected: object) -> FieldPredicate:
        """Build a greater-than-or-equal predicate."""

        raise NotImplementedError("Implement Field.__ge__")


def where(field_name: str) -> Field:
    """Return a Field object for building predicates.

    TODO: Validate field_name if needed, then return Field(field_name).

    The returned Field object is not itself the final predicate. It is an object
    whose comparison methods create callable FieldPredicate objects.
    """

    raise NotImplementedError("Implement where(field_name)")

