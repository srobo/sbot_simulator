from sbot_interface.socket_server import DeviceServer, SocketServer


def setup_devices() -> SocketServer:
    # this is the configuration of devices connected to the robot
    devices = [
    ]

    device_servers = []

    for device in devices:
        # connect each device to a socket to receive commands from sbot
        device_servers.append(DeviceServer(device))

    # collect all device servers into a single server which will handle all connections and commands
    return SocketServer(device_servers)


def main() -> None:
    server = setup_devices()
    # generate and print the socket url and information for each device
    print(server.links_formatted())
    # start select loop for all server sockets and device sockets
    server.run()


if __name__ == '__main__':
    main()
