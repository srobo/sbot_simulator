#!/usr/bin/env python3
"""
A script to package the project to be run by end users.

This strips down the project to the essentials, removing any unnecessary files
and folders, and zips the project for distribution.

The included files are:
- The simulator directory
- A generated VERSION file
- A readme.txt copied from the user readme
- A set of zone_X folders
- An example code file in zone_0
- A setup script to install the project into a virtual environment
"""
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from shutil import which
from tempfile import TemporaryDirectory

# Add the simulator directory to the path
sys.path.insert(0, str(Path(__file__).parents[1] / "simulator"))
from environment import NUM_ZONES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
project_root = Path(__file__).parents[1]


try:
    version = subprocess.check_output(
        ['git', 'describe', '--tags', '--always'],
        cwd=str(project_root),
    ).decode().strip()
except subprocess.CalledProcessError:
    logger.exception("Failed to get version from git")
    exit(1)

(project_root / "dist").mkdir(exist_ok=True)
os.chdir(str(project_root / "dist"))

with TemporaryDirectory() as temp_dir:
    temp_dir = Path(temp_dir)
    logger.info("Copying simulator folder to temp directory")
    shutil.copytree(project_root / "simulator", temp_dir / "simulator")
    shutil.copy(project_root / "requirements.txt", temp_dir / "simulator/requirements.txt")

    logger.info("Copying LICENSE to temp directory")
    shutil.copy(project_root / "LICENSE", temp_dir / "LICENSE")

    logger.info("Adding README to temp directory")
    if which("pandoc"):
        logger.info(" Converting markdown to HTML using pandoc")
        subprocess.run(
            [
                "pandoc",
                "--standalone",
                "--embed-resources",  # Embed images in the HTML
                "--metadata",
                'pagetitle="title"',
                str(project_root / "assets/user_readme.md"),
                "--output",
                str(temp_dir / "readme.html"),
            ],
            check=True,
        )
    else:
        logger.warning("Pandoc is not available, just copying markdown files")
        shutil.copy(project_root / "assets/user_readme.md", temp_dir / "readme.md")

    logger.info("Copying helper scripts to temp directory")
    shutil.copy(project_root / "scripts/setup.py", temp_dir / "setup.py")
    shutil.copy(project_root / "scripts/run_simulator.py", temp_dir / "run_simulator.py")

    logger.info("Copying example code to temp directory")
    shutil.copytree(project_root / "example_robots", temp_dir / "example_robots")

    logger.info("Creating zone folders")
    for i in range(NUM_ZONES):
        Path(temp_dir / f"zone_{i}").mkdir()

    shutil.copy(project_root / "example_robots/basic_robot.py", temp_dir / "zone_0/robot.py")

    logger.info("Creating VERSION file")
    (temp_dir / "simulator/VERSION").write_text(version)

    logger.info("Packaging project")
    shutil.make_archive(f"sbot-simulator-{version}", "zip", temp_dir)
    logger.info("Project packaged successfully")
    logger.info(f"Output file: sbot-simulator-{version}.zip")
