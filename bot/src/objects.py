from dataclasses import dataclass
import logging
from typing import Optional

from src.irc import WaifuMessage

logger = logging.getLogger(__name__)


@dataclass
class Match:
    tier: str
    match_format: str

    status: str = "open"
    fighter_red: Optional[str] = None
    fighter_blue: Optional[str] = None
    streak_red: Optional[int] = None
    streak_blue: Optional[int] = None
    bet_red: Optional[int] = None
    bet_blue: Optional[int] = None
    winner: Optional[str] = None
    colour: Optional[str] = None

    def update(self, waifu_message: WaifuMessage) -> bool:
        if waifu_message.message_type == "win" and self.status == "open":
            logger.warning("Somehow missed the locked bet step.")
            return False

        if waifu_message.message_type == "locked":
            self.fighter_red = waifu_message.fighter_red
            self.fighter_blue = waifu_message.fighter_blue
            self.bet_red = waifu_message.bet_red
            self.bet_blue = waifu_message.bet_blue
            self.streak_red = waifu_message.streak_red
            self.streak_blue = waifu_message.streak_blue
            self.status = "locked"
        else:
            self.winner = waifu_message.winner
            self.colour = waifu_message.colour
        return True
