from mininet.topo import Topo


class Topology(Topo):
    def build(self, switches_number=2):
        leftHost1 = self.addHost('h1')
        leftHost2 = self.addHost('h2')
        rightHost1 = self.addHost('h3')
        rightHost2 = self.addHost('h4')

        switches = []
        for i in range(switches_number):
            switch_name = "s" + str(i)
            switches.append(self.addSwitch(switch_name))

        self.addLink(leftHost1, switches[0])
        self.addLink(leftHost2, switches[0])
        self.addLink(rightHost1, switches[len(switches) - 1])
        self.addLink(rightHost2, switches[len(switches) - 1])
        for i in range(len(switches) - 1):
            self.addLink(switches[i], switches[i + 1])


topos = {'customTopo': Topology}
