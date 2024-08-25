"""
A wrapper for the Webots motor device.

The motor will apply a small amount of variation to the power setting to simulate
inaccuracies in the motor.
"""
import logging
from abc import ABC, abstractmethod

from sbot_interface.devices.util import (
    WebotsDevice,
    add_jitter,
    get_globals,
    get_robot_device,
    map_to_range,
)

MAX_POWER = 1000
MIN_POWER = -1000


class BaseMotor(ABC):
    """Base class for motor devices."""

    @abstractmethod
    def disable(self) -> None:
        """Disable the motor."""
        pass

    @abstractmethod
    def set_power(self, value: int) -> None:
        """Set the power of the motor (±1000)."""
        pass

    @abstractmethod
    def get_power(self) -> int:
        """Get the power of the motor."""
        pass

    @abstractmethod
    def get_current(self) -> int:
        """Get the current draw of the motor in mA."""
        pass

    @abstractmethod
    def enabled(self) -> bool:
        """Check if the motor is enabled."""
        pass


class NullMotor(BaseMotor):
    """Null motor device. Allows the robot to run without a motor device attached."""

    def __init__(self) -> None:
        self.power = 0
        self._enabled = False

    def disable(self) -> None:
        """Disable the motor."""
        self._enabled = False

    def set_power(self, value: int) -> None:
        """Set the power of the motor."""
        self.power = value
        self._enabled = True

    def get_power(self) -> int:
        """Get the power of the motor."""
        return self.power

    def get_current(self) -> int:
        """Get the current draw of the motor in mA."""
        return 0

    def enabled(self) -> bool:
        """Check if the motor is enabled."""
        return self._enabled


class Motor(BaseMotor):
    """
    A wrapper for the Webots motor device.

    The motor will apply a small amount of variation to the power setting to simulate
    inaccuracies in the motor.

    :param device_name: The name of the motor device.
    """

    def __init__(self, device_name: str) -> None:
        self.power = 0
        self._enabled = False
        g = get_globals()
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.Motor)
        # Put the motor in velocity control mode
        self._device.setPosition(float('inf'))
        self._device.setVelocity(0)
        self._max_speed = self._device.getMaxVelocity()
        # Limit the torque the motor can apply to have realistic acceleration
        self._device.setAvailableTorque(1)

    def disable(self) -> None:
        """Disable the motor."""
        self._device.setVelocity(0)
        self._enabled = False

    def set_power(self, value: int) -> None:
        """
        Set the power of the motor.

        :param value: The power setting for the motor. A value between -1000 and 1000.
        """
        if value != 0:
            if abs(value) < 0.05:
                logging.warning(
                    "Motor power is too low, values below 0.05 will not move the motor."
                )
                value = 0
            else:
                # Apply a small amount of variation to the power setting to simulate
                # inaccuracies in the motor
                value = int(add_jitter(value, (MIN_POWER, MAX_POWER), std_dev_percent=1))

        self._device.setVelocity(map_to_range(
            value,
            (MIN_POWER, MAX_POWER),
            (-self._max_speed, self._max_speed),
        ))
        self.power = value
        self._enabled = True

    def get_power(self) -> int:
        """
        Get the power of the motor.

        :return: The power setting for the motor. A value between -1000 and 1000.
        """
        return self.power

    def get_current(self) -> int:
        """
        Get the current draw of the motor in mA.

        :return: The current draw of the motor in mA.
        """
        # TODO calculate from torque feedback
        return 0

    def enabled(self) -> bool:
        """
        Check if the motor is enabled.

        :return: True if the motor is enabled, False otherwise.
        """
        return self._enabled
