#!/usr/bin/python
#-*- coding=utf-8 -*-
##
# @file rtspServer_test.py
# @brief unit test for rtspServer.py
# @author yy
# @version 0.1
# @date 2012-07-05

import datetime

from twisted.trial import unittest
from twisted.test import proto_helpers

from liveStreamServer import LiveServer
from source import LiveSource
from rtspServer import RTSPServer
from rtspHandler import RTSPRequestHandler
from rtpClient import TCPSender, UDPSender



class TestSource(LiveSource):
    """source for test """
    def __init__(self):
        super(TestSource, self).__init__(name = 'stream.264')
        self._SDP = '\r\n'.join(["m=video 0 RTP/AVP 96",
                         "a=control:trackID=0",
                         "a=rtpmap:96 H264/90000",
                         "a=fmtp:96 packetization-mode=1;profile-level-id=6742c0;sprop-parameter-sets=Z0LgHtoCgLRA,aM4wpIA="])
        
class ClassName(object):
    """docstring for ClassName"""
    def __init__(self, arg):
        super(ClassName, self).__init__()
        self.arg = arg
        
    def getSDP(self):
        return self._SDP

    def getName(self):
        return self._name

class RTSPServerTestCase(unittest.TestCase):

    def setUp(self):
        liveServer = LiveServer()
        liveServer.addSource(TestSource())
        
        factory = RTSPServer(liveServer)
        self.protocol = factory.buildProtocol(('127.0.0.1', 1556))
        self.transport = proto_helpers.StringTransportWithDisconnection()
        self.transport.protocol = self.protocol
        self.protocol.makeConnection(self.transport)

    def test_OPTIONS(self):
        self.protocol.dataReceived("OPTIONS rtsp://127.0.0.1:1556/stream.264 RTSP/1.0\r\n"
                                    "CSeq: 1\r\n"
                                    "User-Agent: LibVLC/1.1.4 (LIVE555 Streaming Media v2010.04.09\r\n\r\n")
        self.assertEqual(self.transport.value(), "RTSP/1.0 200 OK\r\n"
                        "Server: python rtsp; Platform/Linux; Release/GM; state/beta;%s\r\n"
                        "CSeq: 1\r\n"
                        "Public: DESCRIBE, SETUP, TEARDOWN, PLAY, OPTIONS\r\n\r\n"\
                        %(datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')))

    def test_DESCRIBE_success(self):
        lines = ["DESCRIBE rtsp://127.0.0.1:1556/stream.264 RTSP/1.0",
                 "CSeq: 2",
                 "Accept: application/sdp",
                 "User-Agent: LibVLC/1.1.4 (LIVE555 Streaming Media v2010.04.09)"]
        result = self.protocol._handler.handleDESCRIBE(self.protocol, lines)
        self.assertTrue('Content-Length: 260' in result)

    def test_DESCRIBE_fail(self):
        lines = ["DESCRIBE rtsp://127.0.0.1:1556/notExist.264 RTSP/1.0",
                 "CSeq: 2",
                 "Accept: application/sdp",
                 "User-Agent: LibVLC/1.1.4 (LIVE555 Streaming Media v2010.04.09)"]
        result = self.protocol._handler.handleDESCRIBE(self.protocol, lines)
        self.assertTrue('RTSP/1.0 404 Not Found' in result)

    def test_tcpSETUP(self):
        self.protocol._handler._setSource(TestSource())
        lines = ["SETUP rtsp://127.0.0.1:1556/stream.264/trackID=0 RTSP/1.0",
                 "CSeq: 3",
                 "Transport: RTP/AVP/TCP;unicast;interleaved=0-1",
                 "User-Agent: LibVLC/1.1.4 (LIVE555 Streaming Media v2010.04.09)"]
        result = self.protocol._handler.handleSETUP(self.protocol, lines)
        self.assertTrue("OK" in result[0])
        self.assertTrue(isinstance(self.protocol._handler._client._sender, TCPSender))

    def test_udpSETUP(self):
        self.protocol._handler._setSource(TestSource())
        lines = ["SETUP rtsp://127.0.0.1:1556/stream.264/trackID=0 RTSP/1.0",
                 "CSeq: 3",
                 "Transport: RTP/AVP;unicast;client_port=51164-51165",
                 "User-Agent: LibVLC/1.1.4 (LIVE555 Streaming Media v2010.04.09)"]
        result = self.protocol._handler.handleSETUP(self.protocol, lines)
        self.assertTrue("OK" in result[0])
        self.assertTrue(isinstance(self.protocol._handler._client._sender, UDPSender))
        self.protocol._handler.cleanRTPClient()

    def test_PLAY(self):
        pass

    def test_TEARDOWN(self):
        pass    

    def tearDown(self):
        self.protocol.transport.loseConnection()

