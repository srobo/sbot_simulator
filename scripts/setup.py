#!/usr/bin/env python3
"""
A script to setup the environment for running the project in Webots.

It will:
1. Create a virtual environment in the project root, if it does not exist
2. Install the dependencies from requirements.txt in the virtual environment
3. Set the python path in runtime.ini to the virtual environment python
4. Repopulate the zone 0 folder with basic_robot.py if robot.py is missing
"""
from __future__ import annotations

import logging
import platform
import shutil
import sys
from pathlib import Path
from subprocess import SubprocessError, check_call
from venv import create

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def populate_python_config(runtime_ini: Path, venv_python: Path) -> None:
    """
    Populate the python configuration in the runtime.ini file.

    This will set the python command to the virtual environment python.

    :param runtime_ini: The path to the runtime.ini file
    :param venv_python: The path to the virtual environment python executable
    """
    runtime_content: list[str] = []
    if runtime_ini.exists():
        prev_runtime_content = runtime_ini.read_text().splitlines()
    else:
        prev_runtime_content = []

    # Remove previous python settings from runtime.ini
    # Everything between [python] and the next section is removed
    in_python_section = False
    for line in prev_runtime_content:
        if line == "[python]":
            in_python_section = True
            if runtime_content and runtime_content[-1] == "":
                runtime_content.pop()
        elif in_python_section and line.startswith("["):
            in_python_section = False
        elif not in_python_section:
            runtime_content.append(line)

    runtime_content.extend([
        "",
        "[python]",
        f"COMMAND = {venv_python.absolute()}",
        "",
    ])

    runtime_ini.write_text('\n'.join(runtime_content))


try:
    if (Path(__file__).parent / 'simulator/VERSION').exists():
        # This is running from a release
        print("Running in release mode")
        project_root = Path(__file__).parent
        requirements = project_root / "simulator/requirements.txt"
    else:
        # This is running from the repository
        print("Running in development mode")
        project_root = Path(__file__).parents[1]
        requirements = project_root / "requirements.txt"

    print(f"Python version: {sys.version} on {platform.platform()}")

    venv_dir = project_root / "venv"

    logger.info(f"Creating virtual environment in {venv_dir.absolute()}")
    create(venv_dir, with_pip=True)

    logger.info(f"Installing dependencies from {requirements.absolute()}")
    if platform.system() == "Windows":
        pip = venv_dir / "Scripts/pip.exe"
        venv_python = venv_dir / "Scripts/python"
    else:
        pip = venv_dir / "bin/pip"
        venv_python = venv_dir / "bin/python"
    check_call(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
        cwd=venv_dir,
    )
    check_call([str(pip), "install", "-r", str(requirements)], cwd=venv_dir)

    logger.info("Setting up Webots Python location")

    controllers_dir = project_root / "simulator/controllers"
    usercode_ini = controllers_dir / "usercode_runner/runtime.ini"
    supervisor_ini = controllers_dir / "competition_supervisor/runtime.ini"
    populate_python_config(usercode_ini, venv_python)
    populate_python_config(supervisor_ini, venv_python)

    # repopulate zone 0 with example code if robot.py is missing
    zone_0 = project_root / "zone_0"
    if not (zone_0 / "robot.py").exists():
        logger.info("Repopulating zone 0 with example code")
        zone_0.mkdir(exist_ok=True)
        shutil.copy(project_root / "example_robots/basic_robot.py", zone_0 / "robot.py")
except SubprocessError:
    logger.error("Setup failed due to an error.")
    input("An error occurred, press enter to close.")
except Exception:
    logger.exception("Setup failed due to an error.")
    input("An error occurred, press enter to close.")
else:
    input("Setup complete, press enter to close.")
