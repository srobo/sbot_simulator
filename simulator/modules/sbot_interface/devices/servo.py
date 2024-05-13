from abc import ABC, abstractmethod

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

