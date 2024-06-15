#!/usr/bin/env python3
"""
This script is used to run the project in Webots.

Largely just a shortcut to running the arena world in Webots.
Only functional in releases.
"""
import platform
from pathlib import Path
from shutil import which
from subprocess import Popen

if platform.system() == "Windows":
    from subprocess import CREATE_NEW_PROCESS_GROUP, DETACHED_PROCESS


if not (Path(__file__).parent / 'simulator/VERSION').exists():
    print("This script is only functional in releases.")
    exit(1)

world_file = Path(__file__).parent / "simulator/worlds/arena.wbt"

webots = which("webots")

# Find the webots executable, if it is not in the PATH
if webots is None:
    if platform.system() == "Darwin":
        webots = "/Applications/Webots.app/Contents/MacOS/webots"
    elif platform.system() == "Windows":
        webots = "C:\\Program Files\\Webots\\msys64\\bin\\webotsw.exe"
    elif platform.system() == "Linux":
        webots = "/usr/bin/webots"
    else:
        print("Unsupported platform.")
        exit(1)

if not Path(webots).exists():
    print("Webots executable not found.")
    exit(1)

# Run the world file in Webots, detaching the process so it does not close when this script does
if platform.system() == "Windows":
    Popen([webots, world_file], creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
else:
    Popen([webots, world_file], start_new_session=True)
