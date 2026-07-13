from mininet.topo import Topo


class AwadDDoSTopology(Topo):

    def build(self):

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        h1 = self.addHost('h1', ip="10.0.0.1/24", mac="00:00:00:00:00:01")
        h2 = self.addHost('h2', ip="10.0.0.2/24", mac="00:00:00:00:00:02")
        h3 = self.addHost('h3', ip="10.0.0.3/24", mac="00:00:00:00:00:03")
        h4 = self.addHost('h4', ip="10.0.0.4/24", mac="00:00:00:00:00:04")
        h5 = self.addHost('h5', ip="10.0.0.5/24", mac="00:00:00:00:00:05")
        h6 = self.addHost('h6', ip="10.0.0.6/24", mac="00:00:00:00:00:06")
        h7 = self.addHost('h7', ip="10.0.0.7/24", mac="00:00:00:00:00:07")
        h8 = self.addHost('h8', ip="10.0.0.8/24", mac="00:00:00:00:00:08")

        self.addLink(h1, s1)
        self.addLink(h2, s1)

        self.addLink(h3, s2)
        self.addLink(h4, s2)

        self.addLink(h5, s3)
        self.addLink(h6, s3)

        self.addLink(h7, s4)
        self.addLink(h8, s4)

        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, s4)
