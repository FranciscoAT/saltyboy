from argparse import ArgumentParser
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

from src.run import run


if __name__ == "__main__":
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

    log_level = logging.INFO
    if arguments.debug:
        log_level = logging.DEBUG

    handlers = []
    if arguments.log_path:
        path = Path(arguments.log_path)
        if not path.exists():
            logging.error("Path %s, does not exist", arguments.log_path)
            exit(1)
        if not path.is_dir():
            logging.error("Path %s, is not a directory", arguments.log_path)

        handlers.append(
            TimedRotatingFileHandler(
                filename=f"{arguments.log_path}/saltybot.log",
                utc=True,
                backupCount=3,
                when="midnight",
            )
        )

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(name)s:%(lineno)s - %(message)s",
        handlers=handlers,
    )

    if arguments.debug:
        logging.info("Running in debug mode.")

    load_dotenv()
    try:
        run()
    except Exception:
        logging.error("Something went wrong.", exc_info=True)
        raise
