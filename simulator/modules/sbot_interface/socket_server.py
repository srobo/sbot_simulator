from __future__ import annotations

import sys
import logging
import select
import socket
from threading import Event
from typing import Protocol

from sbot_interface.devices.util import get_globals

LOGGER = logging.getLogger(__name__)
g = get_globals()


class Board(Protocol):
    asset_tag: str
    software_version: str

    def handle_command(self, command: str) -> str | bytes:
        pass


class DeviceServer:
    def __init__(self, board: Board) -> None:
        self.board = board
        # create TCP socket server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 0))
        self.server_socket.listen(1)  # only allow one connection per device
        self.server_socket.setblocking(True)
        LOGGER.info(f'Started server for {self.board_type} ({self.board.asset_tag}) on port {self.port}')

        self.device_socket: socket.socket | None = None
        self.buffer = b''

    def process_data(self, data: bytes) -> bytes | None:
        self.buffer += data
        if b'\n' in self.buffer:
            # Sleep to simulate processing time
            g.sleep(g.timestep / 1000)
            data, self.buffer = self.buffer.split(b'\n', 1)
            return self.run_command(data.decode().strip())
        else:
            return None

    def run_command(self, command: str) -> bytes:
        LOGGER.debug(f'> {command}')
        try:
            response = self.board.handle_command(command)
            if isinstance(response, bytes):
                LOGGER.debug(f'< {len(response)} bytes')
                return response
            else:
                LOGGER.debug(f'< {response}')
                return response.encode() + b'\n'
        except Exception as e:
            LOGGER.exception(f'Error processing command: {command}')
            return f'NACK:{e}\n'.encode()

    def flush_buffer(self) -> None:
        self.buffer = b''

    def socket(self) -> socket.socket:
        """
        Return the socket to select on.

        If the device is connected, return the device socket. Otherwise, return the server socket.
        """
        if self.device_socket is not None:
            # ignore the server socket while we are connected
            return self.device_socket
        else:
            return self.server_socket

    def accept(self) -> None:
        if self.device_socket is not None:
            self.disconnect_device()
        self.device_socket, _ = self.server_socket.accept()
        self.device_socket.setblocking(True)
        LOGGER.info(f'Connected to {self.asset_tag} from {self.device_socket.getpeername()}')

    def disconnect_device(self) -> None:
        self.flush_buffer()
        if self.device_socket is not None:
            self.device_socket.close()
            self.device_socket = None
            LOGGER.info(f'Disconnected from {self.asset_tag}')

    def close(self) -> None:
        self.disconnect_device()
        self.server_socket.close()

    def __del__(self) -> None:
        self.close()

    @property
    def port(self) -> int:
        if self.server_socket is None:
            return -1
        return self.server_socket.getsockname()[1]

    @property
    def asset_tag(self) -> str:
        return self.board.asset_tag

    @property
    def board_type(self) -> str:
        return self.board.__class__.__name__


class SocketServer:
    def __init__(self, devices: list[DeviceServer]) -> None:
        self.devices = devices
        self.stop_event = Event()
        g.stop_event = self.stop_event

    def run(self) -> None:
        while not self.stop_event.is_set():
            # select on all server sockets and device sockets
            sockets = [device.socket() for device in self.devices]

            readable, _, _ = select.select(sockets, [], [], 0.5)

            for device in self.devices:
                try:
                    if device.server_socket in readable:
                        device.accept()

                    if device.device_socket in readable:
                        try:
                            if sys.platform == 'win32':
                                data = device.device_socket.recv(4096)
                            else:
                                data = device.device_socket.recv(4096, socket.MSG_DONTWAIT)
                        except ConnectionError:
                            device.disconnect_device()
                            continue

                        if not data:
                            device.disconnect_device()
                        else:
                            response = device.process_data(data)
                            if response is not None:
                                try:
                                    device.device_socket.sendall(response)
                                except ConnectionError:
                                    device.disconnect_device()
                                    continue
                except Exception as e:
                    LOGGER.exception(f"Failure in simulated boards: {e}")

    def links(self) -> dict[str, dict[str, str]]:
        return {
            device.asset_tag: {
                'board_type': device.board_type,
                'port': str(device.port),
            }
            for device in self.devices
        }

    def links_formatted(self, address='localhost') -> str:
        return '\n'.join(
            f"socket://{address}:{data['port']}/{data['board_type']}/{asset_tag}"
            for asset_tag, data in self.links().items()
        )
