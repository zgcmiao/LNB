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

verify_cmd = """vtysh -c \'show ip route\'
vtysh -c \'show ip bgp 10.0.0.0\'"""

"""
Configure BGP on all the routers. Configure R1, R2 and R4 in AS 100. Configure R3 in
AS 200. Network 10.0.0.0 should not be sent ouside AS 100 using no-export community
attribute
10.0.0.0/8 not in R2 and R3 routing table"""

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

        r1 = self.addNode('R1', cls=LinuxRouter, ip='1.1.1.1/8', asnum=100, privateDirs=self.privateDirs)
        r2 = self.addNode('R2', cls=LinuxRouter, ip='3.3.3.1/8', asnum=100, privateDirs=self.privateDirs)
        r3 = self.addNode('R3', cls=LinuxRouter, ip='2.2.2.2/8', asnum=200, privateDirs=self.privateDirs)
        r4 = self.addNode('R4', cls=LinuxRouter, ip='3.3.3.2/8', asnum=100, privateDirs=self.privateDirs)

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        self.addLink(r2, r4, intfName1='R2-S0', params1={'ip':'3.3.3.1/8'}, intfName2='R4-S0', params2={'ip':'3.3.3.2/8'})
        self.addLink(r1, r2, intfName1='R1-S0', params1={'ip':'1.1.1.1/8'}, intfName2='R2-S1', params2={'ip':'1.1.1.2/8'})
        self.addLink(r2, r3, intfName1='R2-S2', params1={'ip':'2.2.2.1/8'}, intfName2='R3-S0', params2={'ip':'2.2.2.2/8'})

        self.addLink(r1, h1, intfName1='R1-E0', params1={'ip':'10.1.1.1/8'})
        self.addLink(r2, h2, intfName1='R2-E0', params1={'ip':'20.1.1.1/8'})
        self.addLink(r3, h3, intfName1='R3-E0', params1={'ip':'30.1.1.1/8'})
        self.addLink(r4, h4, intfName1='R4-E0', params1={'ip':'40.1.1.1/8'})
        

def verify(net, verify_cmd, mode):

    cmds = verify_cmd.split('\n')
    ip_route_cmd, ip_bgp_10_cmd = cmds[0], cmds[1]
    r2, r3, r4 = net.get('R2'), net.get('R3'), net.get('R4')

    def _verify(res, regex):
        
        _res = res.split('\n')
        for r in _res:
            if re.search(regex, r):
                 return True
        
        return False
    
    if mode == 'basic':
        ip_route = r3.cmd(ip_route_cmd)
        flag1 = _verify(ip_route, r'10.0.0.0/8(.*?)')
        return flag1
    
    elif mode == 'middle':
        ip_bgp_10 = r3.cmd(ip_bgp_10_cmd)
        flag1 = re.search(r'100(.*?)2.2.2.1(.*?)20.1.1.1(.*?)Community: 100:1', ip_bgp_10, flags=re.DOTALL) is not None
        return flag1
    
    else:
        ip_route_r2, ip_route_r3 = r2.cmd(ip_route_cmd), r3.cmd(ip_route_cmd)
        flag1 = _verify(ip_route_r2, r'10.0.0.0/8(.*?)')
        flag2 = not _verify(ip_route_r3, r'10.0.0.0/8')
        return (flag1, flag2, flag1 and flag2)


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
        if mode == 'basic' and (r.name+'_base.conf') in os.listdir(conf_path):
            r.cmdPrint(f'cp {conf_path}/{r.name}_base.conf /etc/frr/frr.conf')
        elif mode == 'middle' and (r.name+'_middle.conf') in os.listdir(conf_path):
            r.cmdPrint(f'cp {conf_path}/{r.name}_middle.conf /etc/frr/frr.conf')
        else:
            r.cmdPrint(f'cp {conf_path}/{r.name}.conf /etc/frr/frr.conf')
        r.cmdPrint(f'cp {conf_path}/daemons /etc/frr/daemons')
        r.cmdPrint(f'cp {conf_path}/vtysh.conf /etc/frr/vtysh.conf')
        r.cmdPrint('/usr/lib/frr/frrinit.sh start')

    if v:
        time.sleep(10)
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