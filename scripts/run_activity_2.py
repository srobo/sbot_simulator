#!/usr/bin/env python3
"""
A script to run the project in Webots.

Largely just a shortcut to running the arena world in Webots.
Only functional in releases.
"""
import sys
import traceback
from pathlib import Path
from shutil import which
from subprocess import Popen

if sys.platform == "win32":
    from subprocess import CREATE_NEW_PROCESS_GROUP, DETACHED_PROCESS

try:
    if not (Path(__file__).parent / 'simulator/VERSION').exists():
        print("This script is only functional in releases.")
        raise RuntimeError

    world_file = Path(__file__).parent / "simulator/worlds/02-line.wbt"

    webots = which("webots")

    # Find the webots executable, if it is not in the PATH
    if webots is None:
        if sys.platform == "darwin":
            webots = "/Applications/Webots.app/Contents/MacOS/webots"
        elif sys.platform == "win32":
            webots = "C:\\Program Files\\Webots\\msys64\\mingw64\\bin\\webotsw.exe"
        elif sys.platform.startswith("linux"):
            possible_paths = ["/usr/local/bin/webots", "/usr/bin/webots"]
            for path in possible_paths:
                if Path(path).exists():
                    webots = path
                    break
            else:
                print("Webots executable not found.")
                raise RuntimeError
        else:
            print("Unsupported platform.")
            raise RuntimeError

    if not Path(webots).exists():
        print("Webots executable not found.")
        raise RuntimeError

    if not (Path(__file__).parent / "venv").exists():
        print("Please run the setup.py script before running the simulator.")
        raise RuntimeError

    # Run the world file in Webots,
    # detaching the process so it does not close when this script does
    if sys.platform == "win32":
        Popen([webots, world_file], creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
    else:
        Popen([webots, world_file], start_new_session=True)
except RuntimeError:
    input("Press enter to continue...")
    exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    print(traceback.format_exc())
    input("Press enter to continue...")
    exit(1)
