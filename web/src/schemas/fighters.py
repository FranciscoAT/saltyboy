from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from marshmallow import Schema, ValidationError, fields, validates_schema
from marshmallow.validate import Range


class GetFighterSchema(Schema):
    fighter_id = fields.Int(data_key="id", validate=Range(min=0))
    fighter_name = fields.Str(data_key="name")

    @validates_schema(skip_on_field_errors=True)
    def validate_one_of(self, data: Dict, **_) -> None:
        if data.get("fighter_id") is not None and data.get("fighter_name") is not None:
            raise ValidationError("Expecting either `name` or `id` and not both in query parameters.")
        if data.get("fighter_id") is None and not data.get("fighter_name"):
            raise ValidationError("Expecting at least one of `name` or `id` in query parameters.")


@dataclass
class MatchSchema:
    bet_blue: int
    bet_red: int
    date: datetime
    fighter_blue: int
    fighter_red: int
    id: int
    match_format: str
    streak_blue: int
    streak_red: int
    tier: str
    winner: int


@dataclass
class FighterStatsSchema:
    win_rate: float
    average_bet: float
    total_matches: int


@dataclass
class FighterInfoSchema:
    id: int
    best_streak: int
    created_time: datetime
    last_updated: datetime
    name: str
    tier: str
    stats: FighterStatsSchema
    matches: List[MatchSchema]
