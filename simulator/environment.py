"""
Configure the sys.path list for importing simulator modules.

Also contains constants for where several important files are located.
"""
import os
import sys
from pathlib import Path

SIM_ROOT = Path(__file__).absolute().parent
MODULES_ROOT = SIM_ROOT / 'modules'

ARENA_ROOT = Path(os.environ.get('ARENA_ROOT', SIM_ROOT.parent))
ZONE_ROOT = ARENA_ROOT
GAME_MODE_FILE = ARENA_ROOT / 'mode.txt'

NUM_ZONES = 4


if not ARENA_ROOT.is_absolute():
    # Webots sets the current directory of each controller to the directory of
    # the controller file. As such, relative paths would be ambiguous.
    # Hint: `$PWD` or `%CD%` may be useful to construct an absolute path from
    # your relative path.
    raise ValueError(f"'ARENA_ROOT' must be an absolute path, got {ARENA_ROOT!r}")


def setup_environment() -> None:
    """
    Set up the environment for the simulator.

    This function configures the sys.path list to allow importing of the included
    simulator modules.
    """
    sys.path.insert(0, str(MODULES_ROOT))
    this_dir = str(Path(__file__).parent)
    if this_dir in sys.path:
        sys.path.remove(this_dir)


setup_environment()
