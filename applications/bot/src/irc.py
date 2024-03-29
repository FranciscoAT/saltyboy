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

ReturnMessages = (
    OpenBetMessage | LockedBetMessage | WinMessage | OpenBetExhibitionMessage | None
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

    def __init__(
        self, twitch_username: str, twitch_oauth_token: str, logger: logging.Logger
    ) -> None:
        self.username = twitch_username
        self.oauth_token = twitch_oauth_token
        self.ssl_sock: SSLSocket
        self.last_read = datetime.now(timezone.utc)
        self.logger = logger

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
        self.logger.info("Joining channel saltybet...")
        self._send("JOIN #saltybet")
        joined = False
        joined_start = datetime.now(timezone.utc)
        while not joined:
            for message in self._receive(expect_disconnect=False):
                self.logger.info(message)
                if "End of /NAMES list" in message:
                    self.logger.info("Joined successfully!")
                    joined = True
                    break
                if datetime.now(timezone.utc) - joined_start > timedelta(seconds=5):
                    raise TimeoutError(
                        "Took longer than 5 seconds to join saltybet channel."
                    )

    def listen(self) -> Iterator[ReturnMessages]:
        while True:
            if self.last_read < datetime.now(timezone.utc) - timedelta(minutes=10):
                self.logger.warning("Last read was over 10 minutes ago.")
                self.connect()

            try:
                for message in self._receive():
                    if "PING :tmi.twitch.tv" == message:
                        self.logger.info("Received a PING, sending PONG.")
                        self._send("PONG :tmi.twitch.tv")

                    if not message.startswith(":waifu4u"):
                        continue

                    try:
                        if return_message := self.parse_message(
                            message.split("#saltybet :")[1]
                        ):
                            self.logger.debug(message)
                            yield return_message
                    except Exception:
                        self.logger.error("Something went wrong", exc_info=True)
            except RemoteSocketDisconnect:
                # Questionable if this is ever hit
                self.logger.info("Remote socket was likely disconnected. Reconnecting.")
                self.connect()

            yield None

            time.sleep(5)

    def parse_message(self, message: str) -> ReturnMessages | None:
        self.logger.debug(message)
        waifu_message: ReturnMessages | None = None
        if match := self.OPEN_BET_RE.match(message):
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
        elif match := self.LOCKED_BET_RE.match(message):
            waifu_message = LockedBetMessage(
                fighter_red_name=match.group(1),
                streak_red=int(match.group(2)),
                bet_red=int(match.group(3).replace(",", "")),
                fighter_blue_name=match.group(5),
                streak_blue=int(match.group(6)),
                bet_blue=int(match.group(7).replace(",", "")),
            )
        elif match := self.WINNER_RE.match(message):
            waifu_message = WinMessage(
                winner_name=match.group(1), colour=match.group(2)
            )
        elif match := self.OPEN_BET_EXHIBITION_RE.match(message):
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
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2

        self.ssl_sock = context.wrap_socket(sock, server_hostname="irc.chat.twitch.tv")
        self.ssl_sock.connect(("irc.chat.twitch.tv", 6697))
        self.ssl_sock.settimeout(360)

        self._send(f"PASS {self.oauth_token}")
        self._send(f"NICK {self.username}")

        self.logger.info("Authenticating as %s", self.username)
        authenticated = False
        authenticated_start = datetime.now(timezone.utc)
        while not authenticated:
            for message in self._receive(expect_disconnect=False):
                self.logger.info(message)
                if "welcome, glhf!" in message.lower():
                    self.logger.info("Authenticated successfully!")
                    authenticated = True
                    break
                if datetime.now(timezone.utc) - authenticated_start > timedelta(
                    seconds=5
                ):
                    raise TimeoutError("Took longer than 5 seconds to authenticate.")
