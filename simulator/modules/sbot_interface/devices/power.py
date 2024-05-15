from abc import ABC, abstractmethod
from typing import Tuple


class Output:
    def __init__(self, downstream_current = None) -> None:
        self._enabled = False
        self._current_func = downstream_current

    def set_output(self, enable: bool) -> None:
        self._enabled = enable

    def get_output(self) -> bool:
        return self._enabled

    def get_current(self) -> int:
        if self._current_func is not None:
            return self._current_func()
        return 0


class BaseBuzzer(ABC):
    @abstractmethod
    def set_note(self, freq: int, dur: int) -> None:
        pass

    @abstractmethod
    def get_note(self) -> Tuple[int, int]:
        pass


class BaseButton(ABC):
    @abstractmethod
    def get_state(self) -> bool:
        pass


class NullBuzzer(BaseBuzzer):
    def __init__(self) -> None:
        self.frequency = 0
        self.duration = 0
        super().__init__()

    def set_note(self, freq: int, dur: int) -> None:
        self.frequency = freq
        self.duration = dur

    def get_note(self) -> Tuple[int, int]:
        return self.frequency, self.duration


class NullButton(BaseButton):
    def get_state(self) -> bool:
        # button is always pressed
        return True
