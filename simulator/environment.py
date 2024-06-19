"""
Configure the sys.path list for importing simulator modules.

Also contains constants for where several important files are located.
"""
import sys
from pathlib import Path

SIM_ROOT = Path(__file__).absolute().parent
ZONE_ROOT = SIM_ROOT.parent
MODULES_ROOT = SIM_ROOT / 'modules'
GAME_MODE_FILE = SIM_ROOT / 'mode.txt'

NUM_ZONES = 1


def setup_environment():
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
