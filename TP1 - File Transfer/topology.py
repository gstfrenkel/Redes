from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.node import OVSSwitch, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def create_topology():
    # Inicializa la topología de red
    net = Mininet(controller=RemoteController, switch=OVSSwitch)

    # Agrega el controlador
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    # Agrega el switch
    s1 = net.addSwitch('s1')

    # Agrega los hosts
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    h4 = net.addHost('h4')

    # Conecta los hosts y el switch
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    net.addLink(h4, s1)

    # Inicia la red
    net.build()
    
    # Inicia el controlador
    c0.start()
    
    # Inicia los switches
    net.get('s1').start([c0])
    
    return net

if __name__ == '__main__':
    setLogLevel('info')
    net = create_topology()
    CLI(net)
    net.stop()
