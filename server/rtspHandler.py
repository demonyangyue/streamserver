#!/usr/bin/python
#-*- coding=utf-8 -*-

##
# @file rtspHandler.py
# @brief the details of handle rtsp request
# @author yy
# @version 0.1
# @date 2012-07-07


import random, datetime, re
from twisted.python import log
from rtpClient import TCPSender, UDPSender, RTPClient

#for rtp and rtcp port
ServerPortPool = [(x, x+1) for x in range(6000, 7000, 2)]


class RTSPRequestHandler(object):
    """handle  rtsp request for each rtsp protocol"""

    replyOK = "RTSP/1.0 200 OK"
    replyNotFound = "RTSP/1.0 404 Not Found"
                    

    def __init__(self):
        self._sessionNum = ''.join(str(random.randint(0,9)) for i in range(16)) 
        self._source = ''
        self._client = ''
        self._serverInfo = ''.join(["Server: python rtsp; Platform/Linux; Release/GM; state/beta;", \
                          datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')])
        self._SDP = ["v=0", "o=-1 1 IN IP4 127.0.0.1",
                "s=VStream Live", "t=0 0",
                "i=ICL Streaming Media",
                "c=IN IP4 0.0.0.0",]
    
    #for test only
    def _setSource(self, source):
        self._source = source

    def parseCSeq(self, line):
        if 'CSeq' in line:
            return line 
        else:
            return ''

    def replySuccessHead(self, seqLine):
        result = []
        result.append(self.replyOK)
        result.append(self._serverInfo)
        CSeq = self.parseCSeq(seqLine)
        result.append(CSeq)
        return result

    def replyFailHead(self, seqLine):
        result = []
        result.append(self.replyNotFound)
        result.append(self._serverInfo)
        CSeq = self.parseCSeq(seqLine)
        result.append(CSeq)
        return result
       
    def handleOPTIONS(self, proto, lines):
        result = self.replySuccessHead(lines[1])
        public = "Public: DESCRIBE, SETUP, TEARDOWN, PLAY, OPTIONS" 
        result.append(public)
        result.append('')
        return result

    def handleDESCRIBE(self, proto, lines):
        def _getUrl(line):
            return line.split(' ')[1]
        def _getSourceName(line):
            return (line.split(' ')[1]).split('/')[-1]
        url = _getUrl(lines[0])
        content_type = 'Content-Type: application/sdp'
        content_base = ''.join(['Content-Base: ', url, '/'])

        sourceName = _getSourceName(lines[0])
        self._source = self.findSource(proto, sourceName)
        if not self._source:
            log.err('the requested source %s does not exist ' %(sourceName))
            result = self.replyFailHead(lines[1])
            result.append('Connectionlose')
            result.append("")

        else:
            self._SDP.append(self._source.getSDP())
            content_length = ''.join( ['Content-Length: ', str(len('\r\n'.join(self._SDP) + '\r\n')) ])
            result = self.replySuccessHead(lines[1])
            result.append(content_type)
            result.append(content_base)
            result.append(content_length)
            result.append("")
            result.extend(self._SDP)

        return result

    def parseTransline(self, transLine, proto, serverPort):
        if 'interleaved' in transLine:
            sender = TCPSender(proto.transport) 
        else:
            cliAddr = proto.transport.getPeer().host
            cliPort = re.compile('(\d+)-(\d+)').search(transLine).group(1)
            sender = UDPSender(serverPort, cliAddr, int(cliPort))
            
        #initial the rtp client here  
        self._client = RTPClient(self._source, sender)

    def handleSETUP(self, proto, lines):
        transLine = ''
        for line in lines:
            if 'Transport' in line:
                transLine = line
        if not transLine:
            log.err('no tranport line found in setup method')
            return []
  
        result = self.replySuccessHead(lines[1])
        result.append(''.join(['Session: ', self._sessionNum]))

        serverPort = ServerPortPool.pop()[0]
        self.parseTransline(transLine, proto, serverPort)

        if 'interleaved' in transLine:
            result.append(''.join([transLine, ';ssrc=', self._source.getSSRC()]))
        else:
            result.append("".join([transLine, ';server_port=', str(serverPort),\
                          '-', str(serverPort+1), ';ssrc=', self._source.getSSRC()]))
        result.append('')
        return result

    def handlePLAY(self, proto, lines):
        result = self.replySuccessHead(lines[1])
        result.append(''.join(['Session: ', self._sessionNum]))
        result.append(''.join(["Range: npt=0.0000-"]))
        result.append('')

        #register the source in the client 
        self._source.registerObserver(self._client)
        return result


    def handleTEARDOWN(self, proto, lines):
        result = self.replySuccessHead(lines[1])
        result.append(''.join(['Session: ', self._sessionNum]))
        result.append("Connection: Close")
        result.append('')
        
        self.cleanRTPClient()

        return result

    def findSource(self, proto, name):
        return proto.factory.findSource(name)

    def cleanRTPClient(self):
        if self._source and self._client:
            self._client.cleanRTPClient()
            if self._client in self._source.getClients():
                print "remove rtp client form the source"
                self._source.removeObserver(self._client)
        else:
            print "no rtp client to remove"
        
