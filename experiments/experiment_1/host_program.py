import argparse

from src.host import Host
from src.udp_receiver import UDPReceiver
from src.udp_sender import UDPSender
from traffic_models.arrival_processes import PoissonProcess

if __name__ == "__main__":

    # Read args
    parser = argparse.ArgumentParser()
    parser.add_argument("--dst_ip", required=True, type=str)
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--rate", required=True, type=float)

    # Parse
    args = parser.parse_args()
    process = PoissonProcess(args.rate)

    # Create UDP sender and receiver
    sender = UDPSender(
        process,
        args.dst_ip,
        args.port
    )
    receiver = UDPReceiver(args.port)

    host = Host(sender, receiver)
    host.run()
