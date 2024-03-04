from datetime import datetime
from enum import StrEnum, unique
from typing import Optional

from pydantic import BaseModel, Field, field_serializer


# === Base ===
class PaginationResponse(BaseModel):
    page: int = Field(description="Current page number.")
    page_size: int = Field(description="Current page size.")
    count: int = Field(description="Total number of results.")


class PaginationQuery(BaseModel):
    page: int = Field(default=0, description="Page to view.", ge=0)
    page_size: int = Field(
        default=100, description="Number of results per page.", ge=1, le=100
    )


class IdPath(BaseModel):
    id_: int = Field(description="ID of the resource to get.", ge=1)


@unique
class Tier(StrEnum):
    X = "X"
    S = "S"
    A = "A"
    B = "B"
    P = "P"


@unique
class RecordedMatchFormat(StrEnum):
    MATCHMAKING = "matchmaking"
    TOURNAMENT = "tournament"


@unique
class AllMatchFormat(StrEnum):
    MATCHMAKING = "matchmaking"
    TOURNAMENT = "tournament"
    EXHIBITION = "exhibition"


@unique
class Colour(StrEnum):
    RED = "Red"
    BLUE = "Blue"


# === Fighter ===
class ListFighterQuery(PaginationQuery):
    name: str = Field(
        default=None,
        description="Filter fighters by the name of the fighter. Case sensitive. Note, fighter's names are unique, therefore this is likely to only return one result.",
    )
    tier: Tier = Field(
        default=None, description="Filter fighters by the current tier of fighter."
    )
    prev_tier: Tier = Field(
        default=None,
        description="Filter fighters by the previously recorded fighter tier.",
    )
    elo__gte: int = Field(
        default=None,
        description="Filter fighters who's current ELO is greater than or equal to than this number.",
    )
    elo__lt: int = Field(
        default=None,
        description="Filter fighters who's current ELO is less than this number.",
    )
    tier_elo__gte: int = Field(
        default=None,
        description="Filter fighters who's current tier ELO is greater than or equal to than this number.",
    )
    tier_elo__lt: int = Field(
        default=None,
        description="Filter fighters who's current tier ELO is less than this number.",
    )


class FighterModel(BaseModel):
    id: int = Field(description="ID of the fighter.")
    name: str = Field(description="Name of the fighter. Case sensitive.")
    tier: str = Field(description="Current tier of the fighter.")
    prev_tier: str = Field(description="Previously recorded tier of the fighter.")
    elo: int = Field(description="Current ELO of the fighter.")
    tier_elo: int = Field(description="Current tier ELO of the fighter.")
    best_streak: int = Field(description="Best recorded winning streak of the fighter.")
    created_time: datetime = Field(description="Time the fighter was first recorded.")
    last_updated: datetime = Field(
        description="Time the fighter last fought in a match."
    )

    @field_serializer("created_time", "last_updated")
    @classmethod
    def serialize_datetime(cls, v: datetime, *args) -> str:
        return v.isoformat()


class ListFighterResponse(PaginationResponse):
    results: list[FighterModel] = Field(description="Filtered fighters.")


# === Matches ===
class ListMatchQuery(PaginationQuery):
    fighter_red: int = Field(
        default=None,
        description="Filter matches where the Red fighter was a specific fighter by ID.",
        ge=1,
    )
    fighter_blue: int = Field(
        default=None,
        description="Filter matches where the Blue fighter was a specific fighter by ID.",
        ge=1,
    )
    fighter: int = Field(
        default=None,
        description="Filter matches where the Red or Blue fighter is a specific fighter by ID.",
        ge=1,
    )
    winner: int = Field(
        default=None,
        description="Filter matches where the winning fighter was a specific fighter by ID.",
        ge=1,
    )
    bet_red__gte: int = Field(
        default=None,
        description="Filter matches where the amount bet on Red is greater than or equal to this number.",
    )
    bet_red__lt: int = Field(
        default=None,
        description="Filter matches where the amount bet on Red is less than this number.",
    )
    bet_blue__gte: int = Field(
        default=None,
        description="Filter matches where the amount bet on Blue is greater than or equal to this number.",
    )
    bet_blue__lt: int = Field(
        default=None,
        description="Filter matches where the amount bet on Blue is less than this number.",
    )
    bet__gte: int = Field(
        default=None,
        description="Filter matches where the bet on Blue or Red is greater than or equal to this number.",
    )
    bet__lt: int = Field(
        default=None,
        description="Filter matches where the bet on Blue or Red is less than this number.",
    )
    streak_red__gte: int = Field(
        default=None,
        description="Filter matches where the current winning streak on Red at time of the match is greater than or equal to this number.",
    )
    streak_red__lt: int = Field(
        default=None,
        description="Filter matches where the current winning streak on Red at time of the match is less than this number.",
    )
    streak_blue__gte: int = Field(
        default=None,
        description="Filter matches where the current winning streak on Blue at time of the match is greater than or equal to this number.",
    )
    streak_blue__lt: int = Field(
        default=None,
        description="Filter matches where the current winning streak on Blue at time of the match is less than this number.",
    )
    streak__gte: int = Field(
        default=None,
        description="Filter matches where the best streak on Red or Blue is greater than or equal to this number.",
    )
    streak__lt: int = Field(
        default=None,
        description="Filter matches where the best streak on Red or Blue is less than or equal to this number.",
    )
    tier: Tier = Field(
        default=None, description="Filter matches by the tier of the match. "
    )
    match_format: RecordedMatchFormat = Field(
        default=None,
        description="Filter matches by the match format. Note: SaltyBoy does not record Exhibition matches.",
    )
    colour: Colour = Field(
        default=None, description="Filter matches by the winning colour."
    )


class MatchModel(BaseModel):
    id: int = Field(description="ID of the match.")
    date: datetime = Field(description="Date of the match.")
    fighter_red: int = Field(description="ID of the Red fighter.")
    fighter_blue: int = Field(description="ID of the Blue fighter.")
    winner: int = Field(description="ID of the winning fighter.")
    bet_red: int = Field(description="Amount bet on the Red fighter.")
    bet_blue: int = Field(description="Amount bet on the Blue fighter.")
    streak_red: int = Field(
        description="Current winning streak of the Red fighter at time of the match."
    )
    streak_blue: int = Field(
        description="Current winning streak fo the Blue fighter at time of the match."
    )
    tier: Tier = Field(description="Tier of the match.")
    match_format: RecordedMatchFormat = Field(
        description="Format of the match. Note: SaltyBoy does not record Exhibition matches."
    )
    colour: Colour = Field(description="Winning colour.")

    @field_serializer("date")
    @classmethod
    def serialize_datetime(cls, v: datetime, *args) -> str:
        return v.isoformat()


class ListMatchResponse(PaginationResponse):
    results: list[MatchModel] = Field(description="Filtered matches.")


# === Current Match ===
class ExtendedFighterModel(FighterModel):
    matches: list[MatchModel] = Field(
        description="All matches the fighter has fought in."
    )


class CurrentMatchMatchModel(BaseModel):
    fighter_blue: Optional[str] = Field(description="Name of the Blue fighter.")
    fighter_red: Optional[str] = Field(description="Name of the Red fighter.")
    match_format: Optional[AllMatchFormat] = Field(description="Match format.")
    tier: Optional[Tier] = Field(description="Tier of the match.")
    updated_at: Optional[datetime] = Field(
        description="When the current match was updated."
    )

    @field_serializer("updated_at")
    @classmethod
    def serialize_datetime(cls, v: datetime | None, *args) -> str | None:
        if v is not None:
            return v.isoformat()

        return None


class CurrentMatchInfoResponse(CurrentMatchMatchModel):
    fighter_blue_info: Optional[ExtendedFighterModel] = Field(
        default=None, description="Detailed information about the Blue fighter."
    )
    fighter_red_info: Optional[ExtendedFighterModel] = Field(
        default=None, description="Detailed information about the Red fighter."
    )
