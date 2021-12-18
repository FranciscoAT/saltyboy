from datetime import datetime, timedelta
import logging
import os

from src.database import Database
from src.irc import TwitchBot
from src.objects import Match

logger = logging.getLogger(__name__)

FAIL_HOURS = 6


def run() -> None:
    username = _get_environment_variable("USERNAME")
    oauth_token = _get_environment_variable("OAUTH_TOKEN")

    salty_db = Database(_get_environment_variable("DATABASE_PATH"))
    irc_bot = TwitchBot(username, oauth_token)

    last_write = datetime.utcnow()
    current_match = None
    for message in irc_bot.listen():
        if message.message_type == "open":
            logger.info(
                "New match. %s vs %s. Tier: %s.",
                message.fighter_red,
                message.fighter_blue,
                message.tier,
            )
            current_match = Match(tier=message.tier, match_format=message.match_format)  # type: ignore
        elif current_match:
            successful_update = current_match.update(message)
            if successful_update:
                if message.message_type == "locked":
                    logger.info(
                        "Bets locked. %s ($%s). %s ($%s)",
                        message.fighter_red,
                        message.bet_red,
                        message.fighter_blue,
                        message.bet_blue,
                    )
                else:
                    last_write = datetime.utcnow()
                    logger.info("Winner: %s", message.winner)
                    try:
                        salty_db.new_match(current_match)
                    except ValueError:
                        logger.error(
                            "Failed to log current match. %s",
                            current_match,
                            exc_info=True,
                        )

        if datetime.utcnow() - last_write > timedelta(hours=FAIL_HOURS):
            # TODO: This might not be the right place to quit
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
