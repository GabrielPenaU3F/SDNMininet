import mininet.clean as mn_clean
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.node import Host as MininetHost, Switch as MininetSwitch

from hosts.host import Host


class NetworkManager:

    def __init__(self, topology_cls, **kwargs):
        self.topology_cls = topology_cls
        self.net = None
        self._hosts = {}

    def deploy_network(self, controller_ip='127.0.0.1', controller_port=6633):
        if self.net is not None:
            self.destroy_network()

        self.net = self._build_network(controller_ip, controller_port)
        self._wrap_hosts()
        self.net.start()

    def _build_network(self, controller_ip='127.0.0.1', controller_port=6633):
        topo = self.topology_cls()
        try:
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

        except Exception:
            self._clean_network()
            raise

        return net

    @property
    def network_online(self):
        return self.net is not None

    # noinspection PyProtectedMember
    def _stop_hosts(self):
        for host in self._hosts.values():
            host._stop()

    # Stops and destroys the network
    def destroy_network(self):
        if self.net is not None:
            self._stop_hosts()
            self._hosts.clear()
            self.net.stop()
            self.net = None

    # This does NOT support switches - for now, we wrap only hosts
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

    @staticmethod
    def _clean_network():
        mn_clean.cleanup()