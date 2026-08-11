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

        print('Receiver started')

        while True:
            data, addr = self.socket.recvfrom(4096)
            self._print_on_reception(addr, data)

    @staticmethod
    def _print_on_reception(sender, data):
        print(f"Received from {sender}: {data.decode('utf-8')}")


class VerboseSilentListenerHostApp(SilentListenerHostApp):

    def __init__(self, port):
        super().__init__(port)
        self._clean_resources()
        self.t0 = time.monotonic()

    def _print_on_reception(self, sender, data):
        super()._print_on_reception(sender, data)
        seq, send_time = data.decode('utf-8').split(',')
        recv_time = time.monotonic() - self.t0
        latency = recv_time - float(send_time)
        with open('measurements/receiver.log', 'a') as f:
            f.write(f'{seq},{send_time},{recv_time},{latency}\n')

    @staticmethod
    def _clean_resources():
        logfile = Path('measurements/receiver.log')
        logfile.unlink(missing_ok=True)


### MINIMAL SPEAKERS


class DeafSpeakerHostApp(BaseSpeakerHostApp):

    def __init__(self, dst_ip, port):
        super().__init__(dst_ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self):

        print('Sender started')

        i = 0
        t0 = time.monotonic()
        while True:
            msg = f'packet {i}'
            print(f'Time: {time.monotonic() - t0}')
            print(f'Sending: {msg}')

            try:
                self._on_send(i, msg)
                print('OK')
            except Exception as e:
                print('ERROR:', repr(e))
                raise

            i += 1
            time.sleep(1)

    def _on_send(self, seq, message):
        full_msg = f'Seq={seq},MSG={message}'
        self.socket.sendto(
            full_msg.encode('utf-8'),
            (self.dst_ip, self.port)
        )