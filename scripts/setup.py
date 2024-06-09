#!/usr/bin/env python3
"""
This script is used to setup the environment for running the project in Webots.

It will:
1. Create a virtual environment in the project root, if it does not exist
2. Install the dependencies from requirements.txt in the virtual environment
3. Set the python path in runtime.ini to the virtual environment python
4. Repopulate the zone 0 folder with basic_robot.py if robot.py is missing
"""
