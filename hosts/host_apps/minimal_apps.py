import socket
import time

from hosts.host_apps.tx_rx_apps import TXRXHostApp


class SilentListenerHostApp(TXRXHostApp):

    def __init__(self, port):
        self.port = port
        super().__init__(lambda: '', self.listen)

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', self.port))

        print('Receiver started')

        while True:
            data, addr = sock.recvfrom(4096)
            print(f'Received from {addr}: {data.decode()}')


class DeafSpeakerHostApp(TXRXHostApp):

    def __init__(self, dst_ip, port):
        self.dst_ip = dst_ip
        self.port = port
        super().__init__(self.send, lambda: '')

    def send(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dst = (self.dst_ip, self.port)
        print('Sender started')

        i = 0
        t0 = time.monotonic()
        while True:
            msg = f'packet {i}'
            print(f'Time: {time.monotonic() - t0}')
            print(f'Sending: {msg}')

            try:
                sock.sendto(msg.encode(), dst)
                print('OK')
            except Exception as e:
                print('ERROR:', repr(e))
                raise

            i += 1
            time.sleep(1)