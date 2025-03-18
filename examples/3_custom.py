#!/usr/bin/env python3
import logging

from logger import setup_logger

logger = setup_logger(logger_name="root")

# Create a custom logger for birds
bird_logger = logging.getLogger("bird")
bird_logger.setLevel(logging.DEBUG)

# bird_logger = setup_logger(logger_name="bird")


class Bird:
    def __init__(self, name):
        # Using the bird-specific logger
        bird_logger.info(f"Initializing {self.__class__.__name__}")
        bird_logger.debug(f"Initializing {self.__class__.__name__}")

        # Using the root logger
        logger.info(f"Initializing {self.__class__.__name__}")
        logger.debug(f"Initializing {self.__class__.__name__}")
        self.name = name


if __name__ == "__main__":
    try:
        b = Bird("some bird")
    except Exception as e:
        logger.error(e.__str__())
        raise e
