from functools import partial
import code
import os
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, Host
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import Link, Intf, TCIntf, OVSIntf

class LinuxRouter(Node):
    
    def config(self, **opts):
        super(LinuxRouter, self).config(**opts)
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class testTopo(Topo):

    def build(self, **opts):
        r1 = self.addNode('r1', cls=LinuxRouter, ip='1.1.1.1/8', asnum=200)
        r2 = self.addNode('r2', cls=LinuxRouter, ip='2.2.2.2/8', asnum=200)
        r3 = self.addNode('r3', cls=LinuxRouter, ip='3.3.3.3/8', asnum=200)
        self.addLink(r1, r2)
        self.addLink(r1, r3)

def run():
    net = Mininet(topo=testTopo())
    net.start()
    r1 = net.get('r1')
    r2 = net.get('r2')
    r3 = net.get('r3')

    new_intf = Intf('eno1', node=r2)
    # r2.addIntf(new_intf)

    # code.interact(local=locals())
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()