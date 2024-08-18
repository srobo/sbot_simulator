"""
A simulator for the SRO Camera interface.

Provides a message parser that simulates the behavior of a Camera.
Interfaces to a WebotsRemoteCameraSource in the sr-robot3 package.
"""
from __future__ import annotations

import logging
import struct

from sbot_interface.devices.camera import BaseCamera

LOGGER = logging.getLogger(__name__)

# *IDN?
# *STATUS?
# *RESET
# CAM:CALIBRATION?
# CAM:RESOLUTION?
# CAM:FRAME!


class CameraBoard:
    """
    A simulator for the SRO Camera interface.

    :param camera: The camera object to interface with.
    :param asset_tag: The asset tag to report for the camera board.
    :param software_version: The software version to report for the camera board.
    """

    def __init__(self, camera: BaseCamera, asset_tag: str, software_version: str = '1.0'):
        self.asset_tag = asset_tag
        self.software_version = software_version
        self.camera = camera

    def handle_command(self, command: str) -> str | bytes:
        """
        Process a command string and return the response.

        Executes the appropriate action on the camera automatically.

        :param command: The command string to process.
        :return: The response to the command.
        """
        args = command.split(':')
        if args[0] == '*IDN?':
            return f'Student Robotics:CAMv1a:{self.asset_tag}:{self.software_version}'
        elif args[0] == '*STATUS?':
            return 'ACK'
        elif args[0] == '*RESET':
            LOGGER.info(f'Resetting camera board {self.asset_tag}')
            return 'ACK'
        elif args[0] == 'CAM':
            if len(args) < 2:
                return 'NACK:Missing camera command'

            if args[1] == 'CALIBRATION?':
                LOGGER.info(f'Getting calibration data from camera on board {self.asset_tag}')
                return ':'.join(map(str, self.camera.get_calibration()))
            elif args[1] == 'RESOLUTION?':
                LOGGER.info(f'Getting resolution from camera on board {self.asset_tag}')
                resolution = self.camera.get_resolution()
                return f'{resolution[0]}:{resolution[1]}'
            elif args[1] == 'FRAME!':
                LOGGER.info(f'Getting image from camera on board {self.asset_tag}')
                resolution = self.camera.get_resolution()
                img_len = resolution[0] * resolution[1] * 4  # 4 bytes per pixel
                return struct.pack('>BI', 0, img_len) + self.camera.get_image()
            else:
                return 'NACK:Unknown camera command'
        else:
            return f'NACK:Unknown command {command}'
        return 'NACK:Command failed'
