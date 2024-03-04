# pylint: disable=too-many-statements

from typing import Any

from psycopg2.extras import DictRow


def generate_query_obj(page: int, page_size: int) -> dict:
    return {"offset": page * page_size, "limit": page_size}


def construct_final_query(
    select_stmt: str, where_stmts: list[str], include_offset: bool = True
) -> str:
    if where_stmts:
        select_stmt = f"{select_stmt} WHERE {' AND '.join(where_stmts)}"

    if include_offset:
        return f"{select_stmt} ORDER BY id ASC OFFSET %(offset)s LIMIT %(limit)s"

    return select_stmt


# === Fighters ===
def db_get_fighter_by_id(cursor, id_: int) -> DictRow | None:
    cursor.execute("SELECT * FROM fighter WHERE id = %(id)s", {"id": id_})
    return cursor.fetchone()


def db_fighter_count(
    cursor,
    name: str | None = None,
    tier: str | None = None,
    prev_tier: str | None = None,
    elo__gte: int | None = None,
    elo__lt: int | None = None,
    tier_elo__gte: int | None = None,
    tier_elo__lt: int | None = None,
    **kwargs,
) -> int:
    select_stmt = "SELECT COUNT(*) as total FROM fighter"
    where_stmts: list[str] = []
    query_obj: dict[str, Any] = {}

    if name:
        query_obj["name"] = name
        where_stmts.append("name = %(name)s")
    if tier:
        query_obj["tier"] = tier
        where_stmts.append("tier = %(tier)s")
    if prev_tier:
        query_obj["prev_tier"] = prev_tier
        where_stmts.append("prev_tier = %(prev_tier)s")
    if elo__gte is not None:
        query_obj["elo__gte"] = elo__gte
        where_stmts.append("elo >= %(elo__gte)s")
    if elo__lt is not None:
        query_obj["elo__lt"] = elo__lt
        where_stmts.append("elo < %(elo__lt)s")
    if tier_elo__gte is not None:
        query_obj["tier_elo__gte"] = tier_elo__gte
        where_stmts.append("tier_elo >= %(tier_elo__gte)s")
    if tier_elo__lt is not None:
        query_obj["tier_elo__lt"] = tier_elo__lt
        where_stmts.append("tier_elo < %(tier_elo__lt)s")

    cursor.execute(
        construct_final_query(select_stmt, where_stmts, include_offset=False), query_obj
    )
    return cursor.fetchone()["total"]


def db_list_fighters(
    cursor,
    page: int,
    page_size: int,
    name: str | None = None,
    tier: str | None = None,
    prev_tier: str | None = None,
    elo__gte: int | None = None,
    elo__lt: int | None = None,
    tier_elo__gte: int | None = None,
    tier_elo__lt: int | None = None,
) -> list[DictRow]:
    select_stmt = "SELECT * FROM fighter"
    where_stmts: list[str] = []
    query_obj = generate_query_obj(page, page_size)

    if name:
        query_obj["name"] = name
        where_stmts.append("name = %(name)s")
    if tier:
        query_obj["tier"] = tier
        where_stmts.append("tier = %(tier)s")
    if prev_tier:
        query_obj["prev_tier"] = prev_tier
        where_stmts.append("prev_tier = %(prev_tier)s")
    if elo__gte is not None:
        query_obj["elo__gte"] = elo__gte
        where_stmts.append("elo >= %(elo__gte)s")
    if elo__lt is not None:
        query_obj["elo__lt"] = elo__lt
        where_stmts.append("elo < %(elo__lt)s")
    if tier_elo__gte is not None:
        query_obj["tier_elo__gte"] = tier_elo__gte
        where_stmts.append("tier_elo >= %(tier_elo__gte)s")
    if tier_elo__lt is not None:
        query_obj["tier_elo__lt"] = tier_elo__lt
        where_stmts.append("tier_elo < %(tier_elo__lt)s")

    cursor.execute(construct_final_query(select_stmt, where_stmts), query_obj)
    return cursor.fetchall()


# === Matches ===
def db_get_match_by_id(cursor, id_: int) -> DictRow | None:
    cursor.execute("SELECT * FROM match WHERE id = %(id)s", {"id": id_})
    return cursor.fetchone()


