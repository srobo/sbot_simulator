"""
A wrapper for the Webots servo device.

The servo will apply a small amount of variation to the power setting to simulate
inaccuracies in the servo.
"""
from abc import ABC, abstractmethod

from sbot_interface.devices.util import (
    WebotsDevice,
    add_jitter,
    get_globals,
    get_robot_device,
    map_to_range,
)

MAX_POSITION = 2000
MIN_POSITION = 1000


class BaseServo(ABC):
    """The base class for all the servos that can be connected to the Servo board."""

    @abstractmethod
    def disable(self) -> None:
        """Disable the servo."""
        pass

    @abstractmethod
    def set_position(self, value: int) -> None:
        """
        Set the position of the servo.

        Position is the pulse width in microseconds.
        """
        pass

    @abstractmethod
    def get_position(self) -> int:
        """Return the current position of the servo."""
        pass

    @abstractmethod
    def get_current(self) -> int:
        """Return the current draw of the servo in mA."""
        pass

    @abstractmethod
    def enabled(self) -> bool:
        """Return whether the servo is enabled."""
        pass


class NullServo(BaseServo):
    """A servo that does nothing. Used for servos that are not connected."""

    def __init__(self) -> None:
        self.position = 1500
        self._enabled = False

    def disable(self) -> None:
        """Disable the servo."""
        self._enabled = False

    def set_position(self, value: int) -> None:
        """
        Set the position of the servo.

        Position is the pulse width in microseconds.
        """
        self.position = value
        self._enabled = True

    def get_position(self) -> int:
        """
        Return the current position of the servo.

        Position is the pulse width in microseconds.
        """
        return self.position

    def get_current(self) -> int:
        """Return the current draw of the servo in mA."""
        return 0

    def enabled(self) -> bool:
        """Return whether the servo is enabled."""
        return self._enabled


class Servo(BaseServo):
    """A servo connected to the Servo board."""

    def __init__(self, device_name: str) -> None:
        self.position = (MAX_POSITION + MIN_POSITION) // 2
        # TODO use setAvailableForce to simulate disabled
        self._enabled = False
        g = get_globals()
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.Motor)
        self._max_position = self._device.getMaxPosition()
        self._min_position = self._device.getMinPosition()

    def disable(self) -> None:
        """Disable the servo."""
        self._enabled = False

    def set_position(self, value: int) -> None:
        """
        Set the position of the servo.

        Position is the pulse width in microseconds.
        """
        # Apply a small amount of variation to the power setting to simulate
        # inaccuracies in the servo
        value = int(add_jitter(value, (MIN_POSITION, MAX_POSITION), std_dev_percent=0.5))

        self._device.setPosition(map_to_range(
            value,
            (MIN_POSITION, MAX_POSITION),
            (self._min_position + 0.001, self._max_position - 0.001),
        ))
        self.position = value
        self._enabled = True

    def get_position(self) -> int:
        """
        Return the current position of the servo.

        Position is the pulse width in microseconds.
        """
        return self.position

    def get_current(self) -> int:
        """Return the current draw of the servo in mA."""
        # TODO calculate from torque feedback
        return 0

    def enabled(self) -> bool:
        """Return whether the servo is enabled."""
        return self._enabled
