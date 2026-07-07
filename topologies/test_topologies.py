from mininet.topo import Topo


class SimpleTopology(Topo):

    def build(self):

        s1 = self.addSwitch('s1')

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        self.addLink(h1, s1)
        self.addLink(h2, s1)


class TestTopologyTwo(Topo):

    def build(self):

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)

        self.addLink(s1, s2)
        self.addLink(h3, s2)
        self.addLink(h4, s2)

        self.addLink(s2, s3)
        self.addLink(h5, s3)


topos = {'simple_topo': SimpleTopology,
         'test_topo_2': TestTopologyTwo}