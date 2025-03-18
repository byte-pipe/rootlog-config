#!/usr/bin/env python3
import logging

from logger import check_registered_loggers, setup_logger

setup_logger(script=__file__, log_c=True, level_c=logging.DEBUG)


class Animal:
    def __init__(self, name):
        logging.debug(f"Initializing {self.__class__.__name__}")
        self.name = name

    def make_sound(self):
        logging.debug("")
        return "Some generic animal sound"


class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        logging.debug(f"Initializing {self.__class__.__name__}")
        self.breed = breed

    def make_sound(self):
        logging.debug("")
        return "Woof"


if __name__ == "__main__":
    try:
        check_registered_loggers()
        logging.info("start")
        a = Animal("Generic")
        d = Dog("Fido", "Labrador")
        logging.info(a.make_sound())
        logging.debug(d.make_sound())
        logging.debug("end")
        logging.warning("this is how warning looks like")
        logging.error("this is how error looks like")
        logging.critical("this is how critical looks like")
        check_registered_loggers()
    except Exception as e:
        logging.error(e.__str__())
        raise e
