from __future__ import annotations

from abc import ABC, abstractmethod

from sbot_interface.devices.util import get_globals


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
    def get_note(self) -> tuple[int, int]:
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

    def get_note(self) -> tuple[int, int]:
        return self.frequency, self.duration


class NullButton(BaseButton):
    def get_state(self) -> bool:
        # button is always pressed
        return True


class StartButton(BaseButton):
    def __init__(self) -> None:
        self._initialized = False

    def get_state(self) -> bool:
        g = get_globals()
        if not self._initialized:
            if g.robot.getCustomData() != 'start':
                g.robot.setCustomData('ready')
            self._initialized = True

        return g.robot.getCustomData() == 'start'
