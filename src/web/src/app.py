import json
import os
from pathlib import Path

import psycopg2
from apispec import APISpec
from dataclasses_jsonschema.apispec import DataclassesPlugin
from flasgger import Swagger
from flasgger.utils import apispec_to_template
from flask import Flask, request
from flask.helpers import send_file
from flask.json import jsonify
from flask_cors import CORS
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest, NotFound

from src.biz_new import get_fighter_by_id, list_fighters, get_match_by_id, list_matches
from src.schemas import ListFighterQuery, ListMatchQuery

app = Flask(__name__)
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


# === Handlers ===
@app.errorhandler(ValidationError)
def handle_pydantic_validation_error(e: ValidationError):
    return jsonify(json.loads(e.json(include_context=False, include_url=False))), 400


# === Web Endpoints ===
@app.route("/", methods=["GET"])
def get_index_request():
    return send_file(
        Path(__file__).parent.parent / "public/index.html", mimetype="text/html"
    )


@app.route("/favicon.ico", methods=["GET"])
def get_favicon_request():
    return send_file(
        Path(__file__).parent.parent / "public/favicon.ico",
        mimetype="image/vdn.microsoft.icon",
    )


@app.route("/robots.txt", methods=["GET"])
def get_robots_request():
    return send_file(
        Path(__file__).parent.parent / "public/robots.txt", mimetype="text/plain"
    )


# === API Endpoints ===
# Fighters
@app.route("/fighter", methods=["GET"])
def route_list_fighters():
    return jsonify(
        list_fighters(pg_pool, ListFighterQuery(**request.args)).model_dump()
    )


@app.route("/fighter/<int:id_>")
def get_fighter(id_: int):
    if fighter := get_fighter_by_id(pg_pool, id_):
        return jsonify(fighter.model_dump())
    return "Fighter not found", 404


# Matches
@app.route("/match", methods=["GET"])
def route_list_matches():
    return jsonify(list_matches(pg_pool, ListMatchQuery(**request.args)).model_dump())


@app.route("/match/<int:id_>")
def get_match(id_: int):
    if match_ := get_match_by_id(pg_pool, id_):
        return jsonify(match_.model_dump())
    return "Match not found", 404


# @app.route("/current-match", methods=["GET"])
# def get_current_match_request():
#     """
#     Return information about current match
#     Current match information shown is updated regularly based off of the bot service.
#     Match info will never display fighter information for exhibition matches.
#     ---
#     responses:
#       200:
#         description: Current match information
#         content:
#           application/json:
#             schema:
#               $ref: '#/components/schemas/CurrentMatchSchema'
#       204:
#         description: No current match exists
#     """
#     current_match = match_biz.get_current_match()
#     if not current_match:
#         return "", 204
#     return jsonify(asdict(current_match))


# @app.route("/last-match", methods=["GET"])
# def get_last_match_request():
#     """
#     Return information about the last recorded match
#     ---
#     responses:
#       200:
#         description: Last matched played information
#         content:
#           application/json:
#             schema:
#               $ref: '#/components/schemas/EnhancedMatchSchema'
#       204:
#         description: No latest match recorded
#     """
#     last_match = match_biz.get_last_match()
#     if not last_match:
#         return "", 204
#     return jsonify(asdict(last_match))


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
