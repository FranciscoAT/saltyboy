from datetime import datetime, timedelta
import logging
import os

from src.database import Database
from src.irc import TwitchBot
from src.objects.match import Match
from src.objects.waifu import LockedBetMessage, OpenBetMessage, WinMessage

logger = logging.getLogger(__name__)

FAIL_HOURS = 6


def run() -> None:
    username = _get_environment_variable("USERNAME")
    oauth_token = _get_environment_variable("OAUTH_TOKEN")

    salty_db = Database(_get_environment_variable("DATABASE_PATH"))
    irc_bot = TwitchBot(username, oauth_token)

    current_match = None
    for message in irc_bot.listen():
        if isinstance(message, OpenBetMessage):
            logger.info(
                "New match. %s VS. %s. Tier: %s. Format: %s.",
                message.fighter_red,
                message.fighter_blue,
                message.tier,
                message.match_format,
            )
            salty_db.update_current_match(
                fighter_red=message.fighter_red,
                fighter_blue=message.fighter_blue,
                tier=message.tier,
                match_format=message.match_format,
            )
            current_match = Match(message)
        elif current_match:
            if isinstance(message, LockedBetMessage):
                success = current_match.update_locked(message)
                if success:
                    logger.info(
                        "Bets locked. %s ($%s). %s ($%s).",
                        message.fighter_red,
                        message.bet_red,
                        message.fighter_blue,
                        message.bet_blue,
                    )
            elif isinstance(message, WinMessage):
                success = current_match.update_winner(message)
                if success:
                    logger.info("Winner: %s.", message.winner)
                    try:
                        salty_db.new_match(current_match)
                    except ValueError:
                        logger.error(
                            "Failed to log current match. %s",
                            current_match.__dict__,
                            exc_info=True,
                        )


def _get_environment_variable(env_var_name: str) -> str:
    env_var = os.environ[env_var_name]
    if not env_var:
        raise ValueError(f"Missing environment variable {env_var_name}")
    return env_var
