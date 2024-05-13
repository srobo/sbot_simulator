from typing import List, Tuple

from sbot_interface.devices.led import BaseLed
from sbot_interface.devices.power import BaseButton, BaseBuzzer, Output

NUM_OUTPUTS = 7  # 6 12V outputs, 1 5V output
SYS_OUTPUT = 6  # 5V output for the brain

RUN_LED = 0
ERR_LED = 1


## Based on the Power Board v4.4.2sb firmware
class PowerBoard:
    def __init__(
        self,
        outputs: List[Output],
        buzzer: BaseBuzzer,
        button: BaseButton,
        leds: Tuple[BaseLed, BaseLed],
        asset_tag: str,
        software_version: str='4.4.2',
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
        args = command.split(':')
        if args[0] == '*IDN?':
            return f'Student Robotics:PBv4B:{self.asset_tag}:{self.software_version}'
        elif args[0] == '*STATUS?':
            # Output faults are unsupported, fan is always off
            return f"0,0,0,0,0,0,0:{self.temp}:0:5000"
        elif args[0] == '*RESET':
            for output in self.outputs:
                output.set_output(False)
            self.buzzer.set_note(0, 0)
            self.leds[RUN_LED].set_colour(0)
            self.leds[ERR_LED].set_colour(0)
            return 'ACK'
        elif args[0] == 'BTN':
            if len(args) < 2:
                return 'NACK:Missing button command'
            if args[1] == 'START:GET?':
                return f'{self.button.get_state()}:0'
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
                self.outputs[output_number].set_output(state)
                return 'ACK'
            elif args[2] == 'GET?':
                return '1' if self.outputs[output_number].get_output() else '0'
            elif args[2] == 'I?':
                return str(self.outputs[output_number].get_current())
        elif args[0] == 'BATT':
            if len(args) < 2:
                return 'NACK:Missing battery command'
            if args[1] == 'V?':
                return str(self.battery_voltage)
            elif args[1] == 'I?':
                return str(self.current())
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
                    if args[3] == 'F':
                        self.leds[led_type].set_colour(1)
                    else:
                        self.leds[led_type].set_colour(int(args[3]))
                    return 'ACK'
                else:
                    return 'NACK:Invalid LED state'
            elif args[2] == 'GET?':
                return self.leds[led_type].get_colour()
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

                self.buzzer.set_note(freq, dur)
                return 'ACK'
        else:
            return f'NACK:Unknown command {command.strip()}'

    def current(self):
        return sum(output.get_current() for output in self.outputs)
