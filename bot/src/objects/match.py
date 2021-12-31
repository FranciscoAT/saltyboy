import logging
from typing import Optional, Union

from src.objects.waifu import LockedBetMessage, OpenBetMessage, WinMessage

logger = logging.getLogger(__name__)


class Match:
    def __init__(self, waifu_message: OpenBetMessage) -> None:
        self.status = "open"
        self.tier = waifu_message.tier
        self.fighter_red = waifu_message.fighter_red
        self.fighter_blue = waifu_message.fighter_blue
        self.match_format = waifu_message.match_format

        self.streak_red: Optional[int] = None
        self.streak_blue: Optional[int] = None
        self.bet_red: Optional[int] = None
        self.bet_blue: Optional[int] = None
        self.winner: Optional[str] = None
        self.colour: Optional[str] = None

    def update_locked(self, waifu_message: LockedBetMessage) -> bool:
        if self.status != "open":
            logger.warning(
                "Could not update current match. Attempted to update to locked and "
                "match status is not open. Waifu message: %s. Current match: %s.",
                waifu_message,
                self.__dict__,
            )
            return False

        if (
            waifu_message.fighter_red != self.fighter_red
            or waifu_message.fighter_blue != self.fighter_blue
        ):
            logger.warning(
                "Could not update current match. Data mismatch. "
                "Waifu message: %s. Current match: %s",
                waifu_message,
                self.__dict__,
            )
            return False

        self.status = "locked"
        self.bet_red = waifu_message.bet_red
        self.bet_blue = waifu_message.bet_blue
        self.streak_red = waifu_message.streak_red
        self.streak_blue = waifu_message.streak_blue
        return True

    def update_winner(self, waifu_message: WinMessage) -> bool:
        if self.status != "locked":
            logger.warning(
                "Could not update current match. Attempted to update to locked and "
                "match status is not open. Waifu message: %s. Current match: %s.",
                waifu_message,
                self.__dict__,
            )
            return False

        if waifu_message.winner not in [self.fighter_red, self.fighter_blue]:
            logger.warning(
                "Could not update current match. Data mismatch. "
                "Waifu message: %s. Current match: %s",
                waifu_message,
                self.__dict__,
            )
            return False

        self.status = "finished"
        self.winner = waifu_message.winner
        self.colour = waifu_message.colour
        return True
