import argparse

from hosts.host_application import HostApplication
from hosts.silent_sender import SilentSender
from hosts.udp_receiver import UDPReceiver
from hosts.verbose_udp_receiver import VerboseUDPReceiver

if __name__ == '__main__':

    # Read args
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', required=True, type=int)

    # Parse
    args = parser.parse_args()
    sender = SilentSender()
    # receiver = UDPReceiver(args.port)
    receiver = VerboseUDPReceiver(args.port)

    host_app = HostApplication(sender, receiver)
    host_app.run()
