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

# TODO rotary servo
# TODO linear servo
