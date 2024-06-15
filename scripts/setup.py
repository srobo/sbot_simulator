#!/usr/bin/env python3
"""
This script is used to setup the environment for running the project in Webots.

It will:
1. Create a virtual environment in the project root, if it does not exist
2. Install the dependencies from requirements.txt in the virtual environment
3. Set the python path in runtime.ini to the virtual environment python
4. Repopulate the zone 0 folder with basic_robot.py if robot.py is missing
"""
import shutil
from pathlib import Path
from subprocess import run
from venv import create


if (Path(__file__).parent / 'simulator/VERSION').exists():
    # This is running from a release
    project_root = Path(__file__).parent
else:
    # This is running from the repository
    project_root = Path(__file__).parents[1]

venv_dir = project_root / "venv"
requirements = project_root / "requirements.txt"

print(f"Creating virtual environment in {venv_dir.absolute()}")
create(venv_dir, with_pip=True)

print(f"Installing dependencies from {requirements.absolute()}")
run([str(venv_dir / "bin/pip"), "install", "-r", str(requirements)], cwd=venv_dir)

print("Setting up Webots Python location")

runtime_ini = project_root / "simulator/controllers/usercode_runner/runtime.ini"
runtime_content = []
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
    elif in_python_section and line.startswith("["):
        in_python_section = False
    elif not in_python_section:
        runtime_content.append(line)

runtime_content.extend([
    "",
    "[python]",
    f"COMMAND = {(venv_dir / 'bin/python').absolute()}",
])

runtime_ini.write_text('\n'.join(runtime_content))

# repopulate zone 0 with example code if robot.py is missing
zone_0 = project_root / "zone_0"
if not (zone_0 / "robot.py").exists():
    print("Repopulating zone 0 with example code")
    zone_0.mkdir(exist_ok=True)
    shutil.copy(project_root / "example_roobts/basic_robot.py", zone_0 / "robot.py")
