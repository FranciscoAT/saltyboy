import logging
import math
import sqlite3
from datetime import datetime
from sqlite3 import Row
from typing import Any

from src.objects.match import Match

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

        if match.streak_red is None or match.streak_blue is None:
            raise ValueError(
                f"Cannot complete operation best streak not provided. {match}"
            )

        fighter_red = self._get_and_create_fighter(
            match.fighter_red, match.tier, match.streak_red
        )
        fighter_blue = self._get_and_create_fighter(
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

        red_won = fighter_red["id"] == winner
        self._update_fighter(
            fighter_red,
            match.tier,
            match.streak_red,
            fighter_blue["elo"],
            fighter_blue["tier_elo"],
            red_won,
        )
        self._update_fighter(
            fighter_blue,
            match.tier,
            match.streak_blue,
            fighter_red["elo"],
            fighter_red["tier_elo"],
            not red_won,
        )
        self.conn.commit()
        cursor.close()

    def update_current_match(
        self,
        fighter_red: str,
        fighter_blue: str,
        match_format: str,
        tier: str | None = None,
    ) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM current_match")
        insert_obj = {
            "fighter_red": fighter_red,
            "fighter_blue": fighter_blue,
            "tier": tier,
            "match_format": match_format,
        }
        cursor.execute(
            """
                INSERT INTO current_match
                    (
                        fighter_red,
                        fighter_blue,
                        tier,
                        match_format
                    )
                VALUES
                    (
                        :fighter_red,
                        :fighter_blue,
                        :tier,
                        :match_format
                    )
                """,
            insert_obj,
        )
        self.conn.commit()
        cursor.close()

    def _get_and_create_fighter(self, name: str, tier: str, best_streak: int) -> Row:
        fighter = self._get_fighter(name=name)
        if not fighter:
            fighter = self._create_fighter(
                name=name, tier=tier, best_streak=best_streak
            )

        return fighter

    def _create_fighter(self, name: str, tier: str, best_streak: int) -> Row:
        cursor = self.conn.cursor()
        now = datetime.utcnow()
        insert_obj = {
            "name": name,
            "tier": tier,
            "best_streak": best_streak,
            "created_time": now,
            "last_updated": now,
            "elo": 1500,
        }
        cursor.execute(
            """
            INSERT INTO fighter
                (name, tier, best_streak, created_time, last_updated, elo, tier_elo, prev_tier)
            VALUES
                (:name, :tier, :best_streak, :created_time, :last_updated, :elo, :elo, :tier)
            """,
            insert_obj,
        )
        fighter_id = cursor.lastrowid
        self.conn.commit()
        cursor.execute("SELECT * FROM fighter WHERE id = :id", {"id": fighter_id})
        fighter = cursor.fetchone()
        cursor.close()
        return fighter

    def _update_fighter(
        self,
        fighter: Row,
        tier: str,
        best_streak: int,
        opponent_elo: int,
        opponent_tier_elo: int,
        won: bool,
    ) -> None:
        # pylint: disable=too-many-arguments
        updated_tier = tier
        prev_tier = fighter["tier"]
        tier_elo = fighter["tier_elo"] if updated_tier == prev_tier else 1500
        updated_streak = (
            best_streak
            if best_streak > fighter["best_streak"]
            else fighter["best_streak"]
        )
        updated_elo = self._calculate_elo(fighter["elo"], opponent_elo, won)
        updated_tier_elo = self._calculate_elo(tier_elo, opponent_tier_elo, won)

        cursor = self.conn.cursor()
        update_obj = {
            "id": fighter["id"],
            "last_updated": datetime.utcnow(),
            "best_streak": updated_streak,
            "tier": updated_tier,
            "prev_tier": prev_tier,
            "tier_elo": updated_tier_elo,
            "elo": updated_elo,
        }
        cursor.execute(
            """
            UPDATE
                fighter
            SET
                last_updated = :last_updated,
                best_streak = :best_streak,
                tier = :tier,
                prev_tier = :prev_tier,
                tier_elo = :tier_elo,
                elo = :elo
            WHERE
                id = :id
            """,
            update_obj,
        )
        cursor.close()

    def _get_fighter(
        self, id_: int | None = None, name: str | None = None
    ) -> Row | None:
        if id_ is None and not name:
            raise ValueError("Missing one required argument of id or name")

        cursor = self.conn.cursor()
        select_stmt = "SELECT * FROM fighter WHERE"
        query_obj: dict[str, Any] = {}
        if id_ is not None:
            select_stmt += " id = :id"
            query_obj["id"] = id_
        if name:
            select_stmt += " name = :name"
            query_obj["name"] = name

        cursor.execute(select_stmt, query_obj)
        fighter = cursor.fetchone()
        cursor.close()
        return fighter

    @classmethod
    def _calculate_elo(cls, elo: int, opponent_elo: int, won: bool) -> int:
        # Calculate transformed ratings
        tr_alpha = math.pow(10, elo / 400)
        tr_beta = math.pow(10, opponent_elo / 400)

        # Calculate expected score
        es_alpha = tr_alpha / (tr_alpha + tr_beta)

        # Score
        score_alpha = 1 if won is True else 0

        # Calculate updated ELO
        return int(elo + (32 * (score_alpha - es_alpha)))
