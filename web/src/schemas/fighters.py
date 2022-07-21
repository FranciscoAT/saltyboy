from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from dataclasses_jsonschema import JsonSchemaMixin
from src.schemas.base import MatchSchema


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
class FighterStatsSchema(JsonSchemaMixin):
    """Stats about a given fighter"""

    win_rate: float
    average_bet: float
    total_matches: int


@dataclass
class MinimalFighterInfoSchema(JsonSchemaMixin):
    """Minimal information about a fighter"""

    id: int
    best_streak: int
    created_time: datetime
    last_updated: datetime
    name: str
    tier: str
    prev_tier: str
    elo: int
    tier_elo: int


@dataclass
class FighterInfoSchema(MinimalFighterInfoSchema):
    """Enhanced information about a given fighter"""

    stats: FighterStatsSchema
    matches: list[MatchSchema]
