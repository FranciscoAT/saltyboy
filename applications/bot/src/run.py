import logging
import os
import time
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from multiprocessing import Process

import psycopg2.extras

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

bot_logger = logging.getLogger("bot")
watchdog_logger = logging.getLogger("watchdog")


class BotProcess(Process):
    def __init__(
        self,
        postgres_db: str,
        postgres_user: str,
        postgres_password: str,
        postgres_host: str,
        postgres_port: int,
        twitch_username: str,
        twitch_oauth_token: str,
    ) -> None:
        super().__init__(daemon=True)

        self.postgres_db = postgres_db
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password
        self.postgres_host = postgres_host
        self.postgres_port = postgres_port

        self.twitch_username = twitch_username
        self.twitch_oauth_token = twitch_oauth_token

        self.database: Database

    def run(self) -> None:
        bot_logger.info("Bot started")

        self.database = Database(
            dbname=self.postgres_db,
            user=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
        )

        irc_bot = TwitchBot(self.twitch_username, self.twitch_oauth_token)

        current_match: Match | None = None
        for message in irc_bot.listen():
            if isinstance(message, OpenBetMessage):
                bot_logger.info(
                    "New match. %s VS. %s. Tier: %s. Format: %s.",
                    message.fighter_red_name,
                    message.fighter_blue_name,
                    message.tier,
                    message.match_format.value,
                )
                self.database.update_current_match(**asdict(message))

                if message.match_format != MatchFormat.EXHIBITION:
                    current_match = Match(message)
                else:
                    current_match = None
            elif isinstance(message, OpenBetExhibitionMessage):
                bot_logger.info(
                    "New match. %s VS. %s. Format: exhibition",
                    message.fighter_red_name,
                    message.fighter_blue_name,
                )
                self.database.update_current_match(
                    **asdict(message), match_format=MatchFormat.EXHIBITION
                )
                current_match = None
            elif current_match:
                if isinstance(message, LockedBetMessage):
                    if current_match.update_locked(message) is True:
                        bot_logger.info(
                            "Bets locked. %s ($%s). %s ($%s).",
                            message.fighter_red_name,
                            message.bet_red,
                            message.fighter_blue_name,
                            message.bet_blue,
                        )
                elif isinstance(message, WinMessage):
                    if current_match.update_winner(message) is True:
                        bot_logger.info("Winner: %s.", message.winner_name)
                        self.database.record_match(current_match)

    def terminate(self) -> None:
        bot_logger.info("Closing bot process...")
        self.database.connection.close()
        super().terminate()


def run() -> None:
    watchdog_logger.info("Running bot watchdog")

    last_heartbeat_time = datetime.now(timezone.utc)
    last_restart_time = datetime.now(timezone.utc)
    current_bot_process = new_bot_process()
    current_match: psycopg2.extras.DictRow | None

    while True:
        now = datetime.now(timezone.utc)
        current_match = get_current_match()
        restart_bot = False

        # We want to trigger a restart in the following situations:
        # 1. Bot has not recorded an ongoing match and or the updated_at time is null,
        #    and the last successful heartbeat was over 10 minutes ago.
        # 2. The last time a match was updated was over 10 minutes ago.
        # 3. The bot process is somehow not alive.

        if current_match is None or current_match["updated_at"] is None:
            if last_heartbeat_time < now - timedelta(minutes=10):
                watchdog_logger.warning(
                    "Something is not right, triggering bot restart"
                )
                restart_bot = True
        elif current_match["updated_at"].replace(tzinfo=timezone.utc) < now - timedelta(
            minutes=10
        ):
            watchdog_logger.warning(
                "Current match has not been updated in a while bot socket "
                "likely disconnected from remote and hanging."
            )
            restart_bot = True
        elif current_bot_process.is_alive() is False:
            watchdog_logger.warning(
                "Current Bot Process is not alive! Triggering restart"
            )
            restart_bot = True
        else:
            watchdog_logger.info("Everything looks healthy.")
            last_heartbeat_time = datetime.now(timezone.utc)

        # Do not restart the bot if it was restarted within the past 10 minutes.
        # Otherwise, can lead to loop upon loop of forced restarts until the
        # bot has time to record a match.
        if restart_bot is True and last_restart_time < now - timedelta(minutes=10):
            close_bot_process(current_bot_process)
            current_bot_process = new_bot_process()
            last_heartbeat_time = datetime.now(timezone.utc)
            last_restart_time = datetime.now(timezone.utc)

        # Sleep for 5 minutes, watch dog does not need to run that often.
        time.sleep(60 * 5)


def new_bot_process() -> BotProcess:
    bot_process = BotProcess(
        os.environ["POSTGRES_DB"],
        os.environ["POSTGRES_USER"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        int(os.environ["POSTGRES_PORT"]),
        os.environ["TWITCH_USERNAME"],
        os.environ["TWITCH_OAUTH_TOKEN"],
    )
    bot_process.start()
    return bot_process


def get_current_match() -> psycopg2.extras.DictRow | None:
    database = Database(
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
    )
    current_match = database.get_current_match()
    database.connection.close()
    return current_match


def close_bot_process(bot_process: BotProcess) -> None:
    try:
        if bot_process.is_alive() is True:
            bot_process.terminate()
        # Give time for bot process to terminate
        time.sleep(10)
        # Release bot process resources
        bot_process.close()
    except Exception:
        watchdog_logger.warning("Failed to close the bot process.", exc_info=True)

    # Give time for the resources to be released
    time.sleep(10)
