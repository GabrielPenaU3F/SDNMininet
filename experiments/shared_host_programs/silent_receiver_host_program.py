import argparse

from model.host import Host
from model.silent_sender import SilentSender
from model.udp_receiver import UDPReceiver
from model.verbose_udp_receiver import VerboseUDPReceiver

if __name__ == '__main__':

    # Read args
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', required=True, type=int)

    # Parse
    args = parser.parse_args()
    sender = SilentSender()
    # receiver = UDPReceiver(args.port)
    receiver = VerboseUDPReceiver(args.port)

    host = Host(sender, receiver)
    host.run()
