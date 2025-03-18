#!/usr/bin/env python3
import logging

from logger import setup_logger

setup_logger(script=__file__, level_c=logging.DEBUG, level_f=logging.DEBUG, log_c=True)
if __name__ == "__main__":
    for i in range(10):
        logging.info(f"[{i}] this is logged")
