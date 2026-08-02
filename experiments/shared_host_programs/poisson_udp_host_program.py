import argparse

from model.host import Host
from model.traffic_models.arrival_processes import PoissonProcess
from model.udp_receiver import UDPReceiver
from model.udp_sender import UDPSender
from model.verbose_udp_receiver import VerboseUDPReceiver
from model.verbose_udp_sender import VerboseUDPSender

if __name__ == '__main__':

    # Read args
    parser = argparse.ArgumentParser()
    parser.add_argument('--dst_ip', required=True, type=str)
    parser.add_argument('--port', required=True, type=int)
    parser.add_argument('--rate', required=True, type=float)
    parser.add_argument('--seed', default=0, type=int)

    # Parse
    args = parser.parse_args()
    process = PoissonProcess(args.rate, seed=args.seed)

    # Create UDP sender and receiver
    sender = VerboseUDPSender(
        process,
        args.dst_ip,
        args.port
    )
    receiver = UDPReceiver(args.port)
    host = Host(sender, receiver)
    host.run()
