from argparse import ArgumentParser
import logging

from dotenv import load_dotenv

from src.run import run


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "-d", "--debug", action="store_true", help="Run in debug mode"
    )

    arguments = arg_parser.parse_args()

    log_level = logging.INFO
    if arguments.debug:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(name)s:%(lineno)s - %(message)s",
    )

    if arguments.debug:
        logging.info("Running in debug mode.")

    load_dotenv()
    run()
