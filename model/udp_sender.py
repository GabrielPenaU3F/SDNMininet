import socket
import time

from traffic_models.arrival_processes import ArrivalProcess


class UDPSender:

    def __init__(self, process: ArrivalProcess, dst_ip: str, dst_port: int):
        self.process = process

        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        self.destination = (dst_ip, dst_port)

    def run(self):
        while True:
            dt = self.process.interarrival_time()
            time.sleep(dt)

            self.socket.sendto(
                b"Lorem ipsum",
                self.destination
            )