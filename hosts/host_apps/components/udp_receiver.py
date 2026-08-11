import socket


class UDPReceiver:

    def __init__(self, port: int):
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        self.socket.bind(('0.0.0.0', port))

    def begin_listening(self):
        while True:
            data, sender = self.socket.recvfrom(4096)
            self._print_on_reception(sender, data)

    def _print_on_reception(self, sender, data):
        print(f"Received from {sender}: {data.decode('utf-8')}")
