import logging
from typing import Optional

from src.irc import WaifuMessage

logger = logging.getLogger(__name__)


class Match:
    def __init__(self, open_bet: WaifuMessage) -> None:
        self.status = "open"
        self.tier = open_bet.tier
        self.fighter_a: Optional[str] = None
        self.fighter_b: Optional[str] = None
        self.fighter_a_streak: Optional[int] = None
        self.fighter_b_streak: Optional[int] = None
        self.fighter_a_bet: Optional[int] = None
        self.fighter_b_bet: Optional[int] = None
        self.winner: Optional[str] = None
        self.colour: Optional[str] = None

    def update(self, waifu_message: WaifuMessage) -> bool:
        if waifu_message.message_type == "win" and self.status == "open":
            logger.warning("Somehow missed the locked bet step.")
            return False

        if waifu_message.message_type == "locked":

            self.fighter_a = waifu_message.fighter_a
            self.fighter_b = waifu_message.fighter_b
            self.fighter_a_bet = waifu_message.fighter_a_bet
            self.fighter_b_bet = waifu_message.fighter_b_bet
            self.fighter_a_streak = waifu_message.fighter_a_streak
            self.fighter_b_streak = waifu_message.fighter_b_streak
            self.status = "locked"
        else:
            self.winner = waifu_message.winner
            self.colour = waifu_message.colour
        return True
