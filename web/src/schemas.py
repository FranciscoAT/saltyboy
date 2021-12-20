from typing import Dict

from marshmallow import Schema, ValidationError, fields, validates_schema
from marshmallow.validate import Range


class GetFighterSchema(Schema):
    fighter_id = fields.Int(data_key="id", validate=Range(min=0))
    fighter_name = fields.Str(data_key="name")

    @validates_schema(skip_on_field_errors=True)
    def validate_one_of(self, data: Dict, **_) -> None:
        if data.get("fighter_id") is not None and data.get("fighter_name") is not None:
            raise ValidationError("Expecting either `name` or `id` and not both.")
        if data.get("fighter_id") is None and not data.get("fighter_name"):
            raise ValidationError("Expecting at least one of `name` or `id`.")


class AnalyzeMatchSchema(Schema):
    fighter_red = fields.Nested(GetFighterSchema, required=True)
    fighter_blue = fields.Nested(GetFighterSchema, required=True)
