import os
import sqlite3
from sqlite3 import Row
from typing import List, Optional


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(os.environ["DATABASE_PATH"])
        self.conn.row_factory = Row

    def get_fighter(
        self, fighter_name: Optional[str] = None, fighter_id: Optional[int] = None
    ) -> Optional[Row]:
        cursor = self.conn.cursor()
        select_stmt = "SELECT * FROM fighter WHERE"
        query_obj = {}
        if fighter_id:
            select_stmt += " id = :id"
            query_obj["id"] = fighter_id
        if fighter_name:
            select_stmt += " name = :name"
            query_obj["name"] = fighter_name

        cursor.execute(select_stmt, query_obj)
        fighter = cursor.fetchone()
        cursor.close()
        return fighter

    def get_matches(self, fighter_id: int) -> List[Row]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT
                *
            FROM
                match
            WHERE
                fighter_red = :id OR
                fighter_blue = :id
            """,
            {"id": fighter_id},
        )
        return cursor.fetchall()

    def get_current_match(self) -> Optional[Row]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM current_match")
        current_match = cursor.fetchall()
        if not current_match:
            return None
        return current_match[0]

    def get_stats(self, table: str) -> List[Row]:
        cursor = self.conn.cursor()
        cursor.execute(
            f"""
            SELECT
                tier, COUNT(*) as {table}_count
            FROM
                {table}
            GROUP BY
                tier
            ORDER BY
                {table}_count DESC;
            """
        )
        stats = cursor.fetchall()
        cursor.close()
        return stats
