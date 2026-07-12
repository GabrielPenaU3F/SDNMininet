from mininet.net import Mininet
from mininet.node import RemoteController

def build_network(topology_cls, controller_ip="127.0.0.1", controller_port=6633):
    topo = topology_cls()

    net = Mininet(
        topo=topo,
        controller=None,
        autoSetMacs=False
    )

    net.addController(
        "c0",
        controller=RemoteController,
        ip=controller_ip,
        port=controller_port
    )

    return net
