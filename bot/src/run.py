from datetime import datetime, timedelta
import logging
import os
from typing import Optional

from src.irc import TwitchBot, WaifuMessage

logger = logging.getLogger(__name__)

FAIL_HOURS = 6


class Match:
    def __init__(self, open_bet: WaifuMessage) -> None:
        logger.info(
            "New match. %s vs %s. Tier: %s.",
            open_bet.fighter_a,
            open_bet.fighter_b,
            open_bet.tier,
        )
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
            logger.info(
                "Bets locked. %s ($%s). %s ($%s)",
                waifu_message.fighter_a,
                waifu_message.fighter_a_bet,
                waifu_message.fighter_b,
                waifu_message.fighter_b_bet,
            )
            self.fighter_a = waifu_message.fighter_a
            self.fighter_b = waifu_message.fighter_b
            self.fighter_a_bet = waifu_message.fighter_a_bet
            self.fighter_b_bet = waifu_message.fighter_b_bet
            self.fighter_a_streak = waifu_message.fighter_a_streak
            self.fighter_b_streak = waifu_message.fighter_b_streak
            self.status = "locked"
            return False

        self.winner = waifu_message.winner
        self.colour = waifu_message.colour
        logger.info("Winner: %s", waifu_message.winner)
        return True


def run() -> None:
    username = _get_environment_variable("USERNAME")
    oauth_token = _get_environment_variable("OAUTH_TOKEN")

    irc_bot = TwitchBot(username, oauth_token)

    last_write = datetime.utcnow()
    current_match = None
    for message in irc_bot.listen():
        if message.message_type == "open":
            current_match = Match(message)
        elif current_match:
            write_to_db = current_match.update(message)
            if write_to_db:
                last_write = datetime.utcnow()
        elif datetime.utcnow() - last_write > timedelta(hours=FAIL_HOURS):
            logger.critical(
                "Something is wrong. No new matches written for over %s hours",
                FAIL_HOURS,
            )
            quit(1)


def _get_environment_variable(env_var_name: str) -> str:
    env_var = os.environ[env_var_name]
    if not env_var:
        raise ValueError(f"Missing environment variable {env_var_name}")
    return env_var
