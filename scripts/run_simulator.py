#!/usr/bin/env python3
"""
A script to run the project in Webots.

Largely just a shortcut to running the arena world in Webots.
"""
# ruff: noqa: E501
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
    SIM_BASE = Path(__file__).parent.resolve()
else:
    print("Running in development mode")
    # Assume the script is in the scripts directory
    SIM_BASE = Path(__file__).parents[1].resolve()

POSSIBLE_WEBOTS_PATHS = [
    ("darwin", "/Applications/Webots.app/Contents/MacOS/webots"),
    ("win32", "C:\\Program Files\\Webots\\msys64\\mingw64\\bin\\webotsw.exe"),
    ("win32", expandvars("%LOCALAPPDATA%\\Programs\\Webots\\msys64\\mingw64\\bin\\webotsw.exe")),
    # Attempt to use the start menu shortcut
    ("win32", expandvars("%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\Cyberbotics\\Webots.lnk")),
    ("win32", expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Cyberbotics\\Webots.lnk")),
    ("linux", "/usr/local/bin/webots"),
    ("linux", "/usr/bin/webots"),
]


def get_webots_parameters() -> tuple[Path, Path]:
    """
    Get the paths to the Webots executable and the arena world file.

    :return: The paths to the Webots executable and the arena world file
    """
    world_file = SIM_BASE / "simulator/worlds/arena.wbt"

    if not world_file.exists():
        raise RuntimeError("World file not found.")

    if not (SIM_BASE / "venv").exists():
        raise RuntimeError("Please run the setup.py script before running the simulator.")

    # Check if Webots is in the PATH
    webots = which("webots")

    # Find the webots executable, if it is not in the PATH
    if webots is None:
        for system_filter, path in POSSIBLE_WEBOTS_PATHS:
            if sys.platform.startswith(system_filter):
                print(f"Checking {path}")
                if Path(path).exists():
                    webots = path
                    break

    if webots is None or not Path(webots).exists():
        raise RuntimeError("Webots executable not found.")

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
                # shell=True is needed to run from shortcuts
                shell=(webots.suffix == ".lnk"),
            )
        else:
            Popen([str(webots), str(world_file)], start_new_session=True)
    except RuntimeError as e:
        print(f"An error occurred: {e}")
        input("Press enter to continue...")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
        input("Press enter to continue...")
        exit(1)


if __name__ == "__main__":
    main()
