import logging
import os
import time
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from multiprocessing import Process

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

    def run(self) -> None:
        bot_logger.info("Bot started")

        database = Database(
            dbname=self.postgres_db,
            user=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
        )

        irc_bot = TwitchBot(self.twitch_username, self.twitch_oauth_token)

        current_match: Match | None = None
        for message in irc_bot.listen():
            if message is None:
                bot_logger.debug("Updating heartbeat.")
                database.update_bot_heartbeat()
                continue

            if isinstance(message, OpenBetMessage):
                bot_logger.info(
                    "New match. %s VS. %s. Tier: %s. Format: %s.",
                    message.fighter_red_name,
                    message.fighter_blue_name,
                    message.tier,
                    message.match_format.value,
                )
                database.update_current_match(**asdict(message))

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
                database.update_current_match(
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
                        database.record_match(current_match)


def run() -> None:
    watchdog_logger.info("Running bot watchdog")
    bot_process = new_bot_process()
    last_restart_time = datetime.now(timezone.utc)
    last_verified_healthcheck_time = datetime.now(timezone.utc)
    watchdog_log_attenuator = 0

    database = Database(
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
    )

    while True:
        now = datetime.now(timezone.utc)
        last_bot_heartbeat_time = database.get_bot_heartbeat()
        restart_bot = False

        # We want to trigger a restart in the following situations:
        # 1. Bot's heartbeat is over 2 minutes ago. It should check in every minute.
        # 2. If Bot's heartbeat is none and the last verified_healthcheck_time is over
        #    5 minutes ago force a restart.
        # 3. The bot process is somehow not alive.
        if last_bot_heartbeat_time is None:
            if last_verified_healthcheck_time < now - timedelta(minutes=5):
                watchdog_logger.warning(
                    "Bot heartbeat hasn't been set for 5 minutes. Triggering restart."
                )
                restart_bot = True
        elif bot_process.is_alive() is False:
            watchdog_logger.warning(
                "Bot process is somehow not alive. Triggering restart."
            )
            restart_bot = True
        elif last_bot_heartbeat_time < now - timedelta(minutes=2):
            watchdog_logger.warning(
                "Bot process heartbeat is over two minutes old. Triggering restart."
            )
            restart_bot = True
        else:
            # Services are healthy.
            last_verified_healthcheck_time = now

        # Do not restart the bot if it was restarted within the past 5 minutes. To give
        # it time to spin up and have a chance to get healthy.
        if restart_bot is True:
            if last_restart_time < now - timedelta(minutes=5):
                watchdog_logger.info("Restarting bot process...")
                close_bot_process(bot_process)
                bot_process = new_bot_process()
                last_restart_time = now
                last_verified_healthcheck_time = now
            else:
                watchdog_logger.info(
                    "Bot process was last restarted less than 5 minutes ago. "
                    "Refusing to restart."
                )

        # Sleep for a minute, watch dog does not need to run that often.
        time.sleep(60)

        watchdog_logger.debug(
            "Last bot heartbeat: %s", last_bot_heartbeat_time.isoformat()
        )

        # Log watchdog still alive every 5 cycles
        watchdog_log_attenuator += 1
        if watchdog_log_attenuator % 5 == 0:
            watchdog_log_attenuator = 0
            if restart_bot is False:
                watchdog_logger.info(
                    "Services are healthy. Last bot heartbeat: %s",
                    last_bot_heartbeat_time.isoformat(),
                )


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


def close_bot_process(bot_process: BotProcess) -> None:
    watchdog_logger.info("Terminating bot process...")
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
    watchdog_logger.info("Bot process terminated.")
