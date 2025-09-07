#!/usr/bin/env python3
"""
A script to setup the environment for running the project in Webots.

It will:
1. Create a setup virtual environment and install uv into it
2. Use uv to run the standard setup using the desired Python version
"""
import logging
import platform
import sys
from pathlib import Path
from subprocess import SubprocessError, check_call

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

BOLD_RED = '\x1b[31;1m'
GREEN = '\x1b[32;20m'
RESET_COLOUR = '\x1b[0m'

PYTHON_VERSION = "3.11"

try:
    if (Path(__file__).parent / 'simulator/VERSION').exists():
        # This is running from a release
        print("Running in release mode")
        project_root = Path(__file__).parent
    else:
        # This is running from the repository
        print("Running in development mode")
        project_root = Path(__file__).parents[1]

    print(f"Starting with python version: {sys.version} on {platform.platform()}")

    venv_dir = project_root / "simulator/setup_venv"
    script_dir = Path(__file__).parent

    check_call([sys.executable, "-m", "venv", venv_dir])

    logger.info("Installing uv")
    if platform.system() == "Windows":
        venv_bin_dir = venv_dir / "Scripts"
        pip = venv_bin_dir / "pip.exe"
        uv_bin = venv_bin_dir / "uv.exe"
    else:
        venv_bin_dir = venv_dir / "bin"
        pip = venv_bin_dir / "pip"
        uv_bin = venv_bin_dir / "uv"

    check_call(
        [pip, "install", "--only-binary=:all:", "--upgrade", "wheel", "uv"],
        cwd=venv_dir,
    )

    logger.info(f"Running setup using Python {PYTHON_VERSION}")
    setup_script = script_dir.relative_to(project_root) / "setup.py"
    check_call([uv_bin, "run", "--python", PYTHON_VERSION, setup_script], cwd=project_root)
except SubprocessError:
    print(BOLD_RED)
    logger.error("Setup failed due to an error.")
    input(f"An error occurred, press enter to close.{RESET_COLOUR}")
except Exception:
    print(BOLD_RED)
    logger.exception("Setup failed due to an error.")
    input(f"An error occurred, press enter to close.{RESET_COLOUR}")
