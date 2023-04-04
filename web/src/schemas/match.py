from dataclasses import dataclass

from dataclasses_jsonschema import JsonSchemaMixin

from src.schemas.base import MatchSchema
from src.schemas.fighters import FighterInfoSchema, MinimalFighterInfoSchema


@dataclass
class CurrentMatchSchema(JsonSchemaMixin):
    """Information pertaining to the current ongoing match"""

    fighter_blue: str
    fighter_red: str
    match_format: str
    tier: str
    fighter_red_info: FighterInfoSchema
    fighter_blue_info: FighterInfoSchema


@dataclass
class EnhancedMatchSchema(MatchSchema):
    """Information about a specific match"""

    fighter_blue_info: MinimalFighterInfoSchema
    fighter_red_info: MinimalFighterInfoSchema
