import socket
import sys


class UDPReceiver:

    def __init__(self, port: int):
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        # Le dice al kernel:
        # "Quiero recibir todos los paquetes UDP
        # destinados a este puerto."
        self.socket.bind(("0.0.0.0", port))

    def run(self):
        while True:
            data, sender = self.socket.recvfrom(4096)
            print(f"Recibido desde {sender}: {data.decode('utf-8')}")


if __name__ == "__main__":

    port = int(sys.argv[1])
    rcv = UDPReceiver(port)
    rcv.run()
