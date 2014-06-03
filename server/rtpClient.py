#!/usr/bin/python
#-*- coding=utf-8 -*-

##
# @file rtpClient.py
# @brief rtp client which connect to the rtsp server and request the video frames to play
# @author yy
# @version 0.1
# @date 2012-08-16

from zope.interface import Interface, implements
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from rtpPacker import InterLeavedPacker

from twisted.python import log


class TCPSender(object):
    """send interleaved tcp packets to the vlc palyer"""
    def __init__(self, transport):
        self._transport = transport
        self._packer = InterLeavedPacker()

    def send(self, frame):
        interLeavedFrame = self._packer.packFrame(frame)
        self._transport.write(interLeavedFrame)

    def clean(self):
        pass
        
class RTPClientDatagramProtocol(DatagramProtocol):
    def __init__(self, cliAddr, cliPort):
        self._cliAddr = cliAddr
        self._cliPort = cliPort

    def startProtocol(self):
        try:
            self.transport.connect(self._cliAddr, self._cliPort)
        except Exception, e:
            log.err("rtp connection error because " + str(e))

   
    def connectionRefused(self):
        print "rtp connention refused by the player"

    def datagramReceived(self, datagram, host):
        pass

    def stopProtocol(self):
        #TODO how to stop the protocol
        print "rtp connetion disconnected"

class UDPSender(object):
    """send udp packets to the vlc player"""

    def __init__(self, serverPort, cliAddr, cliPort):
        self._serverPort = serverPort
        self._protocol = RTPClientDatagramProtocol(cliAddr, cliPort)
        reactor.listenUDP(serverPort, self._protocol)

    def send(self, frame):
        self._protocol.transport.write(frame)

    def clean(self):
        print "stop listening for rtp client"
        if self._protocol.transport:
            self._protocol.transport.stopListening()

class IObserver(Interface):
    """observer interface , for the observer pattern"""
        
    def update(frame):
        """
        change the state when the subject notified
        """

class RTPClient(object):
        
    implements(IObserver)

    def __init__(self, source, sender):
        self._sender = sender

        #TODO the source member seems not used
        self._source = source

    def cleanRTPClient(self):
        self._sender.clean()

    def update(self, frame):
        self._sender.send(frame)



