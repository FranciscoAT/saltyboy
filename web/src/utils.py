from dataclasses import fields
from sqlite3 import Row
from typing import Any, Type, TypeVar

T = TypeVar("T")


def row_to_dataclass(
    row: Row, dataclass_: Type[T], overwrite_fields: dict[str, Any] | None = None
) -> T:
    overwrite_fields = overwrite_fields or {}
    row_args = {}
    for dc_field in fields(dataclass_):  # type: ignore
        if dc_field.name in overwrite_fields:
            row_args[dc_field.name] = overwrite_fields[dc_field.name]
        else:
            row_args[dc_field.name] = (
                row[dc_field.name] if dc_field.name in row.keys() else None
            )

    return dataclass_(**row_args)
