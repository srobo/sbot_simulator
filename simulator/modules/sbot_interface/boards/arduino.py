"""
A simulator for the SR Arduino board.

Provides a message parser that simulates the behavior of an Arduino board.

Based on the Arduino v2.0 firmware.
"""
from __future__ import annotations

import logging

from sbot_interface.devices.arduino_devices import BasePin, GPIOPinMode, UltrasonicSensor

LOGGER = logging.getLogger(__name__)


class Arduino:
    """
    A simulator for the SR Arduino board.

    :param pins: A list of simulated devices connected to the Arduino board.
                 The list is indexed by the pin number and EmptyPin is used for
                 unconnected pins.
    :param asset_tag: The asset tag to report for the Arduino board.
    :param software_version: The software version to report for the Arduino board.
    """

    def __init__(self, pins: list[BasePin], asset_tag: str, software_version: str = '2'):
        self.pins = pins
        self.asset_tag = asset_tag
        self.software_version = software_version

    def handle_command(self, command: str) -> str:
        """
        Process a command string and return the response.

        Executes the appropriate action on any specified pins automatically.

        :param command: The command string to process.
        :return: The response to the command.
        """
        if command[0] == 'a':  # analog read
            pin_number = self._convert_pin_number(command, 1)
            if pin_number == -1:
                return '0'
            return str(self.pins[pin_number].get_analog())
        elif command[0] == 'r':  # digital read
            pin_number = self._convert_pin_number(command, 1)
            if pin_number == -1:
                return 'l'
            return 'h' if self.pins[pin_number].get_digital() else 'l'
        elif command[0] == 'l':  # digital write low
            pin_number = self._convert_pin_number(command, 1)
            if pin_number != -1:
                self.pins[pin_number].set_digital(False)
            return ''
        elif command[0] == 'h':  # digital write high
            pin_number = self._convert_pin_number(command, 1)
            if pin_number != -1:
                self.pins[pin_number].set_digital(True)
            return ''
        elif command[0] == 'i':  # set pin mode to input
            pin_number = self._convert_pin_number(command, 1)
            if pin_number != -1:
                self.pins[pin_number].set_mode(GPIOPinMode.INPUT)
            return ''
        elif command[0] == 'o':  # set pin mode to output
            pin_number = self._convert_pin_number(command, 1)
            if pin_number != -1:
                self.pins[pin_number].set_mode(GPIOPinMode.OUTPUT)
            return ''
        elif command[0] == 'p':  # set pin mode to input pullup
            pin_number = self._convert_pin_number(command, 1)
            if pin_number != -1:
                self.pins[pin_number].set_mode(GPIOPinMode.INPUT_PULLUP)
            return ''
        elif command[0] == 'u':  # ultrasonic measurement
            pulse_pin = self._convert_pin_number(command, 1)
            echo_pin = self._convert_pin_number(command, 2)

            if pulse_pin == -1 or echo_pin == -1:
                return '0'

            ultrasound_sensor = self.pins[echo_pin]
            if isinstance(ultrasound_sensor, UltrasonicSensor):
                return str(ultrasound_sensor.get_distance())
            else:
                return '0'
        elif command[0] == 'v':  # software version
            return f"SRduino:{self.software_version}"
        else:
            # A problem here: we do not know how to handle the command!
            # Just ignore this for now.
            return ''

    def _convert_pin_number(self, command: str, index: int) -> int:
        if len(command) < index + 1:
            LOGGER.warning(f'Incomplete arduino command: {command}')
            return -1

        pin_str = command[index]
        try:
            pin_number = ord(pin_str) - ord('a')
        except ValueError:
            LOGGER.warning(f'Invalid pin number in command: {command}')
            return -1

        if 0 < pin_number < len(self.pins):
            return pin_number
        else:
            LOGGER.warning(f'Invalid pin number in command: {command}')
            return -1
