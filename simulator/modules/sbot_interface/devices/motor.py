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
