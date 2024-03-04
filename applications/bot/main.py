import logging
import os
from argparse import ArgumentParser
from pathlib import Path

from dotenv import load_dotenv

from src.run import run

if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help=(
            "Enable debug logging. Optionally, you can set DEBUG=1 in the environment."
        ),
    )
    arg_parser.add_argument(
        "-l",
        "--logs",
        help="Sets a rotating file handler at the given path",
    )

    arguments = arg_parser.parse_args()

    if arguments.debug:
        os.environ["DEBUG"] = "1"

    log_path: Path | None = None
    if arguments.logs:
        log_path = Path(arguments.logs)
        if not log_path.is_dir():
            raise ValueError(
                f"Invalid value for logs: {log_path.resolve()}, not a directory!"
            )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if os.environ.get("PRODUCTION") is None:
        env_file_path = Path(__file__).parent.parent.parent / ".env"
        root_logger.info(
            "Non-prod mode. Loading environment file: %s", env_file_path.resolve()
        )
        load_dotenv(env_file_path)

    try:
        run(log_path)
    except Exception:
        root_logger.error("Something went wrong.", exc_info=True)
        raise
