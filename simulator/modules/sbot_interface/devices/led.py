from abc import ABC, abstractmethod

RGB_COLOURS = [
    (False, False, False),  # OFF
    (True, False, False),  # RED
    (True, True, False),  # YELLOW
    (False, True, False),  # GREEN
    (False, True, True),  # CYAN
    (False, False, True),  # BLUE
    (True, False, True),  # MAGENTA
    (True, True, True),  # WHITE
]


class BaseLed(ABC):
    def __init__(self):
        self.colour = 0

    @abstractmethod
    def set_colour(self, colour: int) -> None:
        pass

    @abstractmethod
    def get_colour(self) -> int:
        pass
