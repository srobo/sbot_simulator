from __future__ import annotations

import logging

from sbot_interface.boards import Arduino, CameraBoard, LedBoard, MotorBoard, PowerBoard, ServoBoard, TimeServer
from sbot_interface.devices.arduino_devices import EmptyPin, ReflectanceSensor, MicroSwitch, UltrasonicSensor
from sbot_interface.devices.camera import Camera
from sbot_interface.devices.led import Led, NullLed
from sbot_interface.devices.motor import Motor
from sbot_interface.devices.servo import NullServo
from sbot_interface.devices.power import Output, NullBuzzer, StartButton
from sbot_interface.socket_server import DeviceServer, SocketServer


def setup_devices(log_level: int | str = logging.WARNING) -> SocketServer:
    device_logger = logging.getLogger('sbot_interface')
    device_logger.setLevel(log_level)

    # this is the configuration of devices connected to the robot
    devices = [
        PowerBoard(
            outputs=[Output() for _ in range(7)],
            buzzer=NullBuzzer(),
            button=StartButton(),
            leds=[NullLed() for _ in range(2)],
            asset_tag='PWR',
        ),
        MotorBoard(
            motors=[
                Motor('left motor'),
                Motor('right motor'),
            ],
            asset_tag='MOT',
        ),
        ServoBoard(
            servos=[NullServo() for _ in range(8)],
            asset_tag='SERVO',
        ),
        LedBoard(
            leds=[
                Led('led 1'),
                Led('led 2'),
                Led('led 3'),
            ],
            asset_tag='LED',
        ),
        Arduino(
            pins=[
                EmptyPin(),
                EmptyPin(),
                ReflectanceSensor('reflectance sensor 1'),
                ReflectanceSensor('reflectance sensor 2'),
                UltrasonicSensor('ultrasound front'),
                UltrasonicSensor('ultrasound left'),
                UltrasonicSensor('ultrasound right'),
                UltrasonicSensor('ultrasound back'),
                MicroSwitch('front left bump sensor'),
                MicroSwitch('front right bump sensor'),
                MicroSwitch('rear left bump sensor'),
                MicroSwitch('rear right bump sensor'),
            ],
            asset_tag='Arduino1',
        ),
        TimeServer(
            asset_tag='TimeServer',
        ),
        CameraBoard(
            Camera('camera', frame_rate=15),
            asset_tag='Camera',
        ),
    ]

    device_servers = []

    for device in devices:
        # connect each device to a socket to receive commands from sbot
        device_servers.append(DeviceServer(device))

    # collect all device servers into a single server which will handle all connections and commands
    return SocketServer(device_servers)


def main() -> None:
    server = setup_devices(logging.DEBUG)
    # generate and print the socket url and information for each device
    print(server.links_formatted())
    # start select loop for all server sockets and device sockets
    server.run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
