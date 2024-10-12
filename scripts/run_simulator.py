#!/usr/bin/env python3
"""
A script to run the project in Webots.

Largely just a shortcut to running the arena world in Webots.
"""
from __future__ import annotations

import sys
import traceback
from os.path import expandvars
from pathlib import Path
from shutil import which
from subprocess import Popen

if sys.platform == "win32":
    from subprocess import CREATE_NEW_PROCESS_GROUP, DETACHED_PROCESS

if (Path(__file__).parent / 'simulator/VERSION').exists():
    print("Running in release mode")
    SIM_BASE = Path(__file__).parent
else:
    print("Running in development mode")
    # Assume the script is in the scripts directory
    SIM_BASE = Path(__file__).parents[1]


def get_webots_parameters() -> tuple[Path, Path]:
    """
    Get the paths to the Webots executable and the arena world file.

    :return: The paths to the Webots executable and the arena world file
    """
    world_file = SIM_BASE / "simulator/worlds/arena.wbt"

    if not world_file.exists():
        raise RuntimeError("World file not found.")

    # Check if Webots is in the PATH
    webots = which("webots")

    # Find the webots executable, if it is not in the PATH
    if webots is None:
        if sys.platform == "darwin":
            webots = "/Applications/Webots.app/Contents/MacOS/webots"
        elif sys.platform == "win32":
            possible_paths = [
                "C:\\Program Files\\Webots\\msys64\\mingw64\\bin\\webotsw.exe",
                expandvars("%LOCALAPPDATA%\\Programs\\Webots\\msys64\\mingw64\\bin\\webotsw.exe"),
            ]
            for path in possible_paths:
                if Path(path).exists():
                    webots = path
                    break
            else:
                print("Webots executable not found.")
                raise RuntimeError
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

    if not (SIM_BASE / "venv").exists():
        print("Please run the setup.py script before running the simulator.")
        raise RuntimeError

    return Path(webots), world_file


def main() -> None:
    """Run the project in Webots."""
    try:
        webots, world_file = get_webots_parameters()

        # Run the world file in Webots,
        # detaching the process so it does not close when this script does
        if sys.platform == "win32":
            Popen(
                [str(webots), str(world_file)],
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
            )
        else:
            Popen([str(webots), str(world_file)], start_new_session=True)
    except RuntimeError:
        input("Press enter to continue...")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
        input("Press enter to continue...")
        exit(1)


if __name__ == "__main__":
    main()
