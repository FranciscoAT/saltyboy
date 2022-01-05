from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class GetFighterQuerySchema:
    fighter_id: Optional[Any] = None
    fighter_name: Optional[str] = None

    def __post_init__(self) -> None:
        if self.fighter_id is None and self.fighter_name is None:
            raise ValueError("Expecting one of `name` or `id` in query parameters.")

        if self.fighter_id is not None and self.fighter_name is not None:
            raise ValueError(
                "Expecting either `name` or `id` in query parameters, and not both."
            )

        if self.fighter_id is not None:
            try:
                self.fighter_id = int(self.fighter_id)
            except ValueError:
                raise ValueError("Could not deserialize `id` into an integer.")

            if self.fighter_id < 0:
                raise ValueError("`id` needs to be a value greater than 0. ")


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


@dataclass
class FighterStatsSchema(JsonSchemaMixin):
    """Stats about a given fighter"""
    win_rate: float
    average_bet: float
    total_matches: int


@dataclass
class FighterInfoSchema(JsonSchemaMixin):
    """Information about a given fighter"""
    id: int
    best_streak: int
    created_time: datetime
    last_updated: datetime
    name: str
    tier: str
    prev_tier: str
    stats: FighterStatsSchema
    matches: List[MatchSchema]
    elo: int
    tier_elo: int
