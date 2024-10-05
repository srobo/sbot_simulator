"""
The entry point for all robot controllers.

This script is responsible for setting up the environment, starting the devices,
and running the usercode.

The board simulators are run in a separate thread to allow the usercode to run
in the main thread. This provides the interface between the sr-robot3 module and Webots.
"""
import atexit
import json
import logging
import os
import runpy
import sys
import threading
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from controller import Robot

# Robot constructor lacks a return type annotation in R2023b
sys.path.insert(0, Robot().getProjectPath())  # type: ignore[no-untyped-call]
import environment  # configure path to include modules
from robot_logging import prefix_and_tee_streams
from robot_utils import get_game_mode, get_robot_file, print_simulation_version
from sbot_interface.setup import setup_devices
from sbot_interface.socket_server import SocketServer

# Get the robot object that was created when setting up the environment
_robot = Robot.created
assert _robot is not None, "Robot object not created"
robot = _robot

LOGGER = logging.getLogger('usercode_runner')


def start_devices() -> SocketServer:
    """
    Create the board simulators and return the SocketServer object.

    Using the links or links_formatted method of the SocketServer object, the
    devices' socket addresses can be accessed and passed to the usercode.

    The WEBOTS_DEVICE_LOGGING environment variable, overrides the log level used.
    Default is WARNING.
    """
    if log_level := os.environ.get('WEBOTS_DEVICE_LOGGING'):
        return setup_devices(log_level)
    else:
        return setup_devices()


def run_usercode(robot_file: Path, robot_zone: int, game_mode: str) -> None:
    """
    Run the user's code from the given file.

    Metadata is created in a temporary directory and passed to the usercode.
    The system path is modified to avoid the controller modules being imported
    in the usercode.

    :param robot_file: The path to the robot file
    :param robot_zone: The zone number
    :param game_mode: The game mode string ('dev' or 'comp')
    :raises Exception: If the usercode raises an exception
    """
    # Remove this folder from the path
    sys.path.remove(str(Path.cwd()))
    # Remove our custom modules from the path
    sys.path.remove(str(environment.MODULES_ROOT))
    # Add the usercode folder to the path
    sys.path.insert(0, str(robot_file.parent))

    # Change the current directory to the usercode folder
    os.chdir(robot_file.parent)

    with TemporaryDirectory() as tmpdir:
        # Setup metadata (zone, game_mode)
        Path(tmpdir).joinpath('astoria.json').write_text(json.dumps({
            "arena": "simulator",
            "zone": robot_zone,
            "mode": 'COMP' if game_mode == 'comp' else 'DEV',
        }))
        os.environ['SBOT_METADATA_PATH'] = tmpdir
        os.environ['SBOT_USBKEY_PATH'] = str(Path.cwd())

        # Run the usercode
        # pass robot object to the usercode for keyboard robot control
        runpy.run_path(str(robot_file), init_globals={'__robot__': robot})


def main() -> bool:
    """
    The main entry point for the usercode runner.

    This function is responsible for setting up the environment, starting the
    devices, and running the usercode.

    The zone number is passed as the first argument to the script using
    controllerArgs on the robot.

    On completion, the devices are stopped and atexit functions are run.
    """
    zone = int(sys.argv[1])
    game_mode = get_game_mode()

    # Get the robot file
    try:
        robot_file = get_robot_file(zone)
    except FileNotFoundError as e:
        print(e.args[0])
        robot.step()
        # Not having a robot file is not an error in dev mode
        return game_mode != 'comp'

    # Setup log file
    prefix_and_tee_streams(
        robot_file.parent / f'log-{datetime.now():%Y_%m_%dT%H_%M_%S}.txt',
        prefix=lambda: f'[{zone}| {robot.getTime():0.3f}] ',
    )

    # Setup devices
    devices = start_devices()

    # Print the simulation version
    print_simulation_version()

    # Pass the devices to the usercode
    os.environ['WEBOTS_SIMULATOR'] = '1'
    os.environ['WEBOTS_ROBOT'] = devices.links_formatted()

    # Start devices in a separate thread
    thread = threading.Thread(target=devices.run)
    thread.start()

    # Run the usercode
    try:
        run_usercode(robot_file, zone, game_mode)
    finally:
        # Run cleanup code registered in the usercode
        atexit._run_exitfuncs()  # noqa: SLF001
        # Cleanup devices
        devices.completed = True
        devices.stop_event.set()

    return True


if __name__ == '__main__':
    exit(0 if main() else 1)
