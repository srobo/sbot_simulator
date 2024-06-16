"""A collection of wrappers for the devices that can be connected to the Arduino."""
from abc import ABC, abstractmethod
from enum import Enum

from sbot_interface.devices.led import Led as _Led
from sbot_interface.devices.util import WebotsDevice, get_globals, get_robot_device

ANALOG_MAX = 1023


class GPIOPinMode(str, Enum):
    """The possible modes for a GPIO pin."""

    INPUT = 'INPUT'
    INPUT_PULLUP = 'INPUT_PULLUP'
    OUTPUT = 'OUTPUT'


class BasePin(ABC):
    """The base class for all the devices that can be connected to the Arduino."""

    @abstractmethod
    def get_mode(self) -> GPIOPinMode:
        """Get the current mode of the pin."""
        pass

    @abstractmethod
    def set_mode(self, mode: GPIOPinMode) -> None:
        """Set the mode of the pin."""
        pass

    @abstractmethod
    def get_digital(self) -> bool:
        """Get the digital input value of the pin."""
        pass

    @abstractmethod
    def set_digital(self, value: bool) -> None:
        """Set the digital output value of the pin."""
        pass

    @abstractmethod
    def get_analog(self) -> int:
        """Get the analog input value of the pin."""
        pass


class EmptyPin(BasePin):
    """A pin that does nothing. Used for pins that are not connected."""

    def __init__(self) -> None:
        self._mode = GPIOPinMode.INPUT
        self._digital = False
        self._analog = 0

    def get_mode(self) -> GPIOPinMode:
        """Get the current mode of the pin."""
        return self._mode

    def set_mode(self, mode: GPIOPinMode) -> None:
        """Set the mode of the pin."""
        self._mode = mode

    def get_digital(self) -> bool:
        """Get the digital input value of the pin."""
        return self._digital

    def set_digital(self, value: bool) -> None:
        """Set the digital output value of the pin."""
        self._digital = value

    def get_analog(self) -> int:
        """Get the analog input value of the pin."""
        return self._analog


class UltrasonicSensor(BasePin):
    """
    A sensor that can measure the distance to an object.

    This is attached to the pin specified to be the echo pin, with the trigger pin unused.
    """

    def __init__(self, device_name: str) -> None:
        g = get_globals()
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.DistanceSensor)
        self._device.enable(g.timestep)
        self._mode = GPIOPinMode.INPUT

    def get_mode(self) -> GPIOPinMode:
        """Get the current mode of the pin."""
        return self._mode

    def set_mode(self, mode: GPIOPinMode) -> None:
        """Set the mode of the pin."""
        self._mode = mode

    def get_digital(self) -> bool:
        """Get the digital input value of the pin. This is always False."""
        return False

    def set_digital(self, value: bool) -> None:
        """
        Set the digital output value of the pin.

        This has no effect here.
        """
        pass

    def get_analog(self) -> int:
        """Get the analog input value of the pin. This is always 0."""
        return 0

    def get_distance(self) -> int:
        """
        Get the distance measured by the sensor in mm.

        Relies on the lookup table mapping to the distance in mm.
        """
        return int(self._device.getValue())


class MicroSwitch(BasePin):
    """A simple switch that can be pressed or released."""

    def __init__(self, device_name: str) -> None:
        g = get_globals()
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.TouchSensor)
        self._device.enable(g.timestep)
        self._mode = GPIOPinMode.INPUT

    def get_mode(self) -> GPIOPinMode:
        """Get the current mode of the pin."""
        return self._mode

    def set_mode(self, mode: GPIOPinMode) -> None:
        """Set the mode of the pin."""
        self._mode = mode

    def get_digital(self) -> bool:
        """Get the digital input value of the pin."""
        return bool(self._device.getValue())

    def set_digital(self, value: bool) -> None:
        """
        Set the digital output value of the pin.

        This has no effect here.
        """
        pass

    def get_analog(self) -> int:
        """Get the analog input value of the pin, either 0 or 1023."""
        return 1023 if self._digital else 0


class PressureSensor(BasePin):
    """
    A sensor that can measure the force applied to it.

    This is attached to the pin specified, with the force proportional to the analog value.
    """

    # Use lookupTable [0 0 0, 50 1023 0] // 50 Newton max force
    def __init__(self, device_name: str) -> None:
        g = get_globals()
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.TouchSensor)
        self._device.enable(g.timestep)
        self._mode = GPIOPinMode.INPUT

    def get_mode(self) -> GPIOPinMode:
        """Get the current mode of the pin."""
        return self._mode

    def set_mode(self, mode: GPIOPinMode) -> None:
        """Set the mode of the pin."""
        self._mode = mode

    def get_digital(self) -> bool:
        """
        Get the digital input value of the pin.

        True when the force is above half the maximum value.
        """
        return self.get_analog() > ANALOG_MAX / 2

    def set_digital(self, value: bool) -> None:
        """
        Set the digital output value of the pin.

        This has no effect here.
        """
        pass

    def get_analog(self) -> int:
        """Get the analog input value of the pin. This is proportional to the force applied."""
        return int(self._device.getValue())


class ReflectanceSensor(BasePin):
    """
    A simple sensor that can detect the reflectance of a surface.

    Used for line following, with a higher value indicating a lighter surface.
    """

    def __init__(self, device_name: str) -> None:
        g = get_globals()
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.DistanceSensor)
        self._device.enable(g.timestep)
        self._mode = GPIOPinMode.INPUT

    def get_mode(self) -> GPIOPinMode:
        """Get the current mode of the pin."""
        return self._mode

    def set_mode(self, mode: GPIOPinMode) -> None:
        """Set the mode of the pin."""
        self._mode = mode

    def get_digital(self) -> bool:
        """
        Get the digital input value of the pin.

        True when the reflectance is above half the maximum value.
        """
        return self.get_analog() > ANALOG_MAX / 2

    def set_digital(self, value: bool) -> None:
        """
        Set the digital output value of the pin.

        This has no effect here.
        """
        pass

    def get_analog(self) -> int:
        """
        Get the analog input value of the pin.

        This is proportional to the reflectance of the surface.
        """
        return int(self._device.getValue())


class Led(BasePin):
    """A simple LED that can be turned on or off."""

    def __init__(self, device_name: str) -> None:
        self._led = _Led(device_name)
        self._mode = GPIOPinMode.OUTPUT

    def get_mode(self) -> GPIOPinMode:
        """Get the current mode of the pin."""
        return self._mode

    def set_mode(self, mode: GPIOPinMode) -> None:
        """Set the mode of the pin."""
        self._mode = mode

    def get_digital(self) -> bool:
        """
        Get the digital input value of the pin.

        True when the LED is on.
        """
        return self._led.get_colour() > 0

    def set_digital(self, value: bool) -> None:
        """Set the digital output value of the pin. This turns the LED on or off."""
        self._led.set_colour(1 if value else 0)

    def get_analog(self) -> int:
        """Get the analog input value of the pin. This is always 0."""
        return 0