def db_get_match_count(
    cursor,
    fighter_red: int | None = None,
    fighter_blue: int | None = None,
    fighter: int | None = None,
    winner: int | None = None,
    bet_red__gte: int | None = None,
    bet_red__lt: int | None = None,
    bet_blue__gte: int | None = None,
    bet_blue__lt: int | None = None,
    bet__gte: int | None = None,
    bet__lt: int | None = None,
    streak_red__gte: int | None = None,
    streak_red__lt: int | None = None,
    streak_blue__gte: int | None = None,
    streak_blue__lt: int | None = None,
    streak__gte: int | None = None,
    streak__lt: int | None = None,
    tier: str | None = None,
    match_format: str | None = None,
    colour: str | None = None,
    **kwargs,
) -> int:
    select_stmt = "SELECT COUNT(*) as total FROM match"
    where_stmts: list[str] = []
    query_obj: dict[str, Any] = {}

    if fighter_red is not None:
        where_stmts.append("fighter_red = %(fighter_red)s")
        query_obj["fighter_red"] = fighter_red
    if fighter_blue is not None:
        where_stmts.append("fighter_blue = %(fighter_blue)s")
        query_obj["fighter_blue"] = fighter_blue
    if fighter is not None:
        where_stmts.append("(fighter_red = %(fighter)s OR fighter_blue = %(fighter)s)")
        query_obj["fighter"] = fighter
    if winner is not None:
        where_stmts.append("winner = %(winner)s")
        query_obj["winner"] = winner
    if bet_red__gte is not None:
        where_stmts.append("bet_red >= %(bet_red__gte)s")
        query_obj["bet_red__gte"] = bet_red__gte
    if bet_red__lt is not None:
        where_stmts.append("bet_red < %(bet_red__lt)s")
        query_obj["bet_red__lt"] = bet_red__lt
    if bet_blue__gte is not None:
        where_stmts.append("bet_blue >= %(bet_blue__gte)s")
        query_obj["bet_blue__gte"] = bet_blue__gte
    if bet_blue__lt is not None:
        where_stmts.append("bet_blue < %(bet_blue__lt)s")
        query_obj["bet_blue__lt"] = bet_blue__lt
    if bet__gte is not None:
        where_stmts.append("(bet_red >= %(bet__gte)s OR bet_blue >= %(bet__gte)s)")
        query_obj["bet__gte"] = bet__gte
    if bet__lt is not None:
        where_stmts.append("(bet_red >= %(bet__lt)s OR bet_blue >= %(bet__lt)s)")
        query_obj["bet__lt"] = bet__lt
    if streak_red__gte is not None:
        where_stmts.append("streak_red >= %(streak_red__gte)s")
        query_obj["streak_red__gte"] = streak_red__gte
    if streak_red__lt is not None:
        where_stmts.append("streak_red < %(streak_red__lt)s")
        query_obj["streak_red__lt"] = streak_red__lt
    if streak_blue__gte is not None:
        where_stmts.append("streak_blue >= %(streak_blue__gte)s")
        query_obj["streak_blue__gte"] = streak_blue__gte
    if streak_blue__lt is not None:
        where_stmts.append("streak_blue < %(streak_blue__lt)s")
        query_obj["streak_blue__lt"] = streak_blue__lt
    if streak__gte is not None:
        where_stmts.append(
            "(streak_red >= %(streak__gte)s OR streak_blue >= %(streak__gte)s)"
        )
        query_obj["streak__gte"] = streak__gte
    if streak__lt is not None:
        where_stmts.append(
            "(streak_red >= %(streak__lt)s OR streak_blue >= %(streak__lt)s)"
        )
        query_obj["streak__lt"] = streak__lt
    if tier:
        where_stmts.append("tier = %(tier)s")
        query_obj["tier"] = tier
    if match_format:
        where_stmts.append("match_format = %(match_format)s")
        query_obj["match_format"] = match_format
    if colour:
        where_stmts.append("colour = %(colour)s")
        query_obj["colour"] = colour

    cursor.execute(
        construct_final_query(select_stmt, where_stmts, include_offset=False), query_obj
    )
    return cursor.fetchone()["total"]


