#!/usr/bin/python
#-*- coding=utf-8 -*-
##
# @file rtspServer.py
# @brief Start rtsp session and setup connection with the player
# @author yy
# @version 0.1
# @date 2012-07-05

from twisted.internet import protocol, reactor, defer
from twisted.protocols import basic
from twisted.python import log

from rtspHandler import RTSPRequestHandler

class RTSPState(object):

    def changeState(self, proto, state):
        proto.setState(state)

    def parseRequest(self, proto, lines) :
        """parse the request lines send from the client"""
        try:
            methodName = self.parseMethodName(lines[0])
            result = getattr(self, "handle%s" %(methodName) )(proto, lines)
            if not result:
                proto.transport.loseConnection()
                log.err('parse rtsp request fail, no result returned')
            else:
                proto.sendReply(result)
                if "Not Found" in result[0] or methodName == 'TEARDOWN':
                    proto.transport.loseConnection()
                    log.msg('rtsp connection closed because %s request ' %(methodName))

        except Exception, e:
            proto.transport.loseConnection()
            log.err( "fail to handle rtsp request %s because %s "  %(methodName, str(e)))

    def parseMethodName(self, line):
        #return the first word 
        return line.split()[0]


    def handleOPTIONS(self, proto, lines):
        return proto.getHandler().handleOPTIONS(proto, lines)

    def handleDESCRIBE(self, proto, lines):
        return proto.getHandler().handleDESCRIBE(proto, lines)

     
    def handleSETUP(self, proto, lines):
        log.msg('not implemented')

    def handlePLAY(self, proto, lines):
        log.msg('not implemented')

    def handleTEARDOWN(self, proto, lines):
        log.msg('not implemented')


class RTSPInitState(RTSPState):
    """message received    next state
            SETUP               Ready
            TEARDOWN            Init"""


    def handleSETUP(self, proto, lines):
        self.changeState(proto, RTSPReadyState() )
        return proto.getHandler().handleSETUP(proto, lines)

    def handleTEARDOWN(self, proto, lines):
        pass

class RTSPReadyState(RTSPState):
    """message received    next state
            SETUP               Ready
            TEARDOWN            Init
            PLAY                Playing"""
   
    
    def handleSETUP(self, proto, lines):
        pass

    def handlePLAY(self, proto, lines):
        self.changeState(proto, RTSPPlayingState())
        return proto.getHandler().handlePLAY(proto, lines)

    def handleTEARDOWN(self, proto, lines):
        self.changeState(proto, RTSPInitState() )
        return proto.getHandler().handleTEARDOWN(proto, lines)

class RTSPPlayingState(RTSPState):
    """message received    next state
            SETUP               Playing 
            TEARDOWN            Init
            PLAY                Playing"""

    def handleSETUP(self, proto, lines):
        pass

    def handlePLAY(self, proto, lines):
        pass

    def handleTEARDOWN(self, proto, lines):
        self.changeState(proto, RTSPInitState() )
        return proto.getHandler().handleTEARDOWN(proto, lines)

class RTSPServerProtocol(basic.LineReceiver):
    """receive the data from each client and call service object to process"""

    def __init__(self):
        self._state = RTSPInitState()
        self._dataPool = []
        self._handler = RTSPRequestHandler()

    def getHandler(self):
        return self._handler

    def setState(self, state):
        self._state = state

    def connectionMade(self):
        print "rtsp client connection from %s " %(self.transport.getPeer())
        self.factory.addClient(self)

    def lineReceived(self, line):
        if line:
            self._dataPool.append(line)
        else :
            self._state.parseRequest(self, self._dataPool)
            self._dataPool = []
    
    def sendReply(self, lines):
        """send the reply line to the client"""
        def _sendReply(_):
            for line in lines:
                self.sendLine(line)

        d = defer.succeed("")
        d.addCallback(_sendReply)
        
    def connectionLost(self, reason):
        #TODO the rtsp client removed, but how about the rtp client?
        print "rtsp client connection lost" 
        self.factory.removeClient(self)
        

class RTSPServer(protocol.ServerFactory):
    """create RTSPServerProtocol object for each connection request"""
        
    protocol = RTSPServerProtocol

    def __init__(self, coreServer = ''):
        #to find source from the live server,we need the core server as the bridge
        self._coreServer = coreServer
        self._RTSPClients = [] 

    def addClient(self, cli):
        self._RTSPClients.append(cli)

    def removeClient(self, cli):
        self._RTSPClients.remove(cli)
    
    def findSource(self, name):
        return self._coreServer.findSource(name)

def test():
    port = reactor.listenTCP(1556, RTSPServer())
    print "rtspServer starts at %s" %(port.getHost() )
    reactor.run()

if __name__ == '__main__':
    log.startLogging(open("log.txt",'w'),setStdout = False)
    test()
