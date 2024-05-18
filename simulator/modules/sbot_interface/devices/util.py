from dataclasses import dataclass
from typing import TypeVar

from controller import (
    Accelerometer, Camera, Compass, DistanceSensor, Emitter, GPS, Gyro,
    InertialUnit, LED, Lidar, LightSensor, Motor, PositionSensor, Radar,
    RangeFinder, Receiver, Robot, Speaker, TouchSensor, VacuumGripper,
)
from controller.device import Device

TDevice = TypeVar('TDevice', bound=Device)
__GLOBALS: 'GlobalData' | None = None


class WebotsDevice:
    Accelerometer = Accelerometer
    Camera = Camera
    Compass = Compass
    DistanceSensor = DistanceSensor
    Emitter = Emitter
    GPS = GPS
    Gyro = Gyro
    InertialUnit = InertialUnit
    LED = LED
    Lidar = Lidar
    LightSensor = LightSensor
    Motor = Motor
    PositionSensor = PositionSensor
    Radar = Radar
    RangeFinder = RangeFinder
    Receiver = Receiver
    Speaker = Speaker
    TouchSensor = TouchSensor
    VacuumGripper = VacuumGripper


@dataclass
class GlobalData:
    robot: Robot
    timestep: int


def get_globals() -> GlobalData:
    """Returns the global dictionary."""
    global __GLOBALS
    if __GLOBALS is None:
        robot = Robot()
        __GLOBALS = GlobalData(robot=robot, timestep=int(robot.getBasicTimeStep() * 1000))
    return __GLOBALS


def map_to_range(
    old_min_max: tuple[float, float],
    new_min_max: tuple[float, float],
    value: float,
) -> float:
    """Maps a value from within one range of inputs to within a range of outputs."""
    old_min, old_max = old_min_max
    new_min, new_max = new_min_max
    return ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min


def get_robot_device(robot: Robot, name: str, kind: type[TDevice]) -> TDevice:
    device = robot.getDevice(name)
    if not isinstance(device, kind):
        raise TypeError(f"Failed to get device: {name}.")
    return device
