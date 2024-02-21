import logging
import os
import sys
from argparse import ArgumentParser
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

from src.run import run


def _init_loggers(set_debug: bool, log_path: str | None = None) -> None:
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
            sys.exit(1)
        if not path.is_dir():
            root_logger.error("Path %s, is not a directory", log_path)

        timed_rotating_fh = TimedRotatingFileHandler(
            filename=f"{log_path}/saltybot.log",
            utc=True,
            backupCount=3,
            when="midnight",
        )
        timed_rotating_fh.setFormatter(log_formatter)
        root_logger.addHandler(timed_rotating_fh)
        root_logger.info("Will log to a time rotating file at: %s", log_path)

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
        "-l",
        "--logs",
        help="Sets a rotating file handler at the given path",
    )

    arguments = arg_parser.parse_args()

    _init_loggers(arguments.debug, log_path=arguments.logs)
    logger = logging.getLogger()

    if os.environ.get("PRODUCTION") is None:
        env_file_path = Path(__file__).parent.parent.parent / ".env"
        logger.info(
            "Non-prod mode. Loading environment file: %s", env_file_path.resolve()
        )
        load_dotenv(env_file_path)

    try:
        run()
    except Exception:
        logger.error("Something went wrong.", exc_info=True)
        raise
