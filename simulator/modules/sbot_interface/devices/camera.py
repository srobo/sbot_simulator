"""A wrapper for the Webots camera device."""
from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cache
from math import tan

from sbot_interface.devices.util import WebotsDevice, get_globals, get_robot_device

g = get_globals()


class BaseCamera(ABC):
    """Base class for camera devices."""

    @abstractmethod
    def get_image(self) -> bytes:
        """Get a frame from the camera, encoded as a byte string."""
        pass

    @abstractmethod
    def get_resolution(self) -> tuple[int, int]:
        """Get the resolution of the camera in pixels, width x height."""
        pass

    @abstractmethod
    def get_calibration(self) -> tuple[float, float, float, float]:
        """Return the intrinsic camera calibration parameters fx, fy, cx, cy."""
        pass


class NullCamera(BaseCamera):
    """
    Null camera device.

    Allows the robot to run without a camera device attached.
    """

    def get_image(self) -> bytes:
        """Get a frame from the camera, encoded as a byte string."""
        return b''

    def get_resolution(self) -> tuple[int, int]:
        """Get the resolution of the camera in pixels, width x height."""
        return 0, 0

    def get_calibration(self) -> tuple[float, float, float, float]:
        """Return the intrinsic camera calibration parameters fx, fy, cx, cy."""
        return 0, 0, 0, 0


# Camera
class Camera(BaseCamera):
    """
    A wrapper for the Webots camera device.

    The camera will sleep for 1 frame time before capturing an image to ensure the
    image is up to date.

    :param device_name: The name of the camera device.
    :param frame_rate: The frame rate of the camera in frames per second.
    """

    def __init__(self, device_name: str, frame_rate: int) -> None:
        self._device = get_robot_device(g.robot, device_name, WebotsDevice.Camera)
        # round down to the nearest timestep
        self.sample_time = int(((1000 / frame_rate) // g.timestep) * g.timestep)

    def get_image(self) -> bytes:
        """
        Get a frame from the camera, encoded as a byte string.

        Sleeps for 1 frame time before capturing the image to ensure the image is up to date.

        NOTE The image data buffer is automatically freed at the end of the timestep,
        so must not be accessed after any sleep.

        :return: The image data as a byte string.
        """
        # A frame is only captured every sample_time milliseconds the camera is enabled
        # so we need to wait for a frame to be captured after enabling the camera.
        # The image data buffer is automatically freed at the end of the timestep.
        self._device.enable(self.sample_time)
        g.sleep(self.sample_time / 1000)

        image_data_raw = self._device.getImage()
        self._device.disable()

        return image_data_raw

    @cache
    def get_resolution(self) -> tuple[int, int]:
        """Get the resolution of the camera in pixels, width x height."""
        return self._device.getWidth(), self._device.getHeight()

    @cache
    def get_calibration(self) -> tuple[float, float, float, float]:
        """Return the intrinsic camera calibration parameters fx, fy, cx, cy."""
        return (
            (self._device.getWidth() / 2) / tan(self._device.getFov() / 2),  # fx
            (self._device.getWidth() / 2) / tan(self._device.getFov() / 2),  # fy
            self._device.getWidth() // 2,  # cx
            self._device.getHeight() // 2,  # cy
        )
