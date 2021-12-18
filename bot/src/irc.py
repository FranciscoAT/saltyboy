from dataclasses import dataclass
import logging
import re
from socket import socket
import ssl
from typing import Iterator, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class WaifuMessage:
    message_type: str  # One of: open,locked,win

    # Used in open bet / locked bet
    fighter_red: Optional[str] = None
    fighter_blue: Optional[str] = None

    # Used in open bet
    tier: Optional[str] = None
    match_format: Optional[str] = None

    # Used in locked bet
    bet_red: Optional[int] = None
    bet_blue: Optional[int] = None
    streak_red: Optional[int] = None
    streak_blue: Optional[int] = None

    # Used for win bet
    winner: Optional[str] = None
    colour: Optional[str] = None


class TwitchBot:

    OPEN_BET_RE = re.compile(r"Bets are OPEN for (.+) vs (.+)!\s+\((.) Tier\)\s+.*")
    LOCKED_BET_RE = re.compile(
        r"Bets are locked. (.+) \((-?[0-9]+)\) - \$(([0-9]{1,3},)*[0-9]{1,3}), (.+) \((-?[0-9]+)\) - \$(([0-9]{1,3},)*[0-9]{1,3})"
    )
    WINNER_RE = re.compile(r"(.+) wins! Payouts to Team (Red|Blue)\..*")

    def __init__(self, username: str, oauth_token: str) -> None:
        sock = socket()
        sock.settimeout(360)  # About a minute longer than PING/PONG

        self.ssl_sock = ssl.wrap_socket(sock)
        self.ssl_sock.connect(("irc.chat.twitch.tv", 6697))

        self._send(f"PASS {oauth_token}")
        self._send(f"NICK {username}")

        # Authenticate
        logger.info("Authenticating as %s", username)
        authenticated = False
        while not authenticated:
            for message in self._receive():
                logger.info(message)
                if "welcome, glhf!" in message.lower():
                    logger.info("Authenticated successfully!")
                    authenticated = True
                    break

        # Join channel
        logger.info("Joining channel saltybet...")
        self._send("JOIN #saltybet")
        joined = False
        while not joined:
            for message in self._receive():
                logger.info(message)
                if "End of /NAMES list" in message:
                    logger.info("Joined successfully!")
                    joined = True
                    break

    def listen(self) -> Iterator[WaifuMessage]:
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
    def _parse_message(cls, message: str) -> Optional[WaifuMessage]:
        logger.debug(message)
        waifu_message = None
        if match := cls.OPEN_BET_RE.match(message):
            match_format = None
            if "(matchmaking)" in message:
                match_format = "matchmaking"
            elif "tournament bracket" in message:
                match_format = "tournament"
            else:
                match_format = "exhibition"

            waifu_message = WaifuMessage(
                message_type="open",
                fighter_red=match.group(1),
                fighter_blue=match.group(2),
                tier=match.group(3),
                match_format=match_format,
            )
        elif match := cls.LOCKED_BET_RE.match(message):
            waifu_message = WaifuMessage(
                message_type="locked",
                fighter_red=match.group(1),
                streak_red=int(match.group(2)),
                bet_red=int(match.group(3).replace(",", "")),
                fighter_blue=match.group(5),
                streak_blue=int(match.group(6)),
                bet_blue=int(match.group(7).replace(",", "")),
            )
        elif match := cls.WINNER_RE.match(message):
            waifu_message = WaifuMessage(
                message_type="win", winner=match.group(1), colour=match.group(2)
            )

        return waifu_message

    def _send(self, message: str) -> None:
        self.ssl_sock.send(f"{message}\n".encode("utf-8"))

    def _receive(self) -> List[str]:
        read_buffer = self.ssl_sock.recv(1024).decode()
        return read_buffer.split("\r\n")
