from src.database import Database
from src.schemas.database import DatabaseStatsBreakdown, DatabaseStatsSchema


def get_db_stats() -> DatabaseStatsSchema:
    database_ = Database()
    matches = _get_stats("match", database_)
    fighters = _get_stats("fighter", database_)

    return DatabaseStatsSchema(matches=matches, fighters=fighters)


def _get_stats(table_name: str, database_: Database) -> DatabaseStatsBreakdown:
    db_stats = database_.get_stats(table_name)
    breakdown = {}
    total = 0
    for row in db_stats:
        row_count = row[f"{table_name}_count"]
        breakdown[row["tier"]] = row_count
        total += row_count

    return DatabaseStatsBreakdown(breakdown=breakdown, total=total)
