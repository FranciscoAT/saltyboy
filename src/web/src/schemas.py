from datetime import datetime

from pydantic import BaseModel, field_validator


# === Base ===
def validate_tier_helper(tier: str) -> str:
    upper_tier = tier.upper()
    if upper_tier not in ["X", "S", "A", "B", "P"]:
        raise ValueError("Tier is not valid, must be one of: X, S, A, B, or P.")
    return upper_tier


class PaginationResponse(BaseModel):
    page: int
    page_size: int
    count: int


class PaginationQuery(BaseModel):
    page: int = 0
    page_size: int = 100

    @field_validator("page")
    @classmethod
    def page_validator(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Must not be less than 0.")
        return v

    @field_validator("page_size")
    @classmethod
    def page_size_validator(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Must not be less than 1.")
        if v > 100:
            raise ValueError("Must not be more than 100.")
        return v


# === Fighter ===
class ListFighterQuery(PaginationQuery):
    name: str | None = None
    tier: str | None = None
    prev_tier: str | None = None
    elo__gte: int | None = None
    elo__lt: int | None = None
    tier_elo__gte: int | None = None
    tier_elo__lt: int | None = None

    @field_validator("tier", "prev_tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        return validate_tier_helper(v)


class FighterModel(BaseModel):
    id: int
    name: str
    tier: str
    prev_tier: str
    elo: int
    tier_elo: int
    best_streak: int
    created_time: datetime
    last_updated: datetime


class ListFighterResponse(PaginationResponse):
    results: list[FighterModel]


# === Matches ===
class ListMatchQuery(PaginationQuery):
    fighter_red: int | None = None
    fighter_blue: int | None = None
    winner: int | None = None
    bet_red__gte: int | None = None
    bet_red__lt: int | None = None
    bet_blue__gte: int | None = None
    bet_blue__lt: int | None = None
    streak_red__gte: int | None = None
    streak_red__lt: int | None = None
    streak_blue__gte: int | None = None
    streak_blue__lt: int | None = None
    tier: str | None = None
    match_format: str | None = None
    colour: str | None = None

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        return validate_tier_helper(v)

    @field_validator("match_format")
    @classmethod
    def validate_match_format(cls, v: str) -> str:
        match_format_lower = v.lower()
        if match_format_lower not in ["matchmaking", "tournament"]:
            raise ValueError("match_format must be one of: matchmaking, or tournament.")
        return match_format_lower

    @field_validator("colour")
    @classmethod
    def validate_colour(cls, v: str) -> str:
        capitalized_colour = v.lower().capitalize()
        if capitalized_colour not in ["Red", "Blue"]:
            raise ValueError("colour must be one of: Red, or Blue.")
        return capitalized_colour


class MatchModel(BaseModel):
    id: int
    fighter_red: int
    fighter_blue: int
    winner: int
    bet_red: int
    bet_blue: int
    streak_red: int
    streak_blue: int
    tier: str
    match_format: str
    colour: str


class ListMatchResponse(PaginationResponse):
    results: list[MatchModel]
