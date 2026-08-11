import socket
import time

from hosts.host_apps.minimal_apps import DeafSpeakerHostApp
from traffic_models.arrival_processes import ArrivalProcess, PoissonProcess


class ArrivalProcessSpeakerHostApp(DeafSpeakerHostApp):

    def __init__(self, process: ArrivalProcess, dst_ip: str, port: int, **kwargs):
        super().__init__(dst_ip, port)
        self.process = process

        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

    def send(self):
        seq = 0
        while True:
            dt = self.process.interarrival_time()
            time.sleep(dt)
            self._on_send(seq, 'Lorem ipsum')
            seq += 1


class VerboseArrivalProcessSpeakerHostApp(ArrivalProcessSpeakerHostApp):

    def __init__(self, process: ArrivalProcess, dst_ip: str, port: int, **kwargs):
        super().__init__(process, dst_ip, port)
        self.t0 = time.monotonic()

    def _on_send(self, seq, message):

        payload = f'{seq},{time.monotonic() - self.t0}'
        with open('measurements/sender.log', 'a') as f:
            f.write(f'{payload}\n')

        super()._on_send(seq, message)


class PoissonArrivalSpeakerHostApp(VerboseArrivalProcessSpeakerHostApp):

    def __init__(self, dst_ip: str, port: int, rate: float=1, seed: int=0):
        process = PoissonProcess(rate=rate, seed=seed)
        super().__init__(process, dst_ip, port)