def db_list_matches(
    cursor,
    page: int,
    page_size: int,
    fighter_red: int | None = None,
    fighter_blue: int | None = None,
    fighter: int | None = None,
    winner: int | None = None,
    bet_red__gte: int | None = None,
    bet_red__lt: int | None = None,
    bet_blue__gte: int | None = None,
    bet_blue__lt: int | None = None,
    bet__gte: int | None = None,
    bet__lt: int | None = None,
    streak_red__gte: int | None = None,
    streak_red__lt: int | None = None,
    streak_blue__gte: int | None = None,
    streak_blue__lt: int | None = None,
    streak__gte: int | None = None,
    streak__lt: int | None = None,
    tier: str | None = None,
    match_format: str | None = None,
    colour: str | None = None,
) -> list[DictRow]:
    select_stmt = "SELECT * FROM match"
    where_stmts: list[str] = []
    query_obj = generate_query_obj(page, page_size)

    if fighter_red is not None:
        where_stmts.append("fighter_red = %(fighter_red)s")
        query_obj["fighter_red"] = fighter_red
    if fighter_blue is not None:
        where_stmts.append("fighter_blue = %(fighter_blue)s")
        query_obj["fighter_blue"] = fighter_blue
    if fighter is not None:
        where_stmts.append("(fighter_red = %(fighter)s OR fighter_blue = %(fighter)s)")
        query_obj["fighter"] = fighter
    if winner is not None:
        where_stmts.append("winner = %(winner)s")
        query_obj["winner"] = winner
    if bet_red__gte is not None:
        where_stmts.append("bet_red >= %(bet_red__gte)s")
        query_obj["bet_red__gte"] = bet_red__gte
    if bet_red__lt is not None:
        where_stmts.append("bet_red < %(bet_red__lt)s")
        query_obj["bet_red__lt"] = bet_red__lt
    if bet_blue__gte is not None:
        where_stmts.append("bet_blue >= %(bet_blue__gte)s")
        query_obj["bet_blue__gte"] = bet_blue__gte
    if bet_blue__lt is not None:
        where_stmts.append("bet_blue < %(bet_blue__lt)s")
        query_obj["bet_blue__lt"] = bet_blue__lt
    if bet__gte is not None:
        where_stmts.append("(bet_red >= %(bet__gte)s OR bet_blue >= %(bet__gte)s)")
        query_obj["bet__gte"] = bet__gte
    if bet__lt is not None:
        where_stmts.append("(bet_red >= %(bet__lt)s OR bet_blue >= %(bet__lt)s)")
        query_obj["bet__lt"] = bet__lt
    if streak_red__gte is not None:
        where_stmts.append("streak_red >= %(streak_red__gte)s")
        query_obj["streak_red__gte"] = streak_red__gte
    if streak_red__lt is not None:
        where_stmts.append("streak_red < %(streak_red__lt)s")
        query_obj["streak_red__lt"] = streak_red__lt
    if streak_blue__gte is not None:
        where_stmts.append("streak_blue >= %(streak_blue__gte)s")
        query_obj["streak_blue__gte"] = streak_blue__gte
    if streak_blue__lt is not None:
        where_stmts.append("streak_blue < %(streak_blue__lt)s")
        query_obj["streak_blue__lt"] = streak_blue__lt
    if streak__gte is not None:
        where_stmts.append(
            "(streak_red >= %(streak__gte)s OR streak_blue >= %(streak__gte)s)"
        )
        query_obj["streak__gte"] = streak__gte
    if streak__lt is not None:
        where_stmts.append(
            "(streak_red >= %(streak__lt)s OR streak_blue >= %(streak__lt)s)"
        )
        query_obj["streak__lt"] = streak__lt
    if tier:
        where_stmts.append("tier = %(tier)s")
        query_obj["tier"] = tier
    if match_format:
        where_stmts.append("match_format = %(match_format)s")
        query_obj["match_format"] = match_format
    if colour:
        where_stmts.append("colour = %(colour)s")
        query_obj["colour"] = colour

    cursor.execute(construct_final_query(select_stmt, where_stmts), query_obj)
    return cursor.fetchall()


# === Current Match ===
def db_get_current_match(cursor) -> DictRow | None:
    cursor.execute("SELECT * FROM current_match LIMIT 1")
    return cursor.fetchone()
