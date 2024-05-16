from __future__ import annotations

from abc import ABC, abstractmethod


class BaseCamera(ABC):
    @abstractmethod
    def get_image(self) -> bytes:
        pass

    @abstractmethod
    def get_resolution(self) -> tuple[int, int]:
        pass


class NullCamera(BaseCamera):
    def get_image(self) -> bytes:
        return b''

    def get_resolution(self) -> tuple[int, int]:
        return 0, 0


# Camera
