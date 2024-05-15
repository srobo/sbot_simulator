import logging
from typing import List

from sbot_interface.devices.arduino_devices import BasePin, GPIOPinMode, UltrasonicSensor

LOGGER = logging.getLogger(__name__)


## Based on the Arduino v2.0 firmware
class Arduino:
    def __init__(self, pins: List[BasePin], asset_tag: str, software_version: str='2.0'):
        self.pins = pins
        self.asset_tag = asset_tag
        self.software_version = software_version

    def handle_command(self, command: str) -> str:
        args = command.split(':')
        if args[0] == '*IDN?':
            return f'SourceBots:Arduino:{self.asset_tag}:{self.software_version}'
        elif args[0] == '*STATUS?':
            return "Yes"
        elif args[0] == '*RESET':
            return "NACK:Reset not supported"
        elif args[0] == 'PIN':
            if len(args) < 4:
                return 'NACK:Missing pin number'
            try:
                pin_number = int(args[1])
            except ValueError:
                return 'NACK:Invalid pin number'
            if not (0 <= pin_number < len(self.pins)):
                return 'NACK:Invalid pin number'
            if args[2] == 'MODE':
                if args[3] == 'GET?':
                    return self.pins[pin_number].get_mode().value
                elif args[3] == 'SET':
                    if len(args) < 5:
                        return 'NACK:Missing mode'
                    try:
                        mode = GPIOPinMode(args[4])
                    except ValueError:
                        return 'NACK:Invalid mode'
                    LOGGER.info(f'Setting pin {pin_number} of arduino {self.asset_tag} to mode {mode}')
                    self.pins[pin_number].set_mode(mode)
                    return 'ACK'
            elif args[2] == 'DIGITAL':
                if args[3] == 'GET?':
                    return self.pins[pin_number].get_digital()
                elif args[3] == 'SET':
                    if len(args) < 5:
                        return 'NACK:Missing value'
                    value = args[4]
                    if value not in ['0', '1']:
                        return 'NACK:Invalid value'
                    LOGGER.info(f'Setting pin {pin_number} of arduino {self.asset_tag} to digital value {value}')
                    self.pins[pin_number].set_digital(bool(value))
                    return 'ACK'
            elif args[2] == 'ANALOG':
                if args[3] == 'GET?':
                    return self.pins[pin_number].get_analog()
            else:
                return 'NACK:Unknown pin command'
        elif args[0] == 'ULTRASOUND':
            if len(args) < 4:
                return 'NACK:Missing pin numbers'
            try:
                pulse_pin = int(args[1])
                echo_pin = int(args[2])
            except ValueError:
                return 'NACK:Invalid pin numbers'
            if not (0 <= pulse_pin < len(self.pins) and 0 <= echo_pin < len(self.pins)):
                return 'NACK:Invalid pin numbers'
            if args[3] == 'MEASURE?':
                ultrasound_sensor = self.pins[echo_pin]
                if isinstance(ultrasound_sensor, UltrasonicSensor):
                    return ultrasound_sensor.get_distance()
                return 'NACK:UltraSound sensor not connected'
            else:
                return 'NACK:Unknown ultrasound command'
        else:
            return f'NACK:Unknown command {command.strip()}'
