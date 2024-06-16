"""
A set of board simulators for the SRO robot.

When connected to the SocketServer, these can be used with the sbot project.
"""
from sbot_interface.boards.arduino import Arduino
from sbot_interface.boards.camera import CameraBoard
from sbot_interface.boards.led_board import LedBoard
from sbot_interface.boards.motor_board import MotorBoard
from sbot_interface.boards.power_board import PowerBoard
from sbot_interface.boards.servo_board import ServoBoard
from sbot_interface.boards.time_server import TimeServer

__all__ = [
    'Arduino',
    'CameraBoard',
    'LedBoard',
    'MotorBoard',
    'PowerBoard',
    'ServoBoard',
    'TimeServer',
]
