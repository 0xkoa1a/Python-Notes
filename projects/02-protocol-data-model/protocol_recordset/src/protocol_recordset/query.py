"""Small query objects for RecordSet filtering."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TypeAlias
import operator

Compare: TypeAlias = Callable[[object, object], bool]
Record: TypeAlias = Mapping[str, object]


@dataclass(frozen=True)
class FieldPredicate:
    """Callable predicate produced by comparing a Field with a value."""

    field_name: str
    operator: Compare
    expected: object

    def __call__(self, record: Record) -> bool:
        """Return whether record matches this predicate.

        TODO: Implement the calling protocol.

        record is the mapping object supplied by RecordSet.filter or user code.
        Calling this predicate should read record[self.field_name] and compare it
        with self.expected according to self.operator.
        """

        return self.operator(record[self.field_name], self.expected)


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

        return FieldPredicate(self.name, operator.eq, expected)

    def __ne__(self, expected: object) -> FieldPredicate:  # type: ignore[override]
        """Build a not-equal predicate."""

        return FieldPredicate(self.name, operator.ne, expected)

    def __lt__(self, expected: object) -> FieldPredicate:
        """Build a less-than predicate."""

        return FieldPredicate(self.name, operator.lt, expected)

    def __le__(self, expected: object) -> FieldPredicate:
        """Build a less-than-or-equal predicate."""

        return FieldPredicate(self.name, operator.le, expected)

    def __gt__(self, expected: object) -> FieldPredicate:
        """Build a greater-than predicate."""

        return FieldPredicate(self.name, operator.gt, expected)

    def __ge__(self, expected: object) -> FieldPredicate:
        """Build a greater-than-or-equal predicate."""

        return FieldPredicate(self.name, operator.ge, expected)


def where(field_name: str) -> Field:
    """Return a Field object for building predicates.

    TODO: Validate field_name if needed, then return Field(field_name).

    The returned Field object is not itself the final predicate. It is an object
    whose comparison methods create callable FieldPredicate objects.
    """

    return Field(field_name)

