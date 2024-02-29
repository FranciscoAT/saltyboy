import logging
import math
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras

from src.objects import Match, MatchFormat

logger = logging.getLogger(__name__)


class Database:
    ACCEPTED_MATCH_FORMATS = [MatchFormat.MATCHMAKING, MatchFormat.TOURNAMENT]

    def __init__(
        self, dbname: str, user: str, password: str, host: str, port: int
    ) -> None:
        self.connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            cursor_factory=psycopg2.extras.DictCursor,
        )

    def record_match(self, match: Match) -> None:
        if match.match_format not in self.ACCEPTED_MATCH_FORMATS:
            logger.info(
                "Ignoring match since its match_format %s is not in %s",
                match.match_format,
                self.ACCEPTED_MATCH_FORMATS,
            )
            return

        if match.streak_red is None or match.streak_blue is None:
            logger.error(
                "Cannot complete operation. Best streak not provided: %s", match
            )
            return

        fighter_red = self._get_or_create_fighter(
            match.fighter_red_name, match.tier, match.streak_red
        )
        fighter_blue = self._get_or_create_fighter(
            match.fighter_blue_name, match.tier, match.streak_blue
        )

        if match.bet_blue is None or match.bet_red is None or match.winner is None:
            logger.error("Blue bet, red bet or winner was not set: %s", match)
            return

        winner: int | None = None
        if fighter_red["name"] == match.winner:
            winner = fighter_red["id"]
        elif fighter_blue["name"] == match.winner:
            winner = fighter_blue["id"]
        else:
            logger.error(
                "Accuracy error. Winner not found in either fighter objects: %s, "
                "fighter_red: %s, fighter_blue: %s",
                match,
                fighter_red,
                fighter_blue,
            )
            return

        insert_obj = {
            "date": datetime.now(timezone.utc),
            "fighter_red": fighter_red["id"],
            "fighter_blue": fighter_blue["id"],
            "winner": winner,
            "bet_red": match.bet_red,
            "bet_blue": match.bet_blue,
            "streak_red": match.streak_red,
            "streak_blue": match.streak_blue,
            "tier": match.tier,
            "match_format": match.match_format.value,
            "colour": match.colour,
        }

        cursor = self.connection.cursor()
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
                    %(date)s,
                    %(fighter_red)s,
                    %(fighter_blue)s,
                    %(winner)s,
                    %(bet_red)s,
                    %(bet_blue)s,
                    %(streak_red)s,
                    %(streak_blue)s,
                    %(tier)s,
                    %(match_format)s,
                    %(colour)s
                )
            """,
            insert_obj,
        )
        self.connection.commit()

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
        self.connection.commit()
        cursor.close()

    def update_current_match(
        self,
        fighter_red_name: str,
        fighter_blue_name: str,
        match_format: MatchFormat,
        tier: str | None = None,
    ) -> None:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM current_match")
        insert_obj = {
            "fighter_red": fighter_red_name,
            "fighter_blue": fighter_blue_name,
            "tier": tier,
            "match_format": match_format.value,
            "updated_at": datetime.now(timezone.utc),
        }
        cursor.execute(
            """
                INSERT INTO current_match
                    (
                        fighter_red,
                        fighter_blue,
                        tier,
                        match_format,
                        updated_at
                    )
                VALUES
                    (
                        %(fighter_red)s,
                        %(fighter_blue)s,
                        %(tier)s,
                        %(match_format)s,
                        %(updated_at)s
                    )
                """,
            insert_obj,
        )
        self.connection.commit()
        cursor.close()

    def update_bot_heartbeat(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM bot_heartbeat")
        cursor.execute(
            "INSERT INTO bot_heartbeat (heartbeat_time) VALUES (%(heartbeat_time)s)",
            {"heartbeat_time": datetime.now(timezone.utc)},
        )
        self.connection.commit()
        cursor.close()

    def get_bot_heartbeat(self) -> None | datetime:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM bot_heartbeat LIMIT 1")
        bot_heartbeat_row = cursor.fetchone()
        if not bot_heartbeat_row:
            return None
        bot_heartbeat_time = bot_heartbeat_row["heartbeat_time"].replace(tzinfo=timezone.utc)  # type: ignore
        cursor.close()
        return bot_heartbeat_time

    def _get_or_create_fighter(
        self, name: str, tier: str, best_streak: int
    ) -> psycopg2.extras.DictRow:
        fighter = self._get_fighter_by_name(name)
        if not fighter:
            fighter = self._create_fighter(
                name=name, tier=tier, best_streak=best_streak
            )

        return fighter

    def _create_fighter(
        self, name: str, tier: str, best_streak: int
    ) -> psycopg2.extras.DictRow:
        cursor = self.connection.cursor()
        now = datetime.now(timezone.utc)
        insert_obj = {
            "name": name,
            "tier": tier,
            "best_streak": best_streak,
            "created_time": now,
            "elo": 1500,
        }
        cursor.execute(
            """
            INSERT INTO fighter
                (
                    name, 
                    tier, 
                    prev_tier,
                    best_streak, 
                    created_time, 
                    last_updated, 
                    elo, 
                    tier_elo
                )
            VALUES
                (
                    %(name)s, 
                    %(tier)s, 
                    %(tier)s,
                    %(best_streak)s, 
                    %(created_time)s, 
                    %(created_time)s, 
                    %(elo)s, 
                    %(elo)s
                )
            RETURNING
                id
            """,
            insert_obj,
        )
        # We know this should always return something
        fighter_id = cursor.fetchone()[0]  # type: ignore
        self.connection.commit()
        cursor.execute("SELECT * FROM fighter WHERE id = %(id)s", {"id": fighter_id})
        fighter = cursor.fetchone()
        cursor.close()
        return fighter  # type: ignore

    def _update_fighter(
        self,
        fighter: psycopg2.extras.DictRow,
        tier: str,
        best_streak: int,
        opponent_elo: int,
        opponent_tier_elo: int,
        won: bool,
    ) -> None:
        updated_tier = tier
        prev_tier = fighter["tier"]

        # Tier elo is the current tier elo if fighter hasn't changed tiers, otherwise
        # reset tier elo to 1500
        tier_elo = fighter["tier_elo"] if updated_tier == prev_tier else 1500

        updated_streak = (
            best_streak
            if best_streak > fighter["best_streak"]
            else fighter["best_streak"]
        )

        updated_elo = self._calculate_elo(fighter["elo"], opponent_elo, won)
        updated_tier_elo = self._calculate_elo(tier_elo, opponent_tier_elo, won)

        cursor = self.connection.cursor()
        update_obj = {
            "id": fighter["id"],
            "last_updated": datetime.now(timezone.utc),
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
                last_updated = %(last_updated)s,
                best_streak = %(best_streak)s,
                tier = %(tier)s,
                prev_tier = %(prev_tier)s,
                tier_elo = %(tier_elo)s,
                elo = %(elo)s
            WHERE
                id = %(id)s
            """,
            update_obj,
        )
        cursor.close()

    def _get_fighter_by_name(self, name: str) -> psycopg2.extras.DictRow | None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM fighter WHERE name = %(name)s", {"name": name})
        fighter = cursor.fetchone()
        cursor.close()
        return fighter  # type: ignore

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
