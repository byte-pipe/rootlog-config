import logging

from logger.module_examples.animal import Animal


class Dog(Animal):
    """Dog extends Animal and provides dog-specific logging."""

    def __init__(self, name: str):
        super().__init__(name)
        logging.info(f"Dog created: {self.name}")

    def make_sound(self):
        """Override make_sound to log and return a dog bark."""
        sound = "Woof"
        logging.debug(f"Dog {self.name} makes sound: {sound}")
        return sound
