"""
A simulator for the SRO LED hat.

Provides a message parser that simulates the behavior of the LED hat.
"""
from __future__ import annotations

import logging

from sbot_interface.devices.led import RGB_COLOURS, BaseLed

LOGGER = logging.getLogger(__name__)

# *IDN?
# *STATUS?
# *RESET
# LED:<n>:SET:<r>:<g>:<b>
# LED:<n>:GET?
# LED:START:SET:<0/1>
# LED:START:GET?

LED_START = 4


class LedBoard:
    """
    A simulator for the SRO LED hat.

    :param leds: A list of simulated LEDs connected to the LED hat.
                    The list is indexed by the LED number.
    :param asset_tag: The asset tag to report for the LED hat.
    :param software_version: The software version to report for the LED hat.
    """

    def __init__(self, leds: list[BaseLed], asset_tag: str, software_version: str = '1.0'):
        self.leds = leds
        self.asset_tag = asset_tag
        self.software_version = software_version

    def handle_command(self, command: str) -> str:
        """
        Process a command string and return the response.

        Executes the appropriate action on any specified LEDs automatically.

        :param command: The command string to process.
        :return: The response to the command.
        """
        args = command.split(':')
        if args[0] == '*IDN?':
            return f'Student Robotics:KCHv1B:{self.asset_tag}:{self.software_version}'
        elif args[0] == '*STATUS?':
            return 'ACK'
        elif args[0] == '*RESET':
            LOGGER.info(f'Resetting led board {self.asset_tag}')
            for led in self.leds:
                led.set_colour(0)
            return 'ACK'
        elif args[0] == 'LED':
            if len(args) < 2:
                return 'NACK:Missing LED number'

            if args[1] == 'START':
                led_number = LED_START
                if len(args) < 3:
                    return 'NACK:Missing LED command'
                if args[2] == 'SET':
                    if len(args) < 4:
                        return 'NACK:Missing LED start'
                    try:
                        start = int(args[3])
                    except ValueError:
                        return 'NACK:Invalid LED start'
                    if start not in [0, 1]:
                        return 'NACK:Invalid LED start'
                    LOGGER.info(f'Setting start LED on board {self.asset_tag} to {start}')
                    self.leds[led_number].set_colour(start)
                    return 'ACK'
                elif args[2] == 'GET?':
                    return str(self.leds[led_number].get_colour())
                else:
                    return "NACK:Unknown start command"
            else:
                try:
                    led_number = int(args[1])
                except ValueError:
                    return 'NACK:Invalid LED number'
                if not (0 <= led_number < len(self.leds)):
                    return 'NACK:Invalid LED number'

                if len(args) < 3:
                    return 'NACK:Missing LED command'
                if args[2] == 'SET':
                    if len(args) < 6:
                        return 'NACK:Missing LED colour'
                    try:
                        r = bool(int(args[3]))
                        g = bool(int(args[4]))
                        b = bool(int(args[5]))
                    except ValueError:
                        return 'NACK:Invalid LED colour'
                    if r not in [0, 1] or g not in [0, 1] or b not in [0, 1]:
                        return 'NACK:Invalid LED colour'
                    LOGGER.info(
                        f'Setting LED {led_number} on board {self.asset_tag} to '
                        f'{r:d}:{g:d}:{b:d} (colour {RGB_COLOURS.index((r, g, b))}',
                    )
                    self.leds[led_number].set_colour(RGB_COLOURS.index((r, g, b)))
                    return 'ACK'
                elif args[2] == 'GET?':
                    colour = RGB_COLOURS[self.leds[led_number].get_colour()]
                    return f"{colour[0]:d}:{colour[1]:d}:{colour[2]:d}"
                else:
                    return 'NACK:Unknown LED command'
        else:
            return f'NACK:Unknown command {command.strip()}'
        return 'NACK:Command failed'
