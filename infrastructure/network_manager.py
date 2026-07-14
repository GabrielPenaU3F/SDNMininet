from mininet.net import Mininet
from mininet.node import RemoteController


class NetworkManager:

    def __init__(self, topology_cls, **kwargs):
        self.topology_cls = topology_cls
        self._net = None

    def build_network(self, controller_ip="127.0.0.1", controller_port=6633):
        topo = self.topology_cls()
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

        self._net = net
        return net

    def start(self):
        self._net.start()

    def stop(self):
        if self._net is not None:
            self._net.stop()
