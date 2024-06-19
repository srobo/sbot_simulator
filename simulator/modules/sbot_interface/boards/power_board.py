"""
A simulator for the SRv4 Power Board.

Provides a message parser that simulates the behavior of a power board.

Based on the Power Board v4.4.2sb firmware.
"""
from __future__ import annotations

import logging

from sbot_interface.devices.led import BaseLed
from sbot_interface.devices.power import BaseButton, BaseBuzzer, Output

LOGGER = logging.getLogger(__name__)

NUM_OUTPUTS = 7  # 6 12V outputs, 1 5V output
SYS_OUTPUT = 6  # 5V output for the brain

RUN_LED = 0
ERR_LED = 1


class PowerBoard:
    """
    A simulator for the SRv4 Power Board.

    :param outputs: A list of simulated outputs connected to the power board.
                        The list is indexed by the output number.
    :param buzzer: A simulated buzzer connected to the power board.
    :param button: A simulated button connected to the power board.
    :param leds: A tuple of simulated LEDs connected to the power board.
    :param asset_tag: The asset tag to report for the power board.
    :param software_version: The software version to report for the power board.
    """

    def __init__(
        self,
        outputs: list[Output],
        buzzer: BaseBuzzer,
        button: BaseButton,
        leds: tuple[BaseLed, BaseLed],
        asset_tag: str,
        software_version: str = '4.4.2',
    ):
        self.outputs = outputs
        self.buzzer = buzzer
        self.button = button
        self.leds = leds
        self.asset_tag = asset_tag
        self.software_version = software_version
        self.temp = 25
        self.battery_voltage = 12000

    def handle_command(self, command: str) -> str:
        """
        Process a command string and return the response.

        Executes the appropriate action on any specified outputs, LEDs,
        or the buzzer automatically.

        :param command: The command string to process.
        :return: The response to the command.
        """
        args = command.split(':')
        if args[0] == '*IDN?':
            return f'Student Robotics:PBv4B:{self.asset_tag}:{self.software_version}'
        elif args[0] == '*STATUS?':
            # Output faults are unsupported, fan is always off
            return f"0,0,0,0,0,0,0:{self.temp}:0:5000"
        elif args[0] == '*RESET':
            LOGGER.info(f'Resetting power board {self.asset_tag}')
            for output in self.outputs:
                output.set_output(False)
            self.buzzer.set_note(0, 0)
            self.leds[RUN_LED].set_colour(0)
            self.leds[ERR_LED].set_colour(0)
            return 'ACK'
        elif args[0] == 'BTN':
            if len(args) < 2:
                return 'NACK:Missing button command'
            if args[1] == 'START' and args[2] == 'GET?':
                return f'{self.button.get_state():d}:0'
            else:
                return 'NACK:Unknown button command'
        elif args[0] == 'OUT':
            if len(args) < 2:
                return 'NACK:Missing output number'
            try:
                output_number = int(args[1])
            except ValueError:
                return 'NACK:Invalid output number'
            if not (0 <= output_number < NUM_OUTPUTS):
                return 'NACK:Invalid output number'

            if len(args) < 3:
                return 'NACK:Missing output command'
            if args[2] == 'SET':
                if output_number == SYS_OUTPUT:
                    return 'NACK:Brain output cannot be controlled'
                if len(args) < 4:
                    return 'NACK:Missing output state'
                try:
                    state = int(args[3])
                except ValueError:
                    return 'NACK:Invalid output state'
                if state not in [0, 1]:
                    return 'NACK:Invalid output state'
                LOGGER.info(
                    f'Setting output {output_number} on board {self.asset_tag} to {state}'
                )
                self.outputs[output_number].set_output(bool(state))
                return 'ACK'
            elif args[2] == 'GET?':
                return '1' if self.outputs[output_number].get_output() else '0'
            elif args[2] == 'I?':
                return str(self.outputs[output_number].get_current())
            else:
                return 'NACK:Unknown output command'
        elif args[0] == 'BATT':
            if len(args) < 2:
                return 'NACK:Missing battery command'
            if args[1] == 'V?':
                return str(self.battery_voltage)
            elif args[1] == 'I?':
                return str(self.current())
            else:
                return 'NACK:Unknown battery command'
        elif args[0] == 'LED':
            if len(args) < 3:
                return 'NACK:Missing LED command'
            if args[1] not in ['RUN', 'ERR']:
                return 'NACK:Invalid LED type'

            led_type = RUN_LED if args[1] == 'RUN' else ERR_LED

            if args[2] == 'SET':
                if len(args) < 4:
                    return 'NACK:Missing LED state'
                if args[3] in ['0', '1', 'F']:
                    LOGGER.info(
                        f'Setting {args[1]} LED on board {self.asset_tag} to {args[3]}'
                    )
                    if args[3] == 'F':
                        self.leds[led_type].set_colour(1)
                    else:
                        self.leds[led_type].set_colour(int(args[3]))
                    return 'ACK'
                else:
                    return 'NACK:Invalid LED state'
            elif args[2] == 'GET?':
                return str(self.leds[led_type].get_colour())
            else:
                return 'NACK:Invalid LED command'
        elif args[0] == 'NOTE':
            if len(args) < 2:
                return 'NACK:Missing note command'
            if args[1] == 'GET?':
                return ':'.join(map(str, self.buzzer.get_note()))
            else:
                if len(args) < 3:
                    return 'NACK:Missing note frequency'
                try:
                    freq = int(args[1])
                except ValueError:
                    return 'NACK:Invalid note frequency'
                if not (0 <= freq < 10000):
                    return 'NACK:Invalid note frequency'

                try:
                    dur = int(args[2])
                except ValueError:
                    return 'NACK:Invalid note duration'
                if dur < 0:
                    return 'NACK:Invalid note duration'

                LOGGER.info(
                    f'Setting buzzer on board {self.asset_tag} to {freq}Hz for {dur}ms'
                )
                self.buzzer.set_note(freq, dur)
                return 'ACK'
        else:
            return f'NACK:Unknown command {command.strip()}'
        return 'NACK:Command failed'

    def current(self) -> int:
        """
        Get the total current draw of all outputs.

        :return: The total current draw of all outputs in mA.
        """
        return sum(output.get_current() for output in self.outputs)
