from typing import Callable, TypeVar

from psycopg2.extras import DictCursor
from psycopg2.pool import ThreadedConnectionPool

from src.database import (
    db_fighter_count,
    db_get_current_match,
    db_get_fighter_by_id,
    db_get_last_match,
    db_get_match_by_id,
    db_get_match_count,
    db_list_fighters,
    db_list_matches,
)
from src.schemas import (
    CurrentMatchInfoResponse,
    CurrentMatchInfoResponseWithStats,
    ExtendedFighterModel,
    ExtendedFighterModelWithStats,
    FighterModel,
    FighterStats,
    ListFighterQuery,
    ListFighterResponse,
    ListMatchQuery,
    ListMatchResponse,
    MatchModel,
)

RT = TypeVar("RT")


def pg_cursor(func: Callable[..., RT]):
    def inner(pg_pool: ThreadedConnectionPool, *args, **kwargs) -> RT:
        pg_connection = pg_pool.getconn()
        pg_cursor_ = pg_connection.cursor(cursor_factory=DictCursor)
        response = func(pg_cursor_, *args, **kwargs)
        pg_cursor_.close()
        pg_pool.putconn(pg_connection)

        return response

    return inner


# === Fighters ===
@pg_cursor
def get_fighter_by_id(cursor, id_: int) -> FighterModel | None:
    if db_fighter := db_get_fighter_by_id(cursor, id_):
        return FighterModel(**db_fighter)
    return None


@pg_cursor
def list_fighters(cursor, query_args: ListFighterQuery) -> ListFighterResponse:
    dumped_args = query_args.model_dump()
    return ListFighterResponse(
        page=query_args.page,
        page_size=query_args.page_size,
        count=db_fighter_count(cursor, **dumped_args),
        results=[FighterModel(**x) for x in db_list_fighters(cursor, **dumped_args)],
    )


# === Matches ===
@pg_cursor
def get_match_by_id(cursor, id_: int) -> MatchModel | None:
    if match_ := db_get_match_by_id(cursor, id_):
        return MatchModel(**match_)
    return None


@pg_cursor
def list_matches(cursor, query_args: ListMatchQuery) -> ListMatchResponse:
    dumped_args = query_args.model_dump()
    return ListMatchResponse(
        page=query_args.page,
        page_size=query_args.page_size,
        count=db_get_match_count(cursor, **dumped_args),
        results=[MatchModel(**x) for x in db_list_matches(cursor, **dumped_args)],
    )


@pg_cursor
def get_last_match(cursor) -> MatchModel | None:
    if match_ := db_get_last_match(cursor):
        return MatchModel(**match_)
    return None


# === Current Match ===
@pg_cursor
def get_current_match_info_with_stats(
    cursor,
) -> CurrentMatchInfoResponseWithStats | None:
    """Deprecated Method call"""
    current_match = db_get_current_match(cursor)
    if not current_match:
        return None

    if current_match["match_format"] == "exhibition":
        return CurrentMatchInfoResponseWithStats(**current_match)

    return CurrentMatchInfoResponseWithStats(
        **current_match,
        fighter_blue_info=get_fighter_details_with_stats(  # type: ignore
            cursor, current_match["fighter_blue"]
        ),
        fighter_red_info=get_fighter_details_with_stats(  # type: ignore
            cursor, current_match["fighter_red"]
        ),
    )


def get_fighter_details_with_stats(
    cursor, name: str
) -> ExtendedFighterModelWithStats | None:
    cursor.execute("SELECT * FROM fighter WHERE name = %(name)s", {"name": name})
    fighter = cursor.fetchone()
    if not fighter:
        return None

    cursor.execute(
        "SELECT * FROM match WHERE fighter_red = %(id)s OR fighter_blue = %(id)s",
        {"id": fighter["id"]},
    )
    matches: list[MatchModel] = []
    total_bet = 0
    wins = 0
    for match_ in cursor.fetchall():
        match_model = MatchModel(**match_)
        matches.append(match_model)
        total_bet += (
            match_model.bet_red
            if match_model.fighter_red == fighter["id"]
            else match_model.bet_blue
        )
        wins += 1 if match_model.winner == fighter["id"] else 0

    if len(matches) == 0:
        stats = FighterStats(average_bet=0.0, total_matches=0, win_rate=0.0)
    else:
        stats = FighterStats(
            average_bet=round(total_bet / len(matches), 2),
            total_matches=len(matches),
            win_rate=round(wins / len(matches), 2),
        )

    return ExtendedFighterModelWithStats(
        **fighter,
        matches=matches,
        stats=stats,
    )


@pg_cursor
def get_current_match_info(cursor) -> CurrentMatchInfoResponse | None:
    current_match = db_get_current_match(cursor)
    if not current_match:
        return None

    if current_match["match_format"] == "exhibition":
        return CurrentMatchInfoResponse(**current_match)

    return CurrentMatchInfoResponse(
        **current_match,
        fighter_blue_info=get_fighter_details(cursor, current_match["fighter_blue"]),  # type: ignore
        fighter_red_info=get_fighter_details(cursor, current_match["fighter_red"]),  # type: ignore
    )


def get_fighter_details(cursor, name: str) -> ExtendedFighterModel | None:
    cursor.execute("SELECT * FROM fighter WHERE name = %(name)s", {"name": name})
    fighter = cursor.fetchone()
    if not fighter:
        return None

    cursor.execute(
        "SELECT * FROM match WHERE fighter_red = %(id)s OR fighter_blue = %(id)s",
        {"id": fighter["id"]},
    )

    return ExtendedFighterModel(
        **fighter, matches=[MatchModel(**x) for x in cursor.fetchall()]
    )
