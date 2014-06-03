#!/usr/bin/python
#-*- coding=utf-8 -*-

##
# @file CoreServer.py
# @brief contains livestream server , filesource server and rtspServer
# @author yy
# @version .1
# @date 2012-08-16

from twisted.application import service,internet
from twisted.internet import reactor
from twisted.python import log
from liveStreamServer import LiveServer
from fileStreamServer import FileServer
from rtspServer import RTSPServer


class CoreServer(object):
    """manage the live soures in Live Server, the file sources in File Server and the clients in RTSPServer"""
    def __init__(self, liveServer):
        self._liveServerPort = 1557
        self._liveServer = liveServer 
        self._RTSPServerPort = 1556
        self._fileServer = ''

    def initialLiveServer(self):
        port = reactor.listenTCP(self._liveServerPort, self._liveServer) 
        print "live stream server starts at %s" %(port.getHost() )

    def initialFileServer(self):
        self._fileServer = FileServer() 

    def initialRTSPServer(self, server):
        port = reactor.listenTCP(self._RTSPServerPort, server)
        print "rtspServer starts at %s" %(port.getHost() )


  
    def findSource(self, name):
        source = self._liveServer.findSource(name) or self._fileServer.findSource(name)
        if not source:
            log.err("can't find source %s for the rtsp client" %(name))
        else:
            return source


def main():

    liveServer = LiveServer()

    coreServer = CoreServer(liveServer)
    #if you only want file stream server , comment this line
    coreServer.initialLiveServer()
    #if you only want live stream server , comment this line
    coreServer.initialFileServer()

    rtspServer = RTSPServer(coreServer)
    coreServer.initialRTSPServer(rtspServer)

    log.startLogging(open("log.txt",'w'),setStdout = False)
    reactor.run()

if __name__ == '__main__':
    main()
elif __name__=='__builtin__':
    reactor.callLater(1, main)
    application=service.Application('hello')
