from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.node import Host as MininetHost, Switch as MininetSwitch

from hosts.host import Host


class NetworkManager:

    def __init__(self, topology_cls, **kwargs):
        self.topology_cls = topology_cls
        self.net = None
        self._running = False
        self._hosts = {}

    def build_network(self, controller_ip='127.0.0.1', controller_port=6633):
        topo = self.topology_cls()
        net = Mininet(
            topo=topo,
            controller=None,
            autoSetMacs=False
        )

        net.addController(
            'c0',
            controller=RemoteController,
            ip=controller_ip,
            port=controller_port
        )

        self.net = net
        self._wrap_hosts()
        return net

    @property
    def network_online(self):
        return self._running

    # noinspection PyProtectedMember
    def start(self):
        self.net.start()
        self._running = True
        for host in self._hosts.values():
            host._start()

    # noinspection PyProtectedMember
    def stop(self):
        if self.net is not None:
            for host in self._hosts.values():
                host._stop()
            self._running = False
            self.net.stop()

    # This does NOT support switches
    def _wrap_hosts(self):
        self._hosts = {
            name: Host(mn_host)
            for name, mn_host in self.net.nameToNode.items()
            if isinstance(mn_host, MininetHost)
        }

    def host(self, hostname):
        return self._hosts[hostname]

    def switch(self, swname):
        switch = self.net[swname]
        if isinstance(switch, MininetSwitch):
            return switch
        return None
