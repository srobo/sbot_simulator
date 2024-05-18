from abc import ABC, abstractmethod
from enum import Enum

from sbot_interface.devices.led import Led as _Led
from sbot_interface.devices.util import WebotsDevice, get_globals, get_robot_device, map_to_range

ANALOG_MAX = 1023

class GPIOPinMode(str, Enum):
    """The possible modes for a GPIO pin."""
    INPUT = 'INPUT'
    INPUT_PULLUP = 'INPUT_PULLUP'
    OUTPUT = 'OUTPUT'


class BasePin(ABC):
    @abstractmethod
    def get_mode(self) -> GPIOPinMode:
        pass

    @abstractmethod
    def set_mode(self, mode: GPIOPinMode) -> None:
        pass

    @abstractmethod
    def get_digital(self) -> bool:
        pass

    @abstractmethod
    def set_digital(self, value: bool) -> None:
        pass

    @abstractmethod
    def get_analog(self) -> int:
        pass


class EmptyPin(BasePin):
    def __init__(self) -> None:
        self._mode = GPIOPinMode.INPUT
        self._digital = False
        self._analog = 0

    def get_mode(self) -> GPIOPinMode:
        return self._mode

    def set_mode(self, mode: GPIOPinMode) -> None:
        self._mode = mode

    def get_digital(self) -> bool:
        return self._digital

    def set_digital(self, value: bool) -> None:
        self._digital = value

    def get_analog(self) -> int:
        return self._analog


class UltrasonicSensor(BasePin):
    def __init__(self, device_name: str) -> None:
        g = get_globals()
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.DistanceSensor)
        self._device.enable(g.timestep)
        self._mode = GPIOPinMode.INPUT

    def get_mode(self) -> GPIOPinMode:
        return self._mode

    def set_mode(self, mode: GPIOPinMode) -> None:
        self._mode = mode

    def get_digital(self) -> bool:
        return False

    def set_digital(self, value: bool) -> None:
        pass

    def get_analog(self) -> int:
        return 0

    def get_distance(self) -> int:
        # Relies on the lookup table mapping to the distance in mm
        return int(self._device.getValue())


class MicroSwitch(BasePin):
    def __init__(self, device_name: str) -> None:
        g = get_globals()
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.TouchSensor)
        self._device.enable(g.timestep)
        self._mode = GPIOPinMode.INPUT

    def get_mode(self) -> GPIOPinMode:
        return self._mode

    def set_mode(self, mode: GPIOPinMode) -> None:
        self._mode = mode

    def get_digital(self) -> bool:
        return bool(self._device.getValue())

    def set_digital(self, value: bool) -> None:
        pass

    def get_analog(self) -> int:
        return 1023 if self._digital else 0


class PressureSensor(BasePin):
    # Use lookupTable [0 0 0, 50 1023 0] // 50 Newton max force
    def __init__(self, device_name: str) -> None:
        g = get_globals()
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.TouchSensor)
        self._device.enable(g.timestep)
        self._mode = GPIOPinMode.INPUT

    def get_mode(self) -> GPIOPinMode:
        return self._mode

    def set_mode(self, mode: GPIOPinMode) -> None:
        self._mode = mode

    def get_digital(self) -> bool:
        return self.get_analog() > ANALOG_MAX / 2

    def set_digital(self, value: bool) -> None:
        pass

    def get_analog(self) -> int:
        return int(self._device.getValue())


class ReflectanceSensor(BasePin):
    def __init__(self, device_name: str) -> None:
        g = get_globals()
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.Camera)
        self._mode = GPIOPinMode.INPUT

    def get_mode(self) -> GPIOPinMode:
        return self._mode

    def set_mode(self, mode: GPIOPinMode) -> None:
        self._mode = mode

    def get_digital(self) -> bool:
        return self.get_analog() > ANALOG_MAX / 2

    def set_digital(self, value: bool) -> None:
        pass

    def get_analog(self) -> int:
        image = self._device.getImage()
        grey_val = self._device.imageGetGray(image, self._device.getWidth(), 0, 0)
        return map_to_range((0, 255), (0, ANALOG_MAX), grey_val)


class Led(BasePin):
    def __init__(self, device_name: str) -> None:
        self._led = _Led(device_name)
        self._mode = GPIOPinMode.OUTPUT

    def get_mode(self) -> GPIOPinMode:
        return self._mode

    def set_mode(self, mode: GPIOPinMode) -> None:
        self._mode = mode

    def get_digital(self) -> bool:
        return self._led.get_colour() > 0

    def set_digital(self, value: bool) -> None:
        self._led.set_colour(1 if value else 0)

    def get_analog(self) -> int:
        return 0
