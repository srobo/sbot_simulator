from typing import List

from sbot_interface.devices.servo import MAX_POSITION, MIN_POSITION, BaseServo


## Based on the Servo Board v4.4 firmware
class ServoBoard:
    def __init__(self, servos: List[BaseServo], asset_tag: str, software_version: str='4.4'):
        self.servos = servos
        self.asset_tag = asset_tag
        self.software_version = software_version
        self.watchdog_fail = False
        self.pgood = True

    def handle_command(self, command: str) -> str:
        args = command.split(':')
        if args[0] == '*IDN?':
            return f'Student Robotics:SBv4B:{self.asset_tag}:{self.software_version}'
        elif args[0] == '*STATUS?':
            return f"{self.watchdog_fail}:{self.pgood}"
        elif args[0] == '*RESET':
            for servo in self.servos:
                servo.disable()
            return 'ACK'
        elif args[0] == 'SERVO':
            if len(args) < 2:
                return 'NACK:Missing servo number'
            if args[1] == 'I?':
                return str(self.current())
            elif args[1] == 'V?':
                return '5000'

            try:
                servo_number = int(args[1])
            except ValueError:
                return 'NACK:Invalid servo number'
            if not (0 <= servo_number < len(self.servos)):
                return 'NACK:Invalid servo number'

            if len(args) < 3:
                return 'NACK:Missing servo command'

            if args[2] == 'DISABLE':
                self.servos[servo_number].disable()
                return 'ACK'
            elif args[2] == 'GET?':
                return str(self.servos[servo_number].get_position())
            elif args[2] == 'SET':
                if len(args) < 4:
                    return 'NACK:Missing servo setpoint'

                try:
                    setpoint = int(args[3])
                except ValueError:
                    return 'NACK:Invalid servo setpoint'
                if not (MIN_POSITION <= setpoint <= MAX_POSITION):
                    return 'NACK:Invalid servo setpoint'

                self.servos[servo_number].set_position(setpoint)
                return 'ACK'
            else:
                return 'NACK:Unknown servo command'
        else:
            return f'NACK:Unknown command {command.strip()}'

    def current(self):
        return sum(servo.get_current() for servo in self.servos)
