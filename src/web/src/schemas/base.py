from dataclasses import dataclass
from datetime import datetime

from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class MatchSchema(JsonSchemaMixin):
    """Information about a singular match"""

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
