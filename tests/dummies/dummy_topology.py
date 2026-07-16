from mininet.topo import Topo


class DummyTopology(Topo):

    def build(self):
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1')
        self.addLink(s1, h1)