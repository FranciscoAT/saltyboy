from dataclasses import dataclass


@dataclass
class OpenBetMessage:
    fighter_red: str
    fighter_blue: str
    tier: str
    match_format: str


@dataclass
class OpenBetExhibitionMessage:
    fighter_red: str
    fighter_blue: str


@dataclass
class LockedBetMessage:
    fighter_red: str
    fighter_blue: str
    bet_red: int
    bet_blue: int
    streak_red: int
    streak_blue: int


@dataclass
class WinMessage:
    winner: str
    colour: str
