import logging
from typing import Union

from sbot_interface.devices.camera import BaseCamera

LOGGER = logging.getLogger(__name__)

# *IDN?
# *STATUS?
# *RESET
# CAM:FRAME!


class CameraBoard:
    def __init__(self, camera: BaseCamera, asset_tag: str, software_version: str='1.0'):
        self.asset_tag = asset_tag
        self.software_version = software_version
        self.camera = camera

    def handle_command(self, command: str) -> Union[str, bytes]:
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

            if args[1] == 'FRAME!':
                LOGGER.info(f'Getting image from camera on board {self.asset_tag}')
                return self.camera.get_image()
            else:
                return 'NACK:Unknown camera command'
        else:
            return f'NACK:Unknown command {command}'
