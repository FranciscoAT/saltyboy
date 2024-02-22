from typing import Callable, TypeVar

from psycopg2.extras import DictCursor
from psycopg2.pool import ThreadedConnectionPool

from src.database import (
    db_fighter_count,
    db_get_fighter_by_id,
    db_list_fighters,
    db_get_match_by_id,
    db_get_match_count,
    db_list_matches,
)
from src.schemas import (
    FighterModel,
    ListFighterQuery,
    ListFighterResponse,
    MatchModel,
    ListMatchQuery,
    ListMatchResponse,
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
