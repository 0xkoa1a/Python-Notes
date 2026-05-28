"""RecordSet container for practicing Python data-model protocols."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import TypeAlias, overload
from copy import deepcopy

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

        self._dict = [dict(deepcopy(r)) for r in records]

    def __repr__(self) -> str:
        """Return a debugging representation.

        TODO: Include class name, record count, and field names.

        repr(recordset) calls this method. The result is for developers reading
        logs or test failures, so it should expose useful structure.
        """

        return f"RecordSet: {self._dict.__repr__()}, len={self.__len__()}"

    def __len__(self) -> int:
        """Return the number of records.

        TODO: Implement the length protocol.

        len(recordset) calls this method. bool(recordset) can also use it when
        __bool__ is not defined.
        """

        return self._dict.__len__()

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
        if isinstance(key, int):
            return dict(self._dict[key])

        if isinstance(key, slice):
            return RecordSet(self._dict[key])

        if isinstance(key, str):
            return [record[key] for record in self._dict]

        raise TypeError(f"Unsupported key type: {type(key).__name__}")

    def __iter__(self) -> Iterator[Record]:
        """Iterate over record copies.

        TODO: Return a fresh iterator each time.

        for record in recordset calls iter(recordset), which calls this method.
        Each yielded record should be a copy, not the internal dictionary.
        """

        return deepcopy(self._dict).__iter__()

    def __contains__(self, item: object) -> bool:
        """Return whether item is one whole record in this RecordSet.

        TODO: Implement membership testing.

        item in recordset calls this method. Membership is about whole records,
        not about whether a scalar appears in any field.
        """

        return self._dict.__contains__(item)

    def filter(self, predicate: Callable[[ReadonlyRecord], bool]) -> "RecordSet":
        """Return a new RecordSet containing records accepted by predicate."""

        return RecordSet(filter(predicate, self._dict))

    def __call__(self, predicate: Callable[[ReadonlyRecord], bool]) -> "RecordSet":
        """Filter this RecordSet by calling it like a function.

        TODO: Delegate to filter(predicate).

        recordset(predicate) calls this method. predicate is a callable object
        that receives one record mapping and returns a truth value.
        """

        return self.filter(predicate)

    def __eq__(self, other: object) -> bool:
        """Compare RecordSet objects by record content.

        TODO: Return NotImplemented for unrelated types.

        Python may give the other operand a chance to compare when this method
        returns NotImplemented. That is different from simply returning False.
        """

        if not isinstance(other, RecordSet):
            return NotImplemented
        return self._dict.__eq__(other._dict)
