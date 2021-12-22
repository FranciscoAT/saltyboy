from argparse import ArgumentParser
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from flask import Flask, request
from flask.helpers import send_file, send_from_directory, url_for
from flask.json import jsonify
from flask.templating import render_template
from marshmallow.exceptions import ValidationError
from werkzeug.exceptions import BadRequest, NotFound

from src import biz
from src.schemas import AnalyzeMatchSchema, GetFighterSchema


app = Flask(__name__)


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
    return jsonify(biz.get_db_stats())


@app.route("/fighters", methods=["GET"])
def get_fighter_request():
    query_params = GetFighterSchema().load(request.args)
    fighter = biz.get_fighter(**query_params)

    if not fighter:
        return NotFound("No fighter found.")

    return jsonify(fighter)


@app.route("/analyze", methods=["POST"])
def analyze_match_request():
    request_payload = request.json
    if not isinstance(request_payload, dict):
        raise BadRequest("Expecting a JSON object payload.")
    payload = AnalyzeMatchSchema().load(request_payload)
    result = biz.analyze_match(**payload)
    return jsonify(result)


@app.errorhandler(ValidationError)
def handle_validation_error(validation_error):
    response = jsonify(validation_error.messages)
    response.status_code = 400
    return response


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
        root_logger.info("Setting time rotating filehandler to path %s", log_path)

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

    load_dotenv()

    mode = os.environ.get("DEPLOYMENT_MODE")

    if mode == "PROD":
        from waitress import serve
        from paste.translogger import TransLogger

        logging.info("Running in production")
        app.debug = False
        serve(
            TransLogger(app, setup_console_handler=False),
            host="0.0.0.0",
            port=5000,
            url_scheme="https",
        )
    else:
        app.run(debug=True, host="localhost", port=5000)
