import logging
import re
import ssl
import time
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from select import select
from socket import socket
from ssl import SSLSocket

from src.objects import (
    LockedBetMessage,
    MatchFormat,
    OpenBetExhibitionMessage,
    OpenBetMessage,
    WinMessage,
)

logger = logging.getLogger(__name__)

ReturnMessages = (
    OpenBetMessage | LockedBetMessage | WinMessage | OpenBetExhibitionMessage
)


class RemoteSocketDisconnect(Exception):
    """Generic exception instructing us to restart the connection"""


class TwitchBot:
    MAX_AUTH_ATTEMPTS = 5

    OPEN_BET_RE = re.compile(r"Bets are OPEN for (.+) vs (.+)!\s+\((.) Tier\)\s+.*")
    OPEN_BET_EXHIBITION_RE = re.compile(
        r"Bets are OPEN for (.+) vs (.+)!\s+\(.+\)\s+\(exhibitions\)\s+.*"
    )
    LOCKED_BET_RE = re.compile(
        r"Bets are locked. (.+) \((-?[0-9]+)\) - \$(([0-9]{1,3},)*[0-9]{1,3}), (.+) \((-?[0-9]+)\) - \$(([0-9]{1,3},)*[0-9]{1,3})"  # pylint: disable=line-too-long
    )
    WINNER_RE = re.compile(r"(.+) wins! Payouts to Team (Red|Blue)\..*")

    def __init__(self, twitch_username: str, twitch_oauth_token: str) -> None:
        self.username = twitch_username
        self.oauth_token = twitch_oauth_token
        self.ssl_sock: SSLSocket
        self.last_read = datetime.now(timezone.utc)

        self.connect()

    def connect(self) -> None:
        num_auth_attempts = 0
        connected = False
        while not connected:
            try:
                self._initialize_socket()
                connected = True
            except TimeoutError:
                num_auth_attempts += 1
                if num_auth_attempts > self.MAX_AUTH_ATTEMPTS:
                    raise

        # Join channel
        logger.info("Joining channel saltybet...")
        self._send("JOIN #saltybet")
        joined = False
        joined_start = datetime.utcnow()
        while not joined:
            for message in self._receive(expect_disconnect=False):
                logger.info(message)
                if "End of /NAMES list" in message:
                    logger.info("Joined successfully!")
                    joined = True
                    break
                if datetime.utcnow() - joined_start > timedelta(seconds=5):
                    raise TimeoutError(
                        "Took longer than 5 seconds to join saltybet channel."
                    )

    def listen(self) -> Iterator[ReturnMessages]:
        while True:
            if self.last_read - datetime.now(timezone.utc) > timedelta(minutes=10):
                # Force a reconnection
                self.connect()

            try:
                for message in self._receive():
                    if "PING :tmi.twitch.tv" == message:
                        logger.info("Received a PING, sending PONG.")
                        self._send("PONG :tmi.twitch.tv")
                    if not message.startswith(":waifu4u"):
                        continue
                    try:
                        return_message = self.parse_message(
                            message.split("#saltybet :")[1]
                        )
                        if return_message:
                            logger.debug(message)
                            yield return_message
                    except Exception:  # pylint: disable=broad-except
                        logger.error("Something went wrong", exc_info=True)
                    time.sleep(5)
            except RemoteSocketDisconnect:
                logger.info("Remote socket was likely disconnected. Reconnecting.")
                self.connect()

    @classmethod
    def parse_message(cls, message: str) -> ReturnMessages | None:
        logger.debug(message)
        waifu_message: ReturnMessages | None = None
        if match := cls.OPEN_BET_RE.match(message):
            if "(matchmaking)" in message:
                match_format = MatchFormat.MATCHMAKING
            elif "tournament bracket" in message:
                match_format = MatchFormat.TOURNAMENT
            else:
                match_format = MatchFormat.EXHIBITION

            waifu_message = OpenBetMessage(
                fighter_red_name=match.group(1),
                fighter_blue_name=match.group(2),
                tier=match.group(3),
                match_format=match_format,
            )
        elif match := cls.LOCKED_BET_RE.match(message):
            waifu_message = LockedBetMessage(
                fighter_red_name=match.group(1),
                streak_red=int(match.group(2)),
                bet_red=int(match.group(3).replace(",", "")),
                fighter_blue_name=match.group(5),
                streak_blue=int(match.group(6)),
                bet_blue=int(match.group(7).replace(",", "")),
            )
        elif match := cls.WINNER_RE.match(message):
            waifu_message = WinMessage(
                winner_name=match.group(1), colour=match.group(2)
            )
        elif match := cls.OPEN_BET_EXHIBITION_RE.match(message):
            waifu_message = OpenBetExhibitionMessage(
                fighter_red_name=match.group(1), fighter_blue_name=match.group(2)
            )

        return waifu_message

    def _send(self, message: str) -> None:
        self.ssl_sock.send(f"{message}\n".encode("utf-8"))

    def _receive(self, expect_disconnect: bool = True) -> list[str]:
        try:
            readable_sockets, _, _ = select([self.ssl_sock], [], [], 10)
            decoded_read_buffer: str | None = None
            for readable_socket in readable_sockets:
                read_buffer = readable_socket.recv(1024)

                if not read_buffer and expect_disconnect is True:
                    # Likely that the remote socket was killed we must reconnect!
                    raise RemoteSocketDisconnect("No bytes returned")

                self.last_read = datetime.now(timezone.utc)
                decoded_read_buffer = read_buffer.decode()

            if decoded_read_buffer:
                return decoded_read_buffer.split("\r\n")
            return []
        except Exception:  # pylint: disable=broad-except
            return []

    def _initialize_socket(self) -> None:
        sock = socket()
        sock.settimeout(360)  # About a minute longer than PING/PONG
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)

        self.ssl_sock = context.wrap_socket(sock)
        self.ssl_sock.connect(("irc.chat.twitch.tv", 6697))
        self.ssl_sock.settimeout(360)

        self._send(f"PASS {self.oauth_token}")
        self._send(f"NICK {self.username}")

        logger.info("Authenticating as %s", self.username)
        authenticated = False
        authenticated_start = datetime.utcnow()
        while not authenticated:
            for message in self._receive(expect_disconnect=False):
                logger.info(message)
                if "welcome, glhf!" in message.lower():
                    logger.info("Authenticated successfully!")
                    authenticated = True
                    break
                if datetime.utcnow() - authenticated_start > timedelta(seconds=5):
                    raise TimeoutError("Took longer than 5 seconds to authenticate.")
