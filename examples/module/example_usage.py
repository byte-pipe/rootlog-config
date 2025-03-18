import logging

from logger import setup_logger
from logger.module_examples.cat import Cat
from logger.module_examples.dog import Dog

# Set up the root logger once at the entry point
# WARNING: Do not pass logger_name unless you specifically need a named logging.
# Using module names (__name__) or other names can create unwanted logger hierarchies.
setup_logger(script=__file__)


def main():
    # Set up some animals
    dog = Dog("Buddy")
    cat = Cat("Whiskers")

    # Make them do things
    logging.info("Making animals produce sounds...")

    dog.make_sound()  # This will log at DEBUG level
    cat.make_sound()  # This will log at DEBUG level

    logging.info("Animal sound demonstration completed!")


if __name__ == "__main__":
    main()
