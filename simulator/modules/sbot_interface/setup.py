"""
Setup the devices connected to the robot.

The main configuration for the devices connected to the robot is the devices
list in the setup_devices function.
"""
from __future__ import annotations

import logging

from sbot_interface.boards import (
    Arduino,
    CameraBoard,
    LedBoard,
    MotorBoard,
    PowerBoard,
    ServoBoard,
    TimeServer,
)
from sbot_interface.devices.arduino_devices import (
    EmptyPin,
    MicroSwitch,
    ReflectanceSensor,
    UltrasonicSensor,
)
from sbot_interface.devices.camera import Camera
from sbot_interface.devices.led import Led, NullLed
from sbot_interface.devices.motor import Motor
from sbot_interface.devices.power import NullBuzzer, Output, StartButton
from sbot_interface.devices.servo import NullServo
from sbot_interface.socket_server import Board, DeviceServer, SocketServer


def setup_devices(log_level: int | str = logging.WARNING) -> SocketServer:
    """
    Setup the devices connected to the robot.

    Contains the main configuration for the devices connected to the robot.

    :param log_level: The logging level to use for the device logger.
    :return: The socket server which will handle all connections and commands.
    """
    device_logger = logging.getLogger('sbot_interface')
    device_logger.setLevel(log_level)

    # this is the configuration of devices connected to the robot
    devices: list[Board] = [
        PowerBoard(
            outputs=[Output() for _ in range(7)],
            buzzer=NullBuzzer(),
            button=StartButton(),
            leds=(NullLed(), NullLed()),
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
                EmptyPin(),  # pin 0
                EmptyPin(),  # pin 1
                EmptyPin(),  # ultrasonic trigger pin, pin 2
                UltrasonicSensor('ultrasound front'),  # pin 3
                EmptyPin(),  # ultrasonic trigger pin, pin 4
                UltrasonicSensor('ultrasound left'),  # pin 5
                EmptyPin(),  # ultrasonic trigger pin, pin 6
                UltrasonicSensor('ultrasound right'),  # pin 7
                EmptyPin(),  # ultrasonic trigger pin, pin 8
                UltrasonicSensor('ultrasound back'),  # pin 9
                MicroSwitch('front left bump sensor'),  # pin 10
                MicroSwitch('front right bump sensor'),  # pin 11
                MicroSwitch('rear left bump sensor'),  # pin 12
                MicroSwitch('rear right bump sensor'),  # pin 13
                ReflectanceSensor('reflectance sensor 1'),  # pin A0
                ReflectanceSensor('reflectance sensor 2'),  # pin A1
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

    device_servers: list[DeviceServer] = []

    for device in devices:
        # connect each device to a socket to receive commands from sbot
        device_servers.append(DeviceServer(device))

    # collect all device servers into a single server which will handle all connections
    # and commands
    return SocketServer(device_servers)


def main() -> None:
    """
    Main function to setup and run the devices. Only used for testing.

    This function will setup the devices and start the select loop to handle all connections.
    """
    server = setup_devices(logging.DEBUG)
    # generate and print the socket url and information for each device
    print(server.links_formatted())
    # start select loop for all server sockets and device sockets
    server.run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
