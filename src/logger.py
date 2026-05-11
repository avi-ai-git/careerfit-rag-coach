# Shared logger factory used across all src modules.
# Writing to stdout (not a file) means Streamlit Cloud captures logs automatically
# without any extra configuration.

import logging
import os


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, creating and configuring it on first call.

    The handler check prevents duplicate log lines when Streamlit re-runs
    the script on every user interaction -- without it, handlers stack up
    and each message prints multiple times.
    Set LOG_LEVEL=DEBUG in the environment to see retrieval and translation details.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # already configured -- adding another handler would duplicate every line

    level = logging.DEBUG if os.getenv("LOG_LEVEL", "").upper() == "DEBUG" else logging.INFO
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(handler)
    return logger


if __name__ == "__main__":
    log = get_logger("careerfit.test")
    log.info("logger initialised -- this is an INFO message")
    log.warning("this is a WARNING message")
