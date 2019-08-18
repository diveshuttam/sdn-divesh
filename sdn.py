from mininet.topo import Topo
from mininet.node import Controller
from os import environ

class SdnTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')

        s1 = self.addSwitch( 's1', protocols='OpenFlow13' )
        s2 = self.addSwitch( 's2', protocols='OpenFlow13' )
        s3 = self.addSwitch( 's3', protocols='OpenFlow13' )

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        self.addLink(h5, s3)
        self.addLink(h6, s3)
        self.addLink(s1, s2)
        self.addLink(s2, s3)

        #mirror link
        self.addLink(h1, s1)
        self.addLink(h1, s3)

topos = { 'sdntopo': ( lambda: SdnTopo() ) }

# POXDIR = environ[ 'HOME' ] + '/shared/sdn-divesh/controller/'

# class RYU( Controller ):
#     def __init__( self, name, cdir=POXDIR,
#                   command='ryu-manager',
#                   cargs=( 'controller.py '),
#                   **kwargs ):
#         Controller.__init__( self, name, cdir=cdir,
#                              command=command,
#                              cargs=cargs, **kwargs )

# controllers={ 'ryu': RYU }
