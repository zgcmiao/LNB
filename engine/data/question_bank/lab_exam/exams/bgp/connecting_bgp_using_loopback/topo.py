from functools import partial
import os
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, Host
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
import re
import argparse

verify_cmd = "vtysh -c \'show ip bgp summary\'"

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
        r2 = self.addNode('R2', cls=LinuxRouter, ip='1.1.1.2/8', asnum=100, privateDirs=self.privateDirs)
        r3 = self.addNode('R3', cls=LinuxRouter, ip='2.2.2.2/8', asnum=100, privateDirs=self.privateDirs)

        self.addLink(r1, r2, intfName1='R1-S0', params1={'ip':'1.1.1.1/8'}, intfName2='R2-S0', params2={'ip':'1.1.1.2/8'})
        self.addLink(r2, r3, intfName1='R2-S1', params1={'ip':'2.2.2.1/8'}, intfName2='R3-S0', params2={'ip':'2.2.2.2/8'})
        self.addLink(r1, r3, intfName1='R1-S1', params1={'ip':'3.3.3.1/8'}, intfName2='R3-S1', params2={'ip':'3.3.3.2/8'})

        for s in range(3):
            for t in range(2):
                self.addHost('h%s-%s' %(s+1, t))

def verify(net, verify_cmd, mode):

    r1 = net.get('R1')
    cmds = verify_cmd.split('\n')
    print(cmds)

    ip_bgp_summary = r1.cmd(cmds[0])

    def _verify(res, regex):
        
        _res = res.split('\n')
        for r in _res:
            if re.search(regex, r):
                 return True
        
        return False
    
    flag1 = _verify(ip_bgp_summary, r'75.75.75.75(.*?)100') and _verify(ip_bgp_summary, r'100.100.100.100(.*?)100')

    return flag1
        

def run(conf_path, mode, v):
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo, 
                   waitConnected=True )  
    
    net.addLink(net.get('h1-0'), net.get('R1'), intfName2='R1-E0', params2={'ip':'10.1.1.1/8'})
    # net.addLink(net.get('h1-1'), net.get('r1'), intfName2='r1-lo', params2={'ip':'50.50.50.50/32'})
    net.addLink(net.get('h2-0'), net.get('R2'), intfName2='R2-E0', params2={'ip':'20.1.1.1/8'})
    # net.addLink(net.get('h2-1'), net.get('r2'), intfName2='r2-lo', params2={'ip':'75.75.75.75/32'})
    net.addLink(net.get('h3-0'), net.get('R3'), intfName2='R3-E0', params2={'ip':'30.1.1.1/8'})
    # net.addLink(net.get('h3-1'), net.get('r3'), intfName2='r3-lo', params2={'ip':'100.100.100.100/32'})

    net.start()
    # info( '*** Routing Table on Router:\n' )
    # info( net[ 'r0' ].cmd( 'route' ) )
    # print(net.hosts)
    for r in net.hosts:
        if 'h' in r.name:
            continue
        r.cmdPrint(f'cp {conf_path}.conf /etc/frr/frr.conf')
        r.cmdPrint(f'cp {conf_path}/daemons /etc/frr/daemons')
        r.cmdPrint(f'cp {conf_path}/vtysh.conf /etc/frr/vtysh.conf')
        r.cmdPrint('/usr/lib/frr/frrinit.sh start')

    r1 = net.get('R1')
    r2 = net.get('R2')
    r3 = net.get('R3')

    r1.cmd('ifconfig lo 50.50.50.50 netmask 255.255.255.255')
    r2.cmd('ifconfig lo 75.75.75.75 netmask 255.255.255.255')
    r3.cmd('ifconfig lo 100.100.100.100 netmask 255.255.255.255')
    # r1.setIP(ip='50.50.50.50/32', intf='lo')
    # r2.setIP(ip='75.75.75.75/32', intf='lo')
    # r3.setIP(ip='100.100.100.100/32', intf='lo')

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
        