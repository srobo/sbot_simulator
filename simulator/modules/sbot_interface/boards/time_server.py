from __future__ import annotations

import logging
from datetime import datetime, timedelta

from sbot_interface.devices.util import get_globals

LOGGER = logging.getLogger(__name__)
g = get_globals()


class TimeServer:
    def __init__(self, asset_tag: str, software_version: str='1.0', start_time: str='2024-06-01T00:00:00+00:00'):
        self.asset_tag = asset_tag
        self.software_version = software_version
        self.start_time = datetime.fromisoformat(start_time)

    def handle_command(self, command: str) -> str:
        args = command.split(':')
        if args[0] == '*IDN?':
            return f'SourceBots:Arduino:{self.asset_tag}:{self.software_version}'
        elif args[0] == '*STATUS?':
            return "Yes"
        elif args[0] == '*RESET':
            return "NACK:Reset not supported"
        elif args[0] == 'TIME?':
            sim_time = g.robot.getTime()
            current_time = self.start_time + timedelta(seconds=sim_time)
            return current_time.isoformat('T', timespec='milliseconds')
        elif args[0] == 'SLEEP':
            if len(args) < 2:
                return 'NACK:Missing duration'
            try:
                duration = int(args[1])
            except ValueError:
                return 'NACK:Invalid duration'
            LOGGER.info(f'Sleeping for {duration} ms')
            g.sleep(duration / 1000)
            return 'ACK'
        else:
            return f'NACK:Unknown command {command.strip()}'
