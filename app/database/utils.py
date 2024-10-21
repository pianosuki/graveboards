from typing import Any
from datetime import datetime

from sqlalchemy.sql.sqltypes import Integer, Float, String, Boolean, DateTime, Text
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.exceptions import TypeValidationError


def validate_column_value(column: InstrumentedAttribute, value: Any):
    column_type = type(column.type)

    if value is None and not column.nullable:
        raise ValueError(f"Field '{column.name}' does not accept null values")
    elif value is None and column.nullable:
        return

    if column_type is Integer:
        if not isinstance(value, int):
            raise TypeValidationError(type(value), int)
    elif column_type is Float:
        if not isinstance(value, (float, int)):
            raise TypeValidationError(type(value), float, int)
    elif column_type is String:
        if not isinstance(value, str):
            raise TypeValidationError(type(value), str)
    elif column_type is Boolean:
        if not isinstance(value, bool):
            raise TypeValidationError(type(value), bool)
    elif column_type is DateTime:
        if not isinstance(value, (str, datetime)):
            raise TypeValidationError(type(value), str, datetime)
    elif column_type is Text:
        if not isinstance(value, str):
            raise TypeValidationError(type(value), str)
