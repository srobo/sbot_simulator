import os
import sys
from pprint import pprint

from controller import Robot

robot = Robot()

sys.path.insert(0, robot.getProjectPath())
import environment  # noqa: E402
environment.setup_environment()

print(f"{robot.getProjectPath()=}")

print(f"""
{os.getcwd()=}
{environment.SIM_ROOT=}
{environment.ZONE_ROOT=}
{environment.MODULES_ROOT=}
""")

print("Environment variables:")
pprint(dict(os.environ))
print('')
print("Path:")
pprint(sys.path)
