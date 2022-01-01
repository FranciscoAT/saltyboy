from datetime import datetime, timedelta
import logging
import re
from socket import socket
import ssl
from typing import Iterator, List, Optional, Union

from src.objects.waifu import (
    LockedBetMessage,
    OpenBetExhibitionMessage,
    OpenBetMessage,
    WinMessage,
)

logger = logging.getLogger(__name__)

ReturnMessages = Union[
    OpenBetMessage, LockedBetMessage, WinMessage, OpenBetExhibitionMessage
]


class TwitchBot:

    MAX_AUTH_ATTEMPTS = 5

    OPEN_BET_RE = re.compile(r"Bets are OPEN for (.+) vs (.+)!\s+\((.) Tier\)\s+.*")
    OPEN_BET_EXHIBITION_RE = re.compile(
        r"Bets are OPEN for (.+) vs (.+)!\s+\(.+\)\s+\(exhibitions\)\s+.*"
    )
    LOCKED_BET_RE = re.compile(
        r"Bets are locked. (.+) \((-?[0-9]+)\) - \$(([0-9]{1,3},)*[0-9]{1,3}), (.+) \((-?[0-9]+)\) - \$(([0-9]{1,3},)*[0-9]{1,3})"
    )
    WINNER_RE = re.compile(r"(.+) wins! Payouts to Team (Red|Blue)\..*")

    def __init__(self, username: str, oauth_token: str) -> None:

        num_auth_attempts = 0
        connected = False
        while not connected:
            try:
                self._connect(oauth_token, username)
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
            for message in self._receive():
                if "PING :tmi.twitch.tv" == message:
                    logger.info("Received a PING, sending PONG.")
                    self._send("PONG :tmi.twitch.tv")
                if not message.startswith(":waifu4u"):
                    continue
                try:
                    message = self._parse_message(message.split("#saltybet :")[1])
                    if message:
                        logger.debug(message)
                        yield message
                except Exception:
                    logger.error("Something went wrong", exc_info=True)

    @classmethod
    def _parse_message(cls, message: str) -> Optional[ReturnMessages]:
        logger.debug(message)
        waifu_message = None
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

    def _receive(self) -> List[str]:
        read_buffer = self.ssl_sock.recv(1024).decode()
        return read_buffer.split("\r\n")

    def _connect(self, oauth_token: str, username: str) -> None:
        sock = socket()
        sock.settimeout(360)  # About a minute longer than PING/PONG

        self.ssl_sock = ssl.wrap_socket(sock)
        self.ssl_sock.connect(("irc.chat.twitch.tv", 6697))

        self._send(f"PASS {oauth_token}")
        self._send(f"NICK {username}")

        logger.info("Authenticating as %s", username)
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
