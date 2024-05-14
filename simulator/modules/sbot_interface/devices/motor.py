from abc import ABC, abstractmethod

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


# TODO motor
