from argparse import ArgumentParser
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from src.run import run


def main() -> None:
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "-d", "--debug", action="store_true", help="Run in debug mode"
    )
    arg_parser.add_argument(
        "-lp",
        "--log-path",
        help="Sets a rotating file handler at the given path.",
    )

    arguments = arg_parser.parse_args()

    _init_loggers(arguments.debug, log_path=arguments.log_path)

    load_dotenv()
    try:
        run()
    except Exception:
        logger = logging.getLogger()
        logger.error("Something went wrong.", exc_info=True)
        raise


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
            filename=f"{log_path}/saltybot.log",
            utc=True,
            backupCount=3,
            when="midnight",
        )
        timed_rotating_fh.setFormatter(log_formatter)
        root_logger.addHandler(timed_rotating_fh)
        root_logger.info("Setting time rotating filehandler to path %s", log_path)

    if set_debug:
        root_logger.info("Running in debug mode.")


if __name__ == "__main__":
    main()
