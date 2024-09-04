import logging
import sys


def get_logger(name: str) -> logging.Logger:
    StdOutHandler = logging.StreamHandler(sys.stdout)
    StdOutHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)s | %(levelname)s >>> %(message)s')
    StdOutHandler.setFormatter(formatter)
    StdOutHandler.setStream(stream=sys.stdout)

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(name)
    logger.addHandler(StdOutHandler)
    return logger
