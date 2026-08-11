import time

from traffic_models.arrival_processes import ArrivalProcess
from hosts.host_apps.components.udp_sender import UDPSender


class VerboseUDPSender(UDPSender):

    def __init__(self, process: ArrivalProcess, dst_ip: str, dst_port: int):
        super().__init__(process, dst_ip, dst_port)
        self.t0 = time.monotonic()

    def _on_send(self, seq):

        payload = f'{seq},{time.monotonic() - self.t0}'
        with open('measurements/sender.log', 'a') as f:
            f.write(f'{payload}\n')

        self.socket.sendto(
            payload.encode('utf-8'),
            self.destination
        )
