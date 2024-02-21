import logging
import os
from dataclasses import asdict

from src.database import Database
from src.irc import TwitchBot
from src.objects import (
    LockedBetMessage,
    Match,
    MatchFormat,
    OpenBetExhibitionMessage,
    OpenBetMessage,
    WinMessage,
)

logger = logging.getLogger(__name__)


def run() -> None:
    twitch_username = os.environ["TWITCH_USERNAME"]
    twitch_oauth_token = os.environ["TWITCH_OAUTH_TOKEN"]

    postgres_db = os.environ["POSTGRES_DB"]
    postgres_user = os.environ["POSTGRES_USER"]
    postgres_password = os.environ["POSTGRES_PASSWORD"]
    postgres_host = os.environ["POSTGRES_HOST"]
    postgres_port = int(os.environ["POSTGRES_PORT"])

    salty_db = Database(
        dbname=postgres_db,
        user=postgres_user,
        password=postgres_password,
        host=postgres_host,
        port=postgres_port,
    )

    irc_bot = TwitchBot(twitch_username, twitch_oauth_token)

    current_match: Match | None = None
    for message in irc_bot.listen():
        if isinstance(message, OpenBetMessage):
            logger.info(
                "New match. %s VS. %s. Tier: %s. Format: %s.",
                message.fighter_red_name,
                message.fighter_blue_name,
                message.tier,
                message.match_format.value,
            )
            salty_db.update_current_match(**asdict(message))

            if message.match_format != MatchFormat.EXHIBITION:
                current_match = Match(message)
            else:
                current_match = None
        elif isinstance(message, OpenBetExhibitionMessage):
            logger.info(
                "New match. %s VS. %s. Format: exhibition",
                message.fighter_red_name,
                message.fighter_blue_name,
            )
            salty_db.update_current_match(
                **asdict(message), match_format=MatchFormat.EXHIBITION
            )
            current_match = None
        elif current_match:
            if isinstance(message, LockedBetMessage):
                if current_match.update_locked(message) is True:
                    logger.info(
                        "Bets locked. %s ($%s). %s ($%s).",
                        message.fighter_red_name,
                        message.bet_red,
                        message.fighter_blue_name,
                        message.bet_blue,
                    )
            elif isinstance(message, WinMessage):
                if current_match.update_winner(message) is True:
                    logger.info("Winner: %s.", message.winner_name)
                    salty_db.record_match(current_match)
