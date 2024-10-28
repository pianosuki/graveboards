from typing import Any
from datetime import datetime

from sqlalchemy.sql import any_, all_
from sqlalchemy.sql.sqltypes import Integer, Float, String, Boolean, DateTime, Text
from sqlalchemy.sql.elements import ColumnClause, literal, BinaryExpression
from sqlalchemy.sql.functions import func
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.exceptions import TypeValidationError
from app.search.enums import FilterOperator


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


def get_filter_condition(filter_operator: FilterOperator, target: InstrumentedAttribute | ColumnClause, value: Any, is_aggregated: bool = False) -> BinaryExpression:
    if not is_aggregated:
        condition = filter_operator.value(target, value)
    else:
        match filter_operator:
            case FilterOperator.EQ:
                condition = literal(value) == any_(func.array_agg(target))
            case FilterOperator.NEQ:
                condition = literal(value) != all_(func.array_agg(target))
            case FilterOperator.GT:
                condition = any_(func.array_agg(target)) > literal(value)
            case FilterOperator.LT:
                condition = any_(func.array_agg(target)) < literal(value)
            case FilterOperator.GTE:
                condition = any_(func.array_agg(target)) >= literal(value)
            case FilterOperator.LTE:
                condition = any_(func.array_agg(target)) <= literal(value)
            case _:
                raise ValueError(f"Invalid flter_operator: {filter_operator}")

    return condition
