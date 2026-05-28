"""RecordSet container for practicing Python data-model protocols."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import TypeAlias, overload

Record: TypeAlias = dict[str, object]
ReadonlyRecord: TypeAlias = Mapping[str, object]


class RecordSet:
    """A small immutable-style container of dictionary records."""

    # TODO: Keep RecordSet explicitly unhashable after implementing __eq__.
    # hash(recordset) should raise TypeError because records are dictionary-like
    # data, and value equality should not imply a stable hash here.
    __hash__ = None

    def __init__(self, records: Iterable[ReadonlyRecord] = ()) -> None:
        """Create a RecordSet from an iterable of mapping records.

        TODO: Copy each input record into internal storage.

        records may be a list, tuple, generator, or any iterable. Each element is
        a mapping object. The RecordSet should not keep aliases to caller-owned
        dictionaries.
        """

        raise NotImplementedError("Implement RecordSet.__init__")

    def __repr__(self) -> str:
        """Return a debugging representation.

        TODO: Include class name, record count, and field names.

        repr(recordset) calls this method. The result is for developers reading
        logs or test failures, so it should expose useful structure.
        """

        raise NotImplementedError("Implement RecordSet.__repr__")

    def __len__(self) -> int:
        """Return the number of records.

        TODO: Implement the length protocol.

        len(recordset) calls this method. bool(recordset) can also use it when
        __bool__ is not defined.
        """

        raise NotImplementedError("Implement RecordSet.__len__")

    @overload
    def __getitem__(self, key: int) -> Record:
        ...

    @overload
    def __getitem__(self, key: slice) -> "RecordSet":
        ...

    @overload
    def __getitem__(self, key: str) -> list[object]:
        ...

    def __getitem__(self, key: int | slice | str) -> Record | "RecordSet" | list[object]:
        """Return a row, a sliced RecordSet, or a field column.

        TODO: Implement the container protocol.

        recordset[key] calls this method. key is an object supplied by Python:
        int for row access, slice for slicing, and str for column access.
        """

        raise NotImplementedError("Implement RecordSet.__getitem__")

    def __iter__(self) -> Iterator[Record]:
        """Iterate over record copies.

        TODO: Return a fresh iterator each time.

        for record in recordset calls iter(recordset), which calls this method.
        Each yielded record should be a copy, not the internal dictionary.
        """

        raise NotImplementedError("Implement RecordSet.__iter__")

    def __contains__(self, item: object) -> bool:
        """Return whether item is one whole record in this RecordSet.

        TODO: Implement membership testing.

        item in recordset calls this method. Membership is about whole records,
        not about whether a scalar appears in any field.
        """

        raise NotImplementedError("Implement RecordSet.__contains__")

    def filter(self, predicate: Callable[[ReadonlyRecord], bool]) -> "RecordSet":
        """Return a new RecordSet containing records accepted by predicate."""

        raise NotImplementedError("Implement RecordSet.filter")

    def __call__(self, predicate: Callable[[ReadonlyRecord], bool]) -> "RecordSet":
        """Filter this RecordSet by calling it like a function.

        TODO: Delegate to filter(predicate).

        recordset(predicate) calls this method. predicate is a callable object
        that receives one record mapping and returns a truth value.
        """

        raise NotImplementedError("Implement RecordSet.__call__")

    def __eq__(self, other: object) -> bool:
        """Compare RecordSet objects by record content.

        TODO: Return NotImplemented for unrelated types.

        Python may give the other operand a chance to compare when this method
        returns NotImplemented. That is different from simply returning False.
        """

        raise NotImplementedError("Implement RecordSet.__eq__")

