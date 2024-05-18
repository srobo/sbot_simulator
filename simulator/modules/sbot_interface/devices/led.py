from abc import ABC, abstractmethod

from sbot_interface.devices.util import WebotsDevice, get_globals, get_robot_device

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


class NullLed(BaseLed):
    def __init__(self):
        self.colour = 0

    def set_colour(self, colour: int) -> None:
        self.colour = colour

    def get_colour(self) -> int:
        return self.colour


class Led(BaseLed):
    def __init__(self, device_name: str, num_colours: int = 1) -> None:
        g = get_globals()
        self.num_colours = num_colours
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.LED)

    def set_colour(self, colour: int) -> None:
        if 0 <= colour < self.num_colours:
            # NOTE: value 0 is OFF
            self._device.set(colour)
        else:
            raise ValueError(f'Invalid colour: {colour}')

    def get_colour(self) -> int:
        # webots uses 1-based indexing
        return self._device.get()
