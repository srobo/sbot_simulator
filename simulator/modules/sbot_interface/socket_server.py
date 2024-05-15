import select
import socket
from typing import Optional, Protocol


class Board(Protocol):
    asset_tag: str
    software_version: str

    def handle_command(self, command: str) -> str:
        pass


class DeviceServer:
    def __init__(self, board: Board) -> None:
        self.board = board
        # create TCP socket server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 0))
        self.server_socket.listen(1)  # only allow one connection per device
        self.server_socket.setblocking(False)

        self.device_socket: Optional[socket.socket] = None
        self.buffer = b''

    def process_data(self, data: bytes) -> Optional[bytes]:
        self.buffer += data
        if b'\n' in self.buffer:
            data, self.buffer = self.buffer.split(b'\n', 1)
            return self.run_command(data.decode()).encode()
        else:
            return None

    def run_command(self, command: str) -> str:
        try:
            return self.board.handle_command(command) + '\n'
        except Exception as e:
            return f'NACK:{e}\n'

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
        self.device_socket.setblocking(False)

    def disconnect_device(self) -> None:
        self.flush_buffer()
        if self.device_socket is not None:
            self.device_socket.close()
            self.device_socket = None

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
        return self.board.__qualname__


class SocketServer:
    def __init__(self, devices: list[DeviceServer]) -> None:
        self.devices = devices

    def run(self) -> None:
        while True:
            # select on all server sockets and device sockets
            sockets = [device.socket() for device in self.devices]

            readable, _, _ = select.select(sockets, [], [])

            for device in self.devices:
                if device.server_socket in readable:
                    device.accept()

                if device.device_socket in readable:
                    data = device.device_socket.recv(4096)
                    if not data:
                        device.disconnect_device()
                    else:
                        response = device.process_data(data)
                        if response is not None:
                            device.device_socket.send(response)

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
            f"socket://{address}:{port}/{board_type}/{asset_tag};"
            for asset_tag, data in self.links().items()
            for board_type, port in data.items()
        )
