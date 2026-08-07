import time

from hosts.udp_receiver import UDPReceiver


class VerboseUDPReceiver(UDPReceiver):

    def _print_on_reception(self, sender, data):
        seq, send_time = data.decode('utf-8').split(',')
        recv_time = time.monotonic()
        latency = recv_time - float(send_time)
        with open('measurements/receiver.log', 'a') as f:
            f.write(f'{seq},{send_time},{recv_time},{latency}\n')
