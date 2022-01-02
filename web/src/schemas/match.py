from dataclasses import dataclass

from dataclasses_jsonschema import JsonSchemaMixin
from src.schemas.fighters import FighterInfoSchema


@dataclass
class CurrentMatchSchema(JsonSchemaMixin):
    """Information pertaining to the current ongoing match"""
    fighter_blue: str
    fighter_red: str
    match_format: str
    tier: str
    fighter_red_info: FighterInfoSchema
    fighter_blue_info: FighterInfoSchema
