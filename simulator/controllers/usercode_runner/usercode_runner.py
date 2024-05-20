import json
import os
import runpy
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from controller import Robot

sys.path.insert(0, Robot().getProjectPath())
import environment  # configure path to include modules
from robot_logging import prefix_and_tee_streams
from sbot_interface.setup import setup_devices
from sbot_interface.socket_server import SocketServer

# Get the robot object that was created when setting up the environment
robot = Robot.created
assert robot is not None, "Robot object not created"


def get_robot_file(robot_zone: int) -> Path:
    robot_file = environment.ZONE_ROOT / f'zone_{robot_zone}' / 'robot.py'

    # Check if the robot file exists
    if not robot_file.exists():
        raise FileNotFoundError(f"No robot controller found for zone {robot_file}")

    return robot_file


def get_game_mode() -> str:
    if environment.GAME_MODE_FILE.exists():
        game_mode = environment.GAME_MODE_FILE.read_text().strip()
    else:
        game_mode = 'dev'

    assert game_mode in ['dev', 'comp'], f'Invalid game mode: {game_mode}'

    return game_mode


def print_simulation_version():
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
    return setup_devices()


def run_usercode(robot_file: Path, robot_zone: int, game_mode: str) -> None:
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


def main():
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
    run_usercode(robot_file, zone, game_mode)

    # Cleanup devices
    devices.stop_event.set()


if __name__ == '__main__':
    exit(main())
