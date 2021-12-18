from datetime import datetime
import logging
import sqlite3
from sqlite3 import Row
from typing import Optional

from src.objects import Match

logger = logging.getLogger(__name__)


class Database:
    _ACCEPTED_FORMATS = ["tournament", "matchmaking"]

    def __init__(self, database_uri: str) -> None:
        self.conn = sqlite3.connect(database_uri)
        self.conn.row_factory = Row

    def new_match(self, match: Match) -> None:
        if match.match_format not in self._ACCEPTED_FORMATS:
            logger.info(
                "Ignoring match since its match_format %s is not in %s",
                match.match_format,
                self._ACCEPTED_FORMATS,
            )
            return

        fighter_red = self._full_get_fighter(
            match.fighter_red, match.tier, match.streak_red
        )
        fighter_blue = self._full_get_fighter(
            match.fighter_blue, match.tier, match.streak_blue
        )

        if match.bet_blue is None or match.bet_red is None or match.winner is None:
            raise ValueError("Blue bet, red bet or winner was None.")

        winner = None
        if fighter_red["name"] == match.winner:
            winner = fighter_red["id"]
        elif fighter_blue["name"] == match.winner:
            winner = fighter_blue["id"]
        else:
            raise ValueError(
                "Accuracy error. Winner not found in either fighter objects."
            )

        insert_obj = {
            "date": datetime.utcnow(),
            "fighter_red": fighter_red["id"],
            "fighter_blue": fighter_blue["id"],
            "winner": winner,
            "bet_red": match.bet_red,
            "bet_blue": match.bet_blue,
            "streak_red": match.streak_red,
            "streak_blue": match.streak_blue,
            "tier": match.tier,
            "match_format": match.match_format,
            "colour": match.colour,
        }

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO match
                (
                    date,
                    fighter_red,
                    fighter_blue,
                    winner,
                    bet_red,
                    bet_blue,
                    streak_red,
                    streak_blue,
                    tier,
                    match_format,
                    colour
                )
            VALUES
                (
                    :date,
                    :fighter_red,
                    :fighter_blue,
                    :winner,
                    :bet_red,
                    :bet_blue,
                    :streak_red,
                    :streak_blue,
                    :tier,
                    :match_format,
                    :colour
                )
            """,
            insert_obj,
        )
        self.conn.commit()
        cursor.close()

    def _full_get_fighter(
        self, name: Optional[str], tier: Optional[str], best_streak: Optional[int]
    ) -> Row:
        if not name or not tier or best_streak is None:
            raise ValueError("Name, tier, or best_streak were empty or None.")

        fighter = self._get_fighter(name=name)
        if not fighter:
            fighter_id = self._create_fighter(name, tier, best_streak)
            fighter = self._get_fighter(id=fighter_id)
        elif fighter["best_streak"] < best_streak or fighter["tier"] != tier:
            self._update_fighter(fighter["id"], tier, best_streak)

        return fighter  # type: ignore

    def _create_fighter(self, name: str, tier: str, best_streak: int) -> int:
        cursor = self.conn.cursor()
        now = datetime.utcnow()
        insert_obj = {
            "name": name,
            "tier": tier,
            "best_streak": best_streak,
            "created_time": now,
            "last_updated": now,
        }
        cursor.execute(
            """
            INSERT INTO fighter
                (name, tier, best_streak, created_time, last_updated)
            VALUES
                (:name, :tier, :best_streak, :created_time, :last_updated)
            """,
            insert_obj,
        )
        fighter_id = cursor.lastrowid
        self.conn.commit()
        cursor.close()
        return fighter_id

    def _update_fighter(self, id: int, tier: str, best_streak: int) -> None:
        cursor = self.conn.cursor()
        update_obj = {
            "id": id,
            "tier": tier,
            "best_streak": best_streak,
            "last_updated": datetime.utcnow(),
        }
        cursor.execute(
            """
            UPDATE
                fighter
            SET
                tier = :tier,
                best_streak = :best_streak,
                last_updated = :last_updated
            WHERE
                id = :id
            """,
            update_obj,
        )
        self.conn.commit()
        cursor.close()

    def _get_fighter(
        self, id: Optional[int] = None, name: Optional[str] = None
    ) -> Optional[Row]:
        if id is None and not name:
            raise ValueError("Missing arguments id or name.")

        cursor = self.conn.cursor()
        select_stmt = "SELECT * FROM fighter WHERE"
        query_obj = {}
        if id is not None:
            select_stmt += " id = :id"
            query_obj["id"] = id
        if name:
            select_stmt += " name = :name"
            query_obj["name"] = name

        cursor.execute(select_stmt, query_obj)
        fighter = cursor.fetchone()
        cursor.close()
        return fighter
