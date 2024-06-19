"""
A wrapper for the Webots LED device.

Supports both single and multi-colour non-PWM LEDs.
"""
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
    """Base class for LED devices."""

    def __init__(self) -> None:
        self.colour = 0

    @abstractmethod
    def set_colour(self, colour: int) -> None:
        """Set the colour of the LED."""
        pass

    @abstractmethod
    def get_colour(self) -> int:
        """Get the colour of the LED."""
        pass


class NullLed(BaseLed):
    """Null LED device. Allows the robot to run without an LED device attached."""

    def __init__(self) -> None:
        self.colour = 0

    def set_colour(self, colour: int) -> None:
        """Set the colour of the LED."""
        self.colour = colour

    def get_colour(self) -> int:
        """Get the colour of the LED."""
        return self.colour


class Led(BaseLed):
    """
    A wrapper for the Webots LED device.

    :param device_name: The name of the LED device.
    :param num_colours: The number of colours the LED supports.
    """

    def __init__(self, device_name: str, num_colours: int = 1) -> None:
        g = get_globals()
        self.num_colours = num_colours
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.LED)

    def set_colour(self, colour: int) -> None:
        """
        Set the colour of the LED.

        :param colour: The colour to set the LED to. A 1-based index for the lookup
                       table of the LED. 0 is OFF.
        """
        if 0 <= colour < self.num_colours:
            # NOTE: value 0 is OFF
            self._device.set(colour)
        else:
            raise ValueError(f'Invalid colour: {colour}')

    def get_colour(self) -> int:
        """
        Get the colour of the LED.

        :return: The colour of the LED. A 1-based index for the lookup table of the LED.
                 0 is OFF.
        """
        # webots uses 1-based indexing
        return self._device.get()
