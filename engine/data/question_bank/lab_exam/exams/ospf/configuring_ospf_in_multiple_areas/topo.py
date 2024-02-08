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

"""
Configure OSPF in Area 0 on R1 ( S0 ), R2 ( S0, E0 ).
Configure OSPF in Area 1 on R1 ( E0 ).
Configure OPSF in Area 2 on R2 ( S1 ), R3 ( S0, E0 )
verify--show ip ospf (Area ID)    show ip ospf interface R1-S0"""

verify_cmd = """vtysh -c \'show ip ospf border-routers\'
vtysh -c \'show ip ospf interface\'"""

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

        r1 = self.addNode('R1', cls=LinuxRouter, ip='1.1.1.1/8', privateDirs=self.privateDirs)
        r2 = self.addNode('R2', cls=LinuxRouter, ip='1.1.1.2/8', privateDirs=self.privateDirs)
        r3 = self.addNode('R3', cls=LinuxRouter, ip='2.2.2.2/8', privateDirs=self.privateDirs)

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')

        self.addLink(r1, r2, intfName1='R1-S0', params1={'ip':'1.1.1.1/8'}, intfName2='R2-S0', params2={'ip':'1.1.1.2/8'})
        self.addLink(r2, r3, intfName1='R2-S1', params1={'ip':'2.2.2.1/8'}, intfName2='R3-S0', params2={'ip':'2.2.2.2/8'})


        self.addLink(r1, h1, intfName1='R1-E0', params1={'ip':'10.1.1.1/8'})
        self.addLink(r2, h2, intfName1='R2-E0', params1={'ip':'20.1.1.1/8'})
        self.addLink(r3, h3, intfName1='R3-E0', params1={'ip':'30.1.1.1/8'})
        

def verify(net, verify_cmds, mode):

    cmds = verify_cmds.split('\n')
    r1 = net.get('R1')
    r2 = net.get('R2')
    r3 = net.get('R3')

    ip_ospf_border_r1, ip_ospf_border_r2, ip_ospf_border_r3 = r1.cmd(cmds[0]), r2.cmd(cmds[0]), r3.cmd(cmds[0])
    ip_ospf_interface = r3.cmd(cmds[1])

    def _verify(res, regex):
        
        _res = res.split('\n')
        for r in _res:
            if re.search(regex, r):
                 return True
        
        return False
    
    if mode == 'basic':
        flag1 = _verify(ip_ospf_border_r1, r'ABR') or _verify(ip_ospf_border_r2, r'ABR') and _verify(ip_ospf_border_r3, r'ABR')
        return flag1
    else:
        flag1 = _verify(ip_ospf_border_r1, r'ABR') or _verify(ip_ospf_border_r2, r'ABR') and _verify(ip_ospf_border_r3, r'ABR')
        flag2 = _verify(ip_ospf_interface, r'Timer intervals configured') # and _verify(ip_bgp, r'2.0.0.0/8(.*?)1.1.1.2(.*?)100 i')
        return flag1, flag2, flag1 and flag2



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
        time.sleep(50)
        res = verify(net, verify_cmd, mode)
        print(res)
        with open(f'{conf_path}/verify_res.txt', 'w') as f:
            f.write(str(res))
    else:
        time.sleep(50)
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