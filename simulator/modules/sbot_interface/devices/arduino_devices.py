from abc import ABC, abstractmethod
from enum import Enum

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


# TODO distance sensor
# TODO bump switch
# TODO reflectance sensor
