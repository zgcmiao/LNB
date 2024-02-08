from functools import partial
import os
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, Host
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import argparse
import re

verify_cmd = """vtysh -c \'show ip bgp summary\'
vtysh -c \'show ip route\'"""

privateDirs = ['/etc/frr', '/var/run/frr']
FRR_BIN_DIR = "/usr/lib/frr"

def clean():
    os.system("sudo killall -9 {} > /dev/null 2>&1"
              .format(' '.join(os.listdir(FRR_BIN_DIR))))
    # os.system("ps -aux|grep 'frr' | awk -F ' ' '{print $2}' | xargs sudo kill")

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    # pylint: disable=arguments-differ
    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()

class NetworkTopo(Topo):
    
    privateDirs = ['/etc/frr', '/var/run/frr']

    def build(self, **opts):

        R1 = self.addNode('R1', cls=LinuxRouter, ip='1.1.1.1/8', asnum=100, privateDirs=self.privateDirs)
        R2 = self.addNode('R2', cls=LinuxRouter, ip='1.1.1.2/8', asnum=200, privateDirs=self.privateDirs)

        self.addLink(R1, R2, intfName1='R1-S0', params1={'ip':'1.1.1.1/8'}, intfName2='R2-S0', params2={'ip':'1.1.1.2/8'})
        self.addLink(R1, R2, intfName1='R1-S1', params1={'ip':'2.2.2.1/8'}, intfName2='R2-S1', params2={'ip':'2.2.2.2/8'})

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        self.addLink(h1, R1, intfName2='R1-E0', params2={'ip':'10.1.1.1/8'})
        self.addLink(h2, R2, intfName2='R2-E0', params2={'ip':'20.1.1.1/8'})

def verify(net, verify_cmd, mode):

    r1 = net.get('R1')
    cmds = verify_cmd.split('\n')
    # print(cmds)

    ip_bgp_summary = r1.cmd(cmds[0])
    ip_route = r1.cmd(cmds[1])
    print(ip_route)

    def _verify(res, regex):
        
        _res = res.split('\n')
        for r in _res:
            if re.search(regex, r):
                 return True
        
        return False
    
    flag1 = _verify(ip_bgp_summary, r'75.75.75.75(.*?)200')    
    flag2 = re.search(r'75.75.75.75(.*?)via 1.1.1.2', ip_route, flags=re.DOTALL) is not None and re.search(r'75.75.75.75(.*?)via 2.2.2.2', ip_route, flags=re.DOTALL) is not None 

    return flag1 and flag2

def run(conf_path, mode, v):
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo, 
                   waitConnected=True )  

    net.start()
    # info( '*** Routing Table on Router:\n' )
    # info( net[ 'r0' ].cmd( 'route' ) )
    print(net.hosts)
    for r in net.hosts:
        if 'h' in r.name:
            continue
        r.cmdPrint(f'cp {conf_path}.conf /etc/frr/frr.conf')
        r.cmdPrint(f'cp {conf_path}/daemons /etc/frr/daemons')
        r.cmdPrint(f'cp {conf_path}/vtysh.conf /etc/frr/vtysh.conf')
        r.cmdPrint('/usr/lib/frr/frrinit.sh start')

    r1 = net.get('R1')
    r2 = net.get('R2')

    r1.cmd('ifconfig lo 50.50.50.50 netmask 255.255.255.255')
    r2.cmd('ifconfig lo 75.75.75.75 netmask 255.255.255.255')

    if v:
        res = verify(net, verify_cmd, mode)
        print(res)
        with open(f'{conf_path}/verify_res.txt', 'w') as f:
            f.write(str(res))
    else:
        CLI(net)
    net.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf_path', default='.', help='conf file path to read')
    parser.add_argument('--mode', choices=['basic','middle','hard'], default='hard', help='conf file path to read')
    parser.add_argument("--verify", action='store_true')
    args = parser.parse_args()

    setLogLevel( 'info' )
    run(args.conf_path, args.mode, args.verify)
    clean()