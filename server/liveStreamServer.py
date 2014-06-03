#!/usr/bin/python
#-*- coding=utf-8 -*-
##
# @file liveStreamServer.py
# @brief accpept live stream
# @author yy
# @version 0.1
# @date 2012-07-10

from twisted.internet import protocol, reactor
from twisted.protocols import basic
from twisted.protocols.policies import TimeoutMixin


from twisted.python import log
from source import LiveSource

class LiveProtocol(basic.LineReceiver, TimeoutMixin):
    """accept live stream data and parse it"""
    delimiter = '\x00\x00\x00\x01'
    #TODO the default MAX_LENGTH is 16384, enough?
    MAX_LENGTH = 65530

    def __init__(self):
        self._source = ''
        #the index in the channel
        self._index = -1

    def getSource(self):
        return self._source
        
    def connectionMade(self):
        self.setTimeout(10)
        sourceName = self.genSourceName()
        print 'live stream %s connected from %s' % (sourceName, self.transport.getPeer())
        self._source = LiveSource(self, sourceName)
        self.factory.addSource(self._source)
        self.transport.registerProducer(self._source, True)

    def genSourceName(self):
        #return 'stream_%d'%(self.factory.getClientNum())
        channels = self.factory.getChannels()
        self._index = channels.index('off')
        channels[self._index] = 'on'
        #if channel num is 0 ,then the souce name is stream_1
        return 'stream_%d' %(self._index + 1)

    def lineReceived(self, line):
        #in case of "00 00 00 01 00 00 00 01"
        self.resetTimeout()
        if line:
            self._source.parseNalu(line)
        else:
            log.msg("receive an empty nalu")

    def timeoutConnection(self):
        log.err('client timeout')
        self.transport.loseConnection()

    def connectionLost(self, reason):
        self.setTimeout(None)
        print 'live stream connection lost from %s' % self.transport.getPeer()
        self.factory.getChannels()[self._index] = 'off'
        self._source.stopSendLoop()
        self._source.stopProducing()
        self.factory.removeSource(self._source)
        self.factory.connectionLost(reason)

    def lineLengthExceeded(self, line): 
        print "too long frame received"

class LiveServer(protocol.ServerFactory):
    """listen for live stream connection"""

    protocol = LiveProtocol
    
    def __init__(self):
        self._clientNum = 0
        self._sources = []
        #for source name only, 'on' stands for the given channel has source connected, 'off' otherwise.
        self._channels = ['off' for i in range(1000)]

    def getClientNum(self):
        return self._clientNum

    def getChannels(self):
        return self._channels

    def buildProtocol(self, addr):
        self._clientNum = self._clientNum + 1
        return protocol.ServerFactory.buildProtocol(self, addr)

    def addSource(self, source):
        self._sources.append(source)

    def removeSource(self, source):
        source.cleanupClients()
        self._sources.remove(source)

    def findSource(self, name):
        """find the live source by name"""
        for source in self._sources:
            if name == source.getName():
                log.msg('find the live source %s for the rtsp client' %(name))
                return source

    def connectionLost(self, reason):
        self._clientNum = self._clientNum - 1
        log.msg("live source connection lost because %s" %(reason))

def test():
    port = reactor.listenTCP(1557, LiveServer())
    print "live stream server starts at %s" %(port.getHost() )
    reactor.run()

if __name__ == '__main__':
    log.startLogging(open("log.txt",'w'),setStdout = False)
    test()
