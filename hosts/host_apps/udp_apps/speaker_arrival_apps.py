import socket
import time
from pathlib import Path

from hosts.host_apps.minimal_apps import DeafSpeakerHostApp
from traffic_models.arrival_processes import ArrivalProcess, PoissonProcess


class ArrivalProcessSpeakerHostApp(DeafSpeakerHostApp):

    def __init__(self, process: ArrivalProcess, dst_ip: str, port: int, **kwargs):
        super().__init__(dst_ip, port)
        self.process = process
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    '''
        Careful: need to compare vs absolute deadlines 
        to void accumulating scheduler delays
    '''

    def send(self):
        seq = 0
        t0 = time.monotonic()
        ideal_t = 0.0
        while True:
            dt = self.process.interarrival_time()
            ideal_t += dt
            sleep_time = ideal_t - (time.monotonic() - t0)
            if sleep_time > 0:
                time.sleep(sleep_time)

            t = time.monotonic()
            real_t = t - t0
            error = real_t - ideal_t
            payload = f'{seq},{ideal_t},{real_t},{error}'
            self._on_send(payload)
            seq += 1

    @property
    def logfile(self):
        return Path('logs/sender.log')


class VerboseArrivalProcessSpeakerHostApp(ArrivalProcessSpeakerHostApp):

    def __init__(self, process: ArrivalProcess, dst_ip: str, port: int, **kwargs):
        super().__init__(process, dst_ip, port)


class PoissonArrivalSpeakerHostApp(VerboseArrivalProcessSpeakerHostApp):

    def __init__(self, dst_ip: str, port: int, rate: float=1, seed: int=0):
        process = PoissonProcess(rate=rate, seed=seed)
        super().__init__(process, dst_ip, port)
