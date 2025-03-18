import logging


class Animal:
    """A generic Animal class utilizing the root logging."""

    def __init__(self, name: str):
        self.name = name
        logging.info(f"Animal created: {self.name}")

    def make_sound(self):
        """Default sound method; subclasses may override this."""
        logging.info(f"Animal {self.name} is making an ambiguous sound.")
        return "Some Sound"
