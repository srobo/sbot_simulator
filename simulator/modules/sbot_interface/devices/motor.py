from abc import ABC, abstractmethod

from sbot_interface.devices.util import WebotsDevice, get_globals, get_robot_device, map_to_range

MAX_POWER = 1000
MIN_POWER = -1000


class BaseMotor(ABC):
    @abstractmethod
    def disable(self) -> None:
        pass

    @abstractmethod
    def set_power(self, value: int) -> None:
        pass

    @abstractmethod
    def get_power(self) -> int:
        pass

    @abstractmethod
    def get_current(self) -> int:
        pass

    @abstractmethod
    def enabled(self) -> bool:
        pass


class NullMotor(BaseMotor):
    def __init__(self) -> None:
        self.power = 0
        self._enabled = False

    def disable(self) -> None:
        self._enabled = False

    def set_power(self, value: int) -> None:
        self.power = value
        self._enabled = True

    def get_power(self) -> int:
        return self.power

    def get_current(self) -> int:
        return 0

    def enabled(self) -> bool:
        return self._enabled


class Motor(BaseMotor):
    def __init__(self, device_name: str) -> None:
        self.power = 0
        self._enabled = False
        g = get_globals()
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.Motor)
        # Put the motor in velocity control mode
        self._device.setPosition(float('inf'))
        self._device.setVelocity(0)
        self._max_speed = self._device.getMaxVelocity()

    def disable(self) -> None:
        self._device.setVelocity(0)
        self._enabled = False

    def set_power(self, value: int) -> None:
        self._device.setVelocity(map_to_range(
            (MIN_POWER, MAX_POWER),
            (-self._max_speed, self._max_speed),
            value,
        ))
        self.power = value
        self._enabled = True

    def get_power(self) -> int:
        return self.power

    def get_current(self) -> int:
        # TODO calculate from torque feedback
        return 0

    def enabled(self) -> bool:
        return self._enabled
