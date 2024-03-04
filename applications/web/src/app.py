import os
from pathlib import Path

import psycopg2
from flask.helpers import send_file
from flask.json import jsonify
from flask_openapi3 import Info, OpenAPI, Tag

from src.biz import (
    get_current_match_info,
    get_fighter_by_id,
    get_match_by_id,
    list_fighters,
    list_matches,
)
from src.schemas import (
    CurrentMatchInfoResponse,
    FighterModel,
    IdPath,
    ListFighterQuery,
    ListFighterResponse,
    ListMatchQuery,
    ListMatchResponse,
    MatchModel,
)

info = Info(
    title="SaltyBoy API",
    version="2.1.0",
    description="""
Welcome to the SaltyBoy API. You are welcome to integrate with this API however please 
bear in mind the following:

- I'll do my best to not bork your integration by updating the endpoints, no promises 
    though.
- Do not abuse the API. By this I mean feel free to scrape in short high bursts but 
    don't spam the API with something in a constant `while` loop for example. After all 
    this runs on a very cheap Vultr instance :)
- If you want new endpoints or a Database dump please ping me on 
    [Github](https://github.com/FranciscoAT/saltyboy). I'm more than happy to review MRs
    for new features and provide PostgreSQL DB dumps.
- The API itself is extremely small so I won't be providing an SDK but there's no 
    authentication and it should be really easy to integrate around it.
- Any datetime strings should be returned in 
    [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format.
""",
)
app = OpenAPI(__name__, info=info)

pg_pool = psycopg2.pool.ThreadedConnectionPool(
    1,
    20,
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host=os.environ["POSTGRES_HOST"],
    port=int(os.environ["POSTGRES_PORT"]),
    database=os.environ["POSTGRES_DB"],
)

fighter_tag = Tag(name="Fighter", description="Fighters recorded by SaltyBoy.")
match_tag = Tag(
    name="Match",
    description=(
        "Matches recorded by SaltyBoy. Only Tournament, and Matchmaking matches are "
        "recorded. Exhibition matches are not."
    ),
)
current_match_tag = Tag(
    name="Current Match",
    description=(
        "Current match information. Mainly used to get detailed information about the "
        "current match by the SaltyBoy extension."
    ),
)

public_path = Path(__file__).parent.parent


# === Web Endpoints ===
@app.route("/", methods=["GET"])
def file_index_request():
    return send_file(public_path / "public/index.html", mimetype="text/html")


@app.route("/favicon.ico", methods=["GET"])
def file_favicon_request():
    return send_file(
        public_path / "public/favicon.ico", mimetype="image/vdn.microsoft.icon"
    )


@app.route("/robots.txt", methods=["GET"])
def file_robots_request():
    return send_file(public_path / "public/robots.txt", mimetype="text/plain")


# === API Endpoints ===
# Fighters
@app.get(
    "/api/fighter/",
    summary="List Fighters",
    responses={200: ListFighterResponse},
    tags=[fighter_tag],
    strict_slashes=False,
)
def api_list_fighters(query: ListFighterQuery):
    """
    Lists Fighters in a paginated format.

    **Elo and Tier Elo**

    SaltyBoy stores and upkeeps a self tracked version of ELO and Tier ELO. When a
    fighter is first detected by SaltyBoy the ELO is set to 1500. SaltyBoy then uses
    a K value of 32 to do ELO update calculations. Tier ELO similarly is set to 1500
    and uses the same K value of 32. However, Tier Elo is reset to 1500 when a fighter
    is  detected to have changed tiers, either up or down.

    **Tier and Previous Tier**

    SaltyBoy keeps track of the current tier of the fighter. It is important to note
    that the real tier of the fighter may not be reflected in SaltyBoy until it sees the
    fighter again. At which point the tier of the fighter is updated, and the Tier ELO
    is also reset as per the above section.
    """
    return jsonify(list_fighters(pg_pool, query).model_dump())


@app.get(
    "/api/fighter/<int:id_>/",
    summary="Get fighter",
    responses={200: FighterModel},
    tags=[fighter_tag],
    strict_slashes=False,
)
def api_get_fighter(path: IdPath):
    """
    Get a specific Fighter by ID.

    **Note**: If you want to scrape the database I would recommend using the
    `GET /api/fighter/` pagination endpoint instead.
    """
    if fighter := get_fighter_by_id(pg_pool, path.id_):
        return jsonify(fighter.model_dump())
    return "Fighter not found", 404


# Matches
@app.get(
    "/api/match/",
    summary="List Matches",
    responses={200: ListMatchResponse},
    tags=[match_tag],
    strict_slashes=False,
)
def api_list_matches(query: ListMatchQuery):
    """
    List Matches in a paginated format.

    The `fighter`, `fighter_blue`, `fighter_red`, and `winner` query parameters are the
    ID of the associated Fighter in the database. In order to map the name of a fighter
    to an ID use the `GET /api/fighter/` endpoint.
    """
    return jsonify(list_matches(pg_pool, query).model_dump())


@app.get(
    "/api/match/<int:id_>/",
    summary="Get match",
    responses={200: MatchModel},
    tags=[match_tag],
    strict_slashes=False,
)
def api_get_match(path: IdPath):
    """
    Get a specific Match by ID.

    **Note**: If you want to scrape the database I would recommend using the
    `GET /api/match/` pagination endpoint instead.
    """
    if match_ := get_match_by_id(pg_pool, path.id_):
        return jsonify(match_.model_dump())
    return "Match not found", 404


# Current Match Info
@app.get(
    "/api/current_match_info/",
    summary="Current Match Information",
    tags=[current_match_tag],
    responses={200: CurrentMatchInfoResponse},
    strict_slashes=False,
)
def api_current_match_info():
    """
    Returns the details of the current match from SaltyBet.

    This can be a bit of a volatile endpoint that can be hard to integrate with so you
    need to be aware of the following:

    - `fighter_blue` and `fighter_red` reference the **name** and not the ID of the
        Fighter. While these fields per the schema _can_ have `null` values in my
        experience I've never seen this.
    - If either `fighter_blue` or `fighter_red` are in the database the respective field
        `fighter_blue_info` or `fighter_red_info` will be filled out otherwise will be
        `null`.
    - `fighter_blue_info` and `fighter_red_info` are just the standard Fighter model
        found in the `GET /api/fighter/` endpoints. However, in them will be a new field
        `matches` which will list **all** matches in the database associated with the
        `fighter_red` or `fighter_blue` Fighter of the current match.
    - `match_format` contains the format of the current match. Important to note that if
        the match format is exhibition then it is always the case that
        `fighter_blue_info` and `fighter_red_info` will have `null` values, as SaltyBoy
        does not record exhibition matches.
    - `tier` contains the tier of the match. Note that in exhibition matches it is very
        probable that this value is `null`. However, in tournament or matchmaking
        matches you can be very confident that this value will not be `null`.
    - `updated_at` should always contain the date time at which the content for this
        endpoint was updated. Note that this time should roughly correlate with the
        time where Waif4u bot announces "Bets are open..." in the Twitch chat.
    - This endpoint is known to go out of date due to the following reasons, and that
        your integration should code defensively and anticipate this endpoint going out
        of date:
        - The upstream bot that scrapes Twitch chat ran into an unrecoverable error.
            Although worth noting that this does not happen much if at all anymore.
        - Waif4U bot goes down in Twitch chat. Also an extremely rare occurrence.
    """
    if current_match_info := get_current_match_info(pg_pool):
        return jsonify(current_match_info.model_dump())
    return jsonify({})
