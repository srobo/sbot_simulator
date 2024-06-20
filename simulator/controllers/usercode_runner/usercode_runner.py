"""
The entry point for all robot controllers.

This script is responsible for setting up the environment, starting the devices,
and running the usercode.

The board simulators are run in a separate thread to allow the usercode to run
in the main thread. This provides the interface between the sbot module and Webots.
"""
import atexit
import json
import logging
import os
import runpy
import subprocess
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
from sbot_interface.setup import setup_devices
from sbot_interface.socket_server import SocketServer

# Get the robot object that was created when setting up the environment
_robot = Robot.created
assert _robot is not None, "Robot object not created"
robot = _robot

LOGGER = logging.getLogger('usercode_runner')


def get_robot_file(robot_zone: int) -> Path:
    """
    Get the path to the robot file for the given zone.

    :param robot_zone: The zone number
    :return: The path to the robot file
    :raises FileNotFoundError: If no robot controller is found for the given zone
    """
    robot_file = environment.ZONE_ROOT / f'zone_{robot_zone}' / 'robot.py'

    # Check if the robot file exists
    if not robot_file.exists():
        raise FileNotFoundError(f"No robot controller found for zone {robot_file}")

    return robot_file


def get_game_mode() -> str:
    """
    Get the game mode from the game mode file.

    Default to 'dev' if the file does not exist.

    :return: The game mode
    """
    if environment.GAME_MODE_FILE.exists():
        game_mode = environment.GAME_MODE_FILE.read_text().strip()
    else:
        game_mode = 'dev'

    assert game_mode in ['dev', 'comp'], f'Invalid game mode: {game_mode}'

    return game_mode


def print_simulation_version() -> None:
    """
    Print the version of the simulator that is running.

    Uses a VERSION file in the root of the simulator to determine the version.
    For development, the version is uses the git describe command.

    The version is printed to the console.
    """
    version_file = environment.SIM_ROOT / 'VERSION'
    if version_file.exists():
        version = version_file.read_text().strip()
    else:
        try:
            version = subprocess.check_output(
                ['git', 'describe', '--tags', '--always'],
                cwd=str(environment.SIM_ROOT.resolve()),
            ).decode().strip()
        except subprocess.CalledProcessError:
            version = 'unknown'

    print(f"Running simulator version: {version}")


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
        Path(tmpdir).joinpath('metadata.json').write_text(json.dumps({
            "zone": robot_zone,
            "is_competition": game_mode == 'comp'
        }))
        os.environ['SBOT_METADATA_PATH'] = tmpdir

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
        # Not having a robot file is not an error in dev mode
        return game_mode == 'comp'

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
        devices.stop_event.set()

    return True


if __name__ == '__main__':
    exit(main())
