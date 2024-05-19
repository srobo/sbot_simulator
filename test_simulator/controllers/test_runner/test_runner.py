import os
import socket
import sys
import threading
from pprint import pprint

from controller import Robot, Camera

FRAME_TIME = 64

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

camera: Camera = robot.getDevice("camera")
camera.enable(FRAME_TIME)

def test_recv_setup():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind(('localhost', 0))
    soc.listen(1)
    return soc

def recv_runner(soc):
    while True:
        client = soc.accept()
        while client[0].recv(4096):
            pass

srv_soc = test_recv_setup()
srv_port = srv_soc.getsockname()[1]
threading.Thread(target=recv_runner, args=(srv_soc,)).start()

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect(("localhost", srv_port))
while robot.step(FRAME_TIME) != -1:
    image = camera.getImage()
    soc.sendall(bytes(len(image)))
    soc.sendall(image)
