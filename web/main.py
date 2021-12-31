from argparse import ArgumentParser
from dataclasses import asdict
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
from typing import Optional

from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from dataclasses_jsonschema.apispec import DataclassesPlugin
from dotenv import load_dotenv
from flasgger import Swagger
from flasgger.utils import apispec_to_template
from flask import Flask, request
from flask.helpers import send_file
from flask.json import jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound

from src.biz import database as database_biz, fighter as fighter_biz, match as match_biz
from src.schemas.database import DatabaseStatsSchema
from src.schemas.fighters import FighterInfoSchema, GetFighterQuerySchema
from src.schemas.match import CurrentMatchSchema


load_dotenv()
app = Flask(__name__)
CORS(app, origins=["https://saltybet.com", "https://salty-boy.com"])

# --- Generic Web Stuff --
@app.route("/", methods=["GET"])
def get_index_request():
    return send_file("public/index.html", mimetype="text/html")


@app.route("/favicon.ico", methods=["GET"])
def get_favicon_request():
    return send_file("public/favicon.ico", mimetype="image/vdn.microsoft.icon")


@app.route("/robots.txt", methods=["GET"])
def get_robots_request():
    return send_file("public/robots.txt", mimetype="text/plain")


# --- API stuff ---
@app.route("/stats", methods=["GET"])
def get_db_stats_request():
    """
    Get information about the database records
    Returns a breakdown of how many matches and fighters the database has cataloged.
    Along with a breakdown of each based off of tier.
    Tiers should be all one of: A, B, P, S, X.
    ---
    description: Get database stats
    responses:
      200:
        description: Database stats
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DatabaseStatsSchema'
    """
    return jsonify(asdict(database_biz.get_db_stats()))


@app.route("/fighters", methods=["GET"])
def get_fighter_request():
    """
    Get information about a fighter.
    Requires either an `id` or a `name` as query parameters.
    ---
    description: Get a fighter
    parameters:
      - name: id
        in: query
        description: Fighter database ID
        schema:
          type: integer
      - name: name
        in: query
        description: Fighter name, case sensitive
        schema:
          type: string
    responses:
      200:
        description: Fighter info
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/FighterInfoSchema'
      400:
        description: Bad Request
      404:
        description: Fighter not found
    """
    try:
        query_params = GetFighterQuerySchema(
            fighter_id=request.args.get("id"), fighter_name=request.args.get("name")
        )
    except ValueError as e:
        raise BadRequest(str(e))

    fighter = fighter_biz.get_fighter(
        fighter_id=query_params.fighter_id, fighter_name=query_params.fighter_name
    )

    if not fighter:
        return NotFound("No fighter found")

    return jsonify(asdict(fighter))


@app.route("/current-match", methods=["GET"])
def get_current_match_request():
    """
    Return information about current match
    Current match information shown is updated regularly based off of the bot service.
    Match info will never display fighter information for exhibition matches.
    ---
    responses:
      200:
        description: Current match information
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CurrentMatchSchema'
      204:
        description: No current match exists
    """
    current_match = match_biz.get_current_match()
    if not current_match:
        return "", 204
    return jsonify(asdict(current_match))


# --- Flasgger ---
app.config["SWAGGER"] = {
    "title": "SaltyBoy",
    "openapi": "3.0.0",
    "termsOfService": "/",
    "specs": [
        {
            "version": "0.0.1",
            "title": "SaltyBoy API",
            "endpoint": "saltyboy_spec",
            "route": "/spec",
        },
    ],
    "servers": [{"url": os.environ.get("SWAGGER_SERVER") or "http://localhost:5000"}],
}
spec = APISpec(
    title="SaltyBoy API",
    version="0.0.1",
    openapi_version="3.0.2",
    description="https://github.com/FranciscoAT/saltyboy",
    plugins=[FlaskPlugin(), DataclassesPlugin()],
)
spec.components.schema("FighterInfoSchema", schema=FighterInfoSchema)
spec.components.schema("CurrentMatchSchema", schema=CurrentMatchSchema)
spec.components.schema("DatabaseStatsSchema", schema=DatabaseStatsSchema)

template = apispec_to_template(app=app, spec=spec, paths=[get_fighter_request])

swagger = Swagger(app, template=template)


def _init_loggers(set_debug: bool, log_path: Optional[str] = None) -> None:
    log_level = logging.INFO
    if set_debug:
        log_level = logging.DEBUG

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    log_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s:%(lineno)s - %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(log_formatter)

    root_logger.addHandler(stream_handler)

    if log_path:
        path = Path(log_path)
        if not path.exists():
            root_logger.error("Path %s, does not exist", log_path)
            exit(1)
        if not path.is_dir():
            root_logger.error("Path %s, is not a directory", log_path)

        timed_rotating_fh = TimedRotatingFileHandler(
            filename=f"{log_path}/saltyweb.log",
            utc=True,
            backupCount=3,
            when="midnight",
        )
        timed_rotating_fh.setFormatter(log_formatter)
        root_logger.addHandler(timed_rotating_fh)
        root_logger.info("Will log to a timed rotating file at: %s", log_path)

    if set_debug:
        root_logger.info("Log level set to DEBUG.")
    else:
        root_logger.info("Log level set to INFO.")


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug logging"
    )
    arg_parser.add_argument(
        "-lp", "--log-path", help="Sets a rotating file handler at the given path"
    )

    arguments = arg_parser.parse_args()
    _init_loggers(arguments.debug, log_path=arguments.log_path)

    mode = os.environ.get("DEPLOYMENT_MODE")

    if mode == "PROD":
        from waitress import serve
        from paste.translogger import TransLogger

        logging.info("Running in production mode")
        app.debug = False
        serve(
            TransLogger(app, setup_console_handler=False),
            host="0.0.0.0",
            port=5000,
            url_scheme="https",
        )
    else:
        logging.info("Running in development mode")
        app.run(debug=True, host="localhost", port=5000)
