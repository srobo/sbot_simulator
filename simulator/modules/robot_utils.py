"""General utilities that are useful across runners."""
import subprocess
import sys
from pathlib import Path

# Configure path to import the environment configuration
sys.path.insert(0, str(Path(__file__).parents[1]))
import environment

# Reset the path
del sys.path[0]


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
        raise FileNotFoundError(f"No robot code to run for zone {robot_zone}")

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
