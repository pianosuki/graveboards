from datetime import datetime

from marshmallow import fields, ValidationError

__all__ = [
    "CustomDateTime"
]


class CustomDateTime(fields.DateTime):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, datetime):
            return value

        try:
            return super()._deserialize(value, attr, data, **kwargs)

        except ValidationError as e:
            raise ValidationError(f"Invalid datetime format: {e}")
