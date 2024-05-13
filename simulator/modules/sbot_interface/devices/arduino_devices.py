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
