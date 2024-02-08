from functools import partial
import os
import argparse
import time
import re
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, Host
from mininet.log import setLogLevel, info
from mininet.cli import CLI

from verify import verify_cmd

privateDirs = ['/etc/frr', '/var/run/frr']
FRR_BIN_DIR = "/usr/lib/frr"

def clean():
    os.system("sudo killall -9 {} > /dev/null 2>&1"
              .format(' '.join(os.listdir(FRR_BIN_DIR))))
    # os.system("ps -aux | grep 'frr' | awk -F ' ' '{print $2}' | xargs sudo kill")

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

        r1 = self.addNode('R1', cls=LinuxRouter, ip='1.1.1.1/8', asnum=200, privateDirs=self.privateDirs)
        r2 = self.addNode('R2', cls=LinuxRouter, ip='1.1.1.2/8', asnum=100, privateDirs=self.privateDirs)
        r3 = self.addNode('R3', cls=LinuxRouter, ip='2.2.2.2/8', asnum=200, privateDirs=self.privateDirs)

        h1 = self.addHost('h1', ip='10.1.1.2/8')
        h2 = self.addHost('h2', ip='20.1.1.2/8')
        h3 = self.addHost('h3', ip='30.1.1.2/8')

        self.addLink(r1, r2, intfName1='R1-S0', params1={'ip':'1.1.1.1/8'}, intfName2='R2-S0', params2={'ip':'1.1.1.2/8'})
        self.addLink(r2, r3, intfName1='R2-S1', params1={'ip':'2.2.2.1/8'}, intfName2='R3-S0', params2={'ip':'2.2.2.2/8'})
        self.addLink(r1, r3, intfName1='R1-S1', params1={'ip':'3.3.3.1/8'}, intfName2='R3-S1', params2={'ip':'3.3.3.2/8'})

        self.addLink(r1, h1, intfName1='R1-E0', params1={'ip':'10.1.1.1/8'})
        self.addLink(r2, h2, intfName1='R2-E0', params1={'ip':'20.1.1.1/8'})
        self.addLink(r3, h3, intfName1='R3-E0', params1={'ip':'30.1.1.1/8'})
        

def verify(r1, verify_cmd, mode):

    cmds = verify_cmd.split('\n')
    r1 = r1

    ip_bgp_summary = r1.cmd(cmds[0])
    ip_route = r1.cmd(cmds[1])
    ip_bgp = r1.cmd(cmds[2])

    def _verify(res, regex):
        
        _res = res.split('\n')
        for r in _res:
            if re.search(regex, r):
                 return True
        
        return False
    
    flag1 = _verify(ip_bgp_summary, r'1.1.1.2(.*?)100') and _verify(ip_bgp_summary, r'3.3.3.2(.*?)200')
    flag2 = _verify(ip_route, r'2.0.0.0/8(.*?)via 3.3.3.2') and _verify(ip_route, r'20.0.0.0/8(.*?)via 1.1.1.2') and _verify(ip_route, r'30.0.0.0/8(.*?)via 3.3.3.2')
    flag3 = _verify(ip_bgp, r'1.0.0.0/8(.*?)1.1.1.2(.*?)100 i') # and _verify(ip_bgp, r'2.0.0.0/8(.*?)1.1.1.2(.*?)100 i')

    return (flag1, flag2, flag3, flag1 and flag2 and flag3)



def run(conf_path, mode, v):
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo, 
                   waitConnected=True )  # controller is used by s1-s3
    net.start()
    # info( '*** Routing Table on Router:\n' )
    # info( net[ 'r0' ].cmd( 'route' ) )
    for r in net.hosts:
        if "h" in r.name:
            continue
        r.cmd(f'cp {conf_path}/{r.name}.conf /etc/frr/frr.conf')
        r.cmd(f'cp {conf_path}/daemons /etc/frr/daemons')
        r.cmd(f'cp {conf_path}/vtysh.conf /etc/frr/vtysh.conf')
        r.cmd('/usr/lib/frr/frrinit.sh start')

    time.sleep(3)

    if v:
        r1 = net.get('R1')
        res = verify(r1, verify_cmd, mode)
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
        