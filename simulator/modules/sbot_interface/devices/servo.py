from abc import ABC, abstractmethod

from sbot_interface.devices.util import WebotsDevice, add_jitter, get_globals, get_robot_device, map_to_range

MAX_POSITION = 2000
MIN_POSITION = 1000


class BaseServo(ABC):
    @abstractmethod
    def disable(self) -> None:
        pass

    @abstractmethod
    def set_position(self, value: int) -> None:
        pass

    @abstractmethod
    def get_position(self) -> int:
        pass

    @abstractmethod
    def get_current(self) -> int:
        pass

    @abstractmethod
    def enabled(self) -> bool:
        pass


class NullServo(BaseServo):
    def __init__(self) -> None:
        self.position = 1500
        self._enabled = False

    def disable(self) -> None:
        self._enabled = False

    def set_position(self, value: int) -> None:
        self.position = value
        self._enabled = True

    def get_position(self) -> int:
        return self.position

    def get_current(self) -> int:
        return 0

    def enabled(self) -> bool:
        return self._enabled


class Servo(BaseServo):
    def __init__(self, device_name: str) -> None:
        self.position = (MAX_POSITION + MIN_POSITION) // 2
        # TODO use setAvailableForce to simulate disabled
        self._enabled = False
        g = get_globals()
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.Motor)
        self._max_position = self._device.getMaxPosition()
        self._min_position = self._device.getMinPosition()

    def disable(self) -> None:
        self._enabled = False

    def set_position(self, value: int) -> None:
        # Apply a small amount of variation to the power setting to simulate inaccuracies in the servo
        value = add_jitter(value, (MIN_POSITION, MAX_POSITION))

        self._device.setPosition(map_to_range(
            value,
            (MIN_POSITION, MAX_POSITION),
            (self._min_position + 0.001, self._max_position - 0.001),
        ))
        self.position = value
        self._enabled = True

    def get_position(self) -> int:
        return self.position

    def get_current(self) -> int:
        # TODO calculate from torque feedback
        return 0

    def enabled(self) -> bool:
        return self._enabled
