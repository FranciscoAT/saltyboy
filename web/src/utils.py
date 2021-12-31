from dataclasses import fields
from sqlite3 import Row
from typing import Any, Dict, Optional, Type, TypeVar

T = TypeVar("T")


def row_to_dataclass(
    row: Row, dc: Type[T], overwrite_fields: Optional[Dict[str, Any]] = None
) -> T:
    overwrite_fields = overwrite_fields or {}
    row_args = {}
    for dc_field in fields(dc):
        if dc_field.name in overwrite_fields:
            row_args[dc_field.name] = overwrite_fields[dc_field.name]
        else:
            row_args[dc_field.name] = (
                row[dc_field.name] if dc_field.name in row.keys() else None
            )

    return dc(**row_args)
