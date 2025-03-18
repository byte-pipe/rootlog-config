import logging

from logger.module_examples.animal import Animal


class Cat(Animal):
    """Cat extends Animal and provides cat-specific logging."""

    def __init__(self, name: str):
        super().__init__(name)
        logging.info(f"Cat created: {self.name}")

    def make_sound(self):
        """Override make_sound to log and return a cat meow."""
        sound = "Meow"
        logging.debug(f"Cat {self.name} makes sound: {sound}")
        return sound
