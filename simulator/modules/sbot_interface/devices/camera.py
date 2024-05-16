from abc import ABC, abstractmethod
from typing import Tuple


class BaseCamera(ABC):
    @abstractmethod
    def get_image(self) -> bytes:
        pass

    @abstractmethod
    def get_resolution(self) -> Tuple[int, int]:
        pass


class NullCamera(BaseCamera):
    def get_image(self) -> bytes:
        return b''

    def get_resolution(self) -> Tuple[int, int]:
        return 0, 0


# Camera
