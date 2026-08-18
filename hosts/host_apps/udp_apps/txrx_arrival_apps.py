import socket
import time

from hosts.host_apps.tx_rx_apps import TXRXHostApp
from traffic_models.arrival_processes import ArrivalProcess, PoissonProcess


class ArrivalProcessTXRXHostApp(TXRXHostApp):

    def __init__(self, process: ArrivalProcess, dst_ip: str, port: int, **kwargs):
        super().__init__(sender=self.send, receiver=self.listen)
        self.process = process
        self.dst_ip = dst_ip
        self.port = port
        self.tx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rx_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self):
        while True:
            dt = self.process.interarrival_time()
            time.sleep(dt)
            payload = f'Lorem ipsum'
            self._on_send(payload)

    def _on_send(self, payload):
        self.tx_socket.sendto(
            payload.encode('utf-8'),
            (self.dst_ip, self.port)
        )

    def listen(self):
        self.rx_socket.bind(('0.0.0.0', self.port))
        while True:
            data, addr = self.rx_socket.recvfrom(4096)


class PoissonArrivalTXRXHostApp(ArrivalProcessTXRXHostApp):

    def __init__(self, dst_ip: str, port: int, rate: float = 1, seed: int = 0):
        process = PoissonProcess(rate=rate, seed=seed)
        super().__init__(process, dst_ip, port)