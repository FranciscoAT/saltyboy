import logging
import re
import ssl
import time
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from select import select
from socket import socket
from ssl import SSLSocket

from src.objects.waifu import (
    LockedBetMessage,
    OpenBetExhibitionMessage,
    OpenBetMessage,
    WinMessage,
)

logger = logging.getLogger(__name__)

ReturnMessages = (
    OpenBetMessage | LockedBetMessage | WinMessage | OpenBetExhibitionMessage
)


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

    def __init__(self, username: str, oauth_token: str) -> None:
        self.username = username
        self.oauth_token = oauth_token
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
            for message in self._receive():
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

            for message in self._receive():
                if "PING :tmi.twitch.tv" == message:
                    logger.info("Received a PING, sending PONG.")
                    self._send("PONG :tmi.twitch.tv")
                if not message.startswith(":waifu4u"):
                    continue
                try:
                    return_message = self.parse_message(message.split("#saltybet :")[1])
                    if return_message:
                        logger.debug(message)
                        yield return_message
                except Exception:  # pylint: disable=broad-except
                    logger.error("Something went wrong", exc_info=True)
                time.sleep(5)

    @classmethod
    def parse_message(cls, message: str) -> ReturnMessages | None:
        logger.debug(message)
        waifu_message: ReturnMessages | None = None
        if match := cls.OPEN_BET_RE.match(message):
            if "(matchmaking)" in message:
                match_format = "matchmaking"
            elif "tournament bracket" in message:
                match_format = "tournament"
            else:
                match_format = "exhibition"

            waifu_message = OpenBetMessage(
                fighter_red=match.group(1),
                fighter_blue=match.group(2),
                tier=match.group(3),
                match_format=match_format,
            )
        elif match := cls.LOCKED_BET_RE.match(message):
            waifu_message = LockedBetMessage(
                fighter_red=match.group(1),
                streak_red=int(match.group(2)),
                bet_red=int(match.group(3).replace(",", "")),
                fighter_blue=match.group(5),
                streak_blue=int(match.group(6)),
                bet_blue=int(match.group(7).replace(",", "")),
            )
        elif match := cls.WINNER_RE.match(message):
            waifu_message = WinMessage(winner=match.group(1), colour=match.group(2))
        elif match := cls.OPEN_BET_EXHIBITION_RE.match(message):
            waifu_message = OpenBetExhibitionMessage(
                fighter_red=match.group(1), fighter_blue=match.group(2)
            )

        return waifu_message

    def _send(self, message: str) -> None:
        self.ssl_sock.send(f"{message}\n".encode("utf-8"))

    def _receive(self) -> list[str]:
        try:
            readable_sockets, _, _ = select([self.ssl_sock], [], [], 10)
            read_buffer: str | None = None
            for readable_socket in readable_sockets:
                read_buffer = readable_socket.recv(1024).decode()
                self.last_read = datetime.now(timezone.utc)

            if read_buffer:
                return read_buffer.split("\r\n")
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
            for message in self._receive():
                logger.info(message)
                if "welcome, glhf!" in message.lower():
                    logger.info("Authenticated successfully!")
                    authenticated = True
                    break
                if datetime.utcnow() - authenticated_start > timedelta(seconds=5):
                    raise TimeoutError("Took longer than 5 seconds to authenticate.")
