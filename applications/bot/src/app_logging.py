import logging
import logging.handlers
import os
from multiprocessing import Queue
from pathlib import Path
from time import sleep


def run_listener(queue: Queue, log_path: Path | None) -> None:
    log_formatter = logging.Formatter(
        "%(asctime)s %(processName)s - %(levelname)s - %(name)s [%(filename)s:%(lineno)s] - %(message)s"
    )

    # Initiate the root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)
    log_level = _get_log_level()
    root_logger.setLevel(log_level)

    # Add a stream handler to the root logger
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(log_formatter)
    root_logger.addHandler(stream_handler)

    if log_path:
        timed_rotating_fh = logging.handlers.TimedRotatingFileHandler(
            filename=f"{log_path}/saltybot.log",
            utc=True,
            backupCount=3,
            when="midnight",
        )
        timed_rotating_fh.setFormatter(log_formatter)
        root_logger.addHandler(timed_rotating_fh)
        root_logger.info("Will log to a time rotating file at: %s", log_path.resolve())

    root_logger.info("Log level set to: %s", logging.getLevelName(log_level))

    while True:
        while not queue.empty():
            record = queue.get()
            logger = logging.getLogger(record.name)
            logger.handle(record)
        sleep(1)


def get_watchdog_logger() -> logging.Logger:
    return _get_cleaned_logger("watchdog")[0]


def get_bot_logger() -> logging.Logger:
    return _get_cleaned_logger("bot")[0]


def configure_process_logger(queue: Queue) -> None:
    root_logger, handler_registered = _get_cleaned_logger()

    if handler_registered is True:
        return

    handler = logging.handlers.QueueHandler(queue)
    root_logger.addHandler(handler)
    root_logger.setLevel(_get_log_level())


def _get_cleaned_logger(name: str | None = None) -> tuple[logging.Logger, bool]:
    logger = logging.getLogger(name)

    handler_registered = False
    for handler in logger.handlers:
        if isinstance(handler, logging.handlers.QueueHandler):
            handler_registered = True
            continue
        logger.removeHandler(handler)

    return logger, handler_registered


def _get_log_level() -> int:
    return logging.DEBUG if os.environ.get("DEBUG") else logging.INFO
