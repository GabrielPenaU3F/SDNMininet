import socket
import time
from pathlib import Path

from hosts.host_apps.tx_rx_apps import BaseListenerHostApp, BaseSpeakerHostApp


### MINIMAL LISTENERS

class SilentListenerHostApp(BaseListenerHostApp):

    def __init__(self, port):
        super().__init__(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def listen(self):
        self.socket.bind(('0.0.0.0', self.port))
        print('Listening', flush=True)
        while True:
            data, addr = self.socket.recvfrom(4096)
            self._print_on_reception(addr, data)

    @staticmethod
    def _print_on_reception(sender, data):
        print(f"Received from {sender}: {data.decode('utf-8')}")


class VerboseSilentListenerHostApp(SilentListenerHostApp):

    def __init__(self, port):
        super().__init__(port)
        self.t0 = time.monotonic()

    def _print_on_reception(self, sender, data):
        super()._print_on_reception(sender, data)
        seq, send_time = data.decode('utf-8').split(',')
        recv_time = time.monotonic() - self.t0
        latency = recv_time - float(send_time)
        with open(self.logfile, 'a') as f:
            f.write(f'SEQ: {seq}, SENT AT: {send_time}, RECV AT: {recv_time}, LAG: {latency}\n')

    @property
    def logfile(self):
        return Path('logs/receiver.log')


### MINIMAL SPEAKERS


class DeafSpeakerHostApp(BaseSpeakerHostApp):

    def __init__(self, dst_ip, port):
        super().__init__(dst_ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self):
        i = 0
        t0 = time.monotonic()
        while True:
            payload = f'{i},{time.monotonic() - t0}'
            self._on_send(payload)
            print('Packet sent', flush=True)
            i += 1
            time.sleep(self._idle_time())

    @staticmethod
    def _idle_time():
        return 1

    def _on_send(self, payload):
        self.socket.sendto(
            payload.encode('utf-8'),
            (self.dst_ip, self.port)
        )

    @property
    def logfile(self):
        return Path('logs/sender.log')