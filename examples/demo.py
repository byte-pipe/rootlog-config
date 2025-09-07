#!/usr/bin/env python3
"""Demo script showing logger usage examples."""
import logging
import threading

from logger import check_registered_loggers, setup_logger


def test_simple():
    """Simple logging example."""
    setup_logger()
    logging.debug("This is a debug message")
    logging.info("This is an info message")
    logging.warning("This is a warning message")
    logging.error("This is an error message")
    logging.critical("This is a critical message")


def test_across_threads():
    """Example of logging across multiple threads."""

    def module_a_do_something():
        logging.debug("Module A: Debug message")
        logging.info("Module A: Info message")
        logging.warning("Module A: Warning message")

    def module_b_do_something():
        logging.debug("Module B: Debug message")  # this should not appear as the root logger level is INFO
        logging.info("Module B: Info message")
        logging.warning("Module B: Warning message")

    setup_logger(level_c=logging.INFO)
    logging.debug("Main: Debug message (should not appear)")
    logging.info("Main: Info message")
    logging.warning("Main: Warning message")
    module_a_do_something()  # Log from imported module
    thread = threading.Thread(target=module_b_do_something)  # Log from module_b in a thread
    check_registered_loggers()
    thread.start()
    thread.join()


if __name__ == "__main__":
    print("Testing simple logging...")
    test_simple()
    print("\nTesting threaded logging...")
    test_across_threads()
