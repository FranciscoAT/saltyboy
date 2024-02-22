import json
import os
from pathlib import Path

import psycopg2
from flask.helpers import send_file
from flask.json import jsonify
from flask_cors import CORS
from pydantic import ValidationError
from flask_openapi3 import Info, Tag, OpenAPI

from src.biz import (
    get_fighter_by_id,
    list_fighters,
    get_match_by_id,
    list_matches,
    get_last_match,
    get_current_match_info,
)
from src.schemas import (
    ListFighterQuery,
    ListMatchQuery,
    ListFighterResponse,
    FighterModel,
    ListMatchResponse,
    MatchModel,
    CurrentMatchInfoResponse,
    IdPath,
)

info = Info(title="SaltyBoy API", version="2.0.0")
app = OpenAPI(__name__, info=info)
CORS(app, origins=["https://saltybet.com", "https://salty-boy.com"])

pg_pool = psycopg2.pool.ThreadedConnectionPool(
    1,
    10,
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


# === Handlers ===
@app.errorhandler(ValidationError)
def handle_pydantic_validation_error(e: ValidationError):
    return jsonify(json.loads(e.json(include_context=False, include_url=False))), 400


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
    summary="List fighters",
    responses={200: ListFighterResponse},
    tags=[fighter_tag],
)
def api_list_fighters(query: ListFighterQuery):
    return jsonify(list_fighters(pg_pool, query).model_dump())


@app.get(
    "/api/fighter/<int:id_>/",
    summary="Get fighter",
    responses={200: FighterModel},
    tags=[fighter_tag],
)
def api_get_fighter(path: IdPath):
    if fighter := get_fighter_by_id(pg_pool, path.id_):
        return jsonify(fighter.model_dump())
    return "Fighter not found", 404


# Matches
@app.get(
    "/api/match/",
    summary="List matches",
    responses={200: ListMatchResponse},
    tags=[match_tag],
)
def api_list_matches(query: ListMatchQuery):
    return jsonify(list_matches(pg_pool, query).model_dump())


@app.get(
    "/api/match/<int:id_>/",
    summary="Get match",
    responses={200: MatchModel},
    tags=[match_tag],
)
def api_get_match(path: IdPath):
    if match_ := get_match_by_id(pg_pool, path.id_):
        return jsonify(match_.model_dump())
    return "Match not found", 404


@app.get(
    "/api/last_match/",
    summary="Get the last played match",
    responses={200: MatchModel},
    tags=[match_tag],
)
def api_last_match():
    if match_ := get_last_match(pg_pool):
        return jsonify(match_.model_dump())
    return jsonify({})


# Current Match Info
@app.get(
    "/current-match",
    summary="[DEPRECATED] Current Match Information",
    tags=[current_match_tag],
    deprecated=True,
    responses={200: CurrentMatchInfoResponse},
)
def api_current_match_info():
    if current_match_info := get_current_match_info(pg_pool):
        return jsonify(current_match_info.model_dump())
    return jsonify({})


# @app.get("/current_match_info")

# === Flasgger ===
# app.config["SWAGGER"] = {
#     "title": "SaltyBoy",
#     "openapi": "3.0.0",
#     "termsOfService": "/",
#     "specs": [
#         {
#             "version": "1.0.0",
#             "title": "SaltyBoy API",
#             "endpoint": "saltyboy_spec",
#             "route": "/spec",
#         },
#     ],
#     "servers": [{"url": os.environ.get("SWAGGER_SERVER") or "http://localhost:5000"}],
# }
# spec = APISpec(
#     title="SaltyBoy API",
#     version="1.0.0",
#     openapi_version="3.0.2",
#     description="https://github.com/FranciscoAT/saltyboy",
#     plugins=[FlaskPlugin(), DataclassesPlugin()],
# )
# spec.components.schema("FighterInfoSchema", schema=FighterInfoSchema)
# spec.components.schema("CurrentMatchSchema", schema=CurrentMatchSchema)
# spec.components.schema("DatabaseStatsSchema", schema=DatabaseStatsSchema)
# spec.components.schema("EnhancedMatchSchema", schema=EnhancedMatchSchema)

# template = apispec_to_template(app=app, spec=spec, paths=[get_fighter_request])

# swagger = Swagger(app, template=template)
