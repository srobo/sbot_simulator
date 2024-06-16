"""A module to define the power devices used in the simulator."""
from __future__ import annotations

from abc import ABC, abstractmethod

from sbot_interface.devices.util import get_globals


class Output:
    """
    A class to represent a power output.

    This does not actually represent any device in the simulator,
    but is used to simulate how the outputs on the power board would behave.

    :param downstream_current: A function to get the current draw of the downstream device.
    """

    def __init__(self, downstream_current=None) -> None:
        self._enabled = False
        self._current_func = downstream_current

    def set_output(self, enable: bool) -> None:
        """Set the output state."""
        self._enabled = enable

    def get_output(self) -> bool:
        """Get the output state."""
        return self._enabled

    def get_current(self) -> int:
        """Get the current draw of the output in mA."""
        if self._current_func is not None:
            return self._current_func()
        return 0


class BaseBuzzer(ABC):
    """The base class for the buzzer device."""

    @abstractmethod
    def set_note(self, freq: int, dur: int) -> None:
        """Set the note to play and its duration."""
        pass

    @abstractmethod
    def get_note(self) -> tuple[int, int]:
        """Get the note that is currently playing and its duration."""
        pass


class BaseButton(ABC):
    """The base class for the button device."""

    @abstractmethod
    def get_state(self) -> bool:
        """Get whether the button is pressed."""
        pass


class NullBuzzer(BaseBuzzer):
    """A buzzer that does nothing. Used for buzzers that are not connected."""

    def __init__(self) -> None:
        self.frequency = 0
        self.duration = 0
        super().__init__()

    def set_note(self, freq: int, dur: int) -> None:
        """Set the note to play."""
        self.frequency = freq
        self.duration = dur

    def get_note(self) -> tuple[int, int]:
        """Get the note that is currently playing and its duration."""
        return self.frequency, self.duration


class NullButton(BaseButton):
    """A button that does nothing. Used for buttons that are not connected."""

    def get_state(self) -> bool:
        """Return whether the button is pressed. Always returns True."""
        # button is always pressed
        return True


class StartButton(BaseButton):
    """
    A button to represent the start button on the robot.

    Uses the robot's custom data to determine if the robot is ready to start.
    """

    def __init__(self) -> None:
        self._initialized = False

    def get_state(self) -> bool:
        """Return whether the start button is pressed."""
        g = get_globals()
        if not self._initialized:
            if g.robot.getCustomData() != 'start':
                g.robot.setCustomData('ready')
            self._initialized = True

        return g.robot.getCustomData() == 'start'
