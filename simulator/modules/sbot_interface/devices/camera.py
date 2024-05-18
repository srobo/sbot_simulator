from __future__ import annotations

from abc import ABC, abstractmethod

from sbot_interface.devices.util import WebotsDevice, get_globals, get_robot_device

g = get_globals()


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
class Camera(BaseCamera):
    def __init__(self, device_name: str, frame_rate: int) -> None:
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.Camera)
        # round down to the nearest timestep
        self.sample_time = ((1000 / frame_rate) // g.timestep) * g.timestep

    def get_image(self) -> bytes:
        # A frame is only captured every sample_time milliseconds the camera is enabled
        # so we need to wait for a frame to be captured after enabling the camera.
        # The image data buffer is automatically freed at the end of the timestep.
        self._device.enable(self.sample_time)
        g.robot.step(self.sample_time)

        image_data_raw = self._device.getImage()
        self._device.disable()

        return image_data_raw

    def get_resolution(self) -> tuple[int, int]:
        return self._device.getWidth(), self._device.getHeight()
