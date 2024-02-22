import logging
from dataclasses import dataclass
from enum import Enum, unique

logger = logging.getLogger(__name__)


@unique
class MatchFormat(Enum):
    TOURNAMENT = "tournament"
    MATCHMAKING = "matchmaking"
    EXHIBITION = "exhibition"


# === Waif4u Messages ===


@dataclass
class OpenBetMessage:
    fighter_red_name: str
    fighter_blue_name: str
    tier: str
    match_format: MatchFormat


@dataclass
class OpenBetExhibitionMessage:
    fighter_red_name: str
    fighter_blue_name: str


@dataclass
class LockedBetMessage:
    fighter_red_name: str
    fighter_blue_name: str
    bet_red: int
    bet_blue: int
    streak_red: int
    streak_blue: int


@dataclass
class WinMessage:
    winner_name: str
    colour: str


# === Match ===
@unique
class MatchStatus(Enum):
    OPEN = "open"
    LOCKED = "locked"
    DONE = "done"


class Match:
    def __init__(self, waifu_message: OpenBetMessage) -> None:
        self.status = MatchStatus.OPEN
        self.tier = waifu_message.tier
        self.fighter_red_name = waifu_message.fighter_red_name
        self.fighter_blue_name = waifu_message.fighter_blue_name
        self.match_format = waifu_message.match_format

        self.streak_red: int | None = None
        self.streak_blue: int | None = None
        self.bet_red: int | None = None
        self.bet_blue: int | None = None
        self.winner: str | None = None
        self.colour: str | None = None

    def update_locked(self, waifu_message: LockedBetMessage) -> bool:
        if self.status != MatchStatus.OPEN:
            logger.warning(
                "Could not update current match. Attempted to update to locked and "
                "match status is not open. Waifu message: %s. Current match: %s.",
                waifu_message,
                self.__dict__,
            )
            return False

        if (
            waifu_message.fighter_red_name != self.fighter_red_name
            or waifu_message.fighter_blue_name != self.fighter_blue_name
        ):
            logger.warning(
                "Could not update current match. Data mismatch. Waifu message: %s. "
                "Current match: %s",
                waifu_message,
                self.__dict__,
            )
            return False

        self.status = MatchStatus.LOCKED
        self.bet_red = waifu_message.bet_red
        self.bet_blue = waifu_message.bet_blue
        self.streak_red = waifu_message.streak_red
        self.streak_blue = waifu_message.streak_blue
        return True

    def update_winner(self, waifu_message: WinMessage) -> bool:
        if self.status != MatchStatus.LOCKED:
            logger.warning(
                "Could not update current match. Attempted to update to locked and "
                "match status is not open. Waifu message: %s. Current match: %s.",
                waifu_message,
                self.__dict__,
            )
            return False

        if waifu_message.winner_name not in [
            self.fighter_red_name,
            self.fighter_blue_name,
        ]:
            logger.warning(
                "Could not update current match. Data mismatch. Waifu message: %s. "
                "Current match: %s",
                waifu_message,
                self.__dict__,
            )
            return False

        self.status = MatchStatus.DONE
        self.winner = waifu_message.winner_name
        self.colour = waifu_message.colour
        return True
