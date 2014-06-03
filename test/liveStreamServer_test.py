#!/usr/bin/python
#-*- coding=utf-8 -*-
##
# @file liveStreamServer_test.py
# @brief unit test for liveStreamServer.py
# @author yy
# @version 0.1
# @date 2012-07-10

from twisted.trial import unittest
from twisted.test import proto_helpers

from liveStreamServer import LiveServer

class LiveServerTestCase(unittest.TestCase):

    def test_connection(self):

        self.factory = LiveServer()
        #build a connection here
        self.transport = proto_helpers.StringTransportWithDisconnection()
        self.protocol = self.factory.buildProtocol(('127.0.0.1', 1557))
        self.transport.protocol = self.protocol
        self.protocol.makeConnection(self.transport)
        self.assertEqual(self.factory.getClientNum(), 1)

        #build another connection here
        self.transport_1 = proto_helpers.StringTransportWithDisconnection()
        self.protocol_1 = self.factory.buildProtocol(('127.0.0.1', 1557))
        self.transport_1.protocol = self.protocol_1
        self.protocol_1.makeConnection(self.transport_1)
        self.assertEqual(self.factory.getClientNum(), 2)

        #tear down the first connection
        self.protocol.transport.loseConnection()
        self.assertEqual(self.factory.getClientNum(), 1)

        #tear down the second connection
        self.protocol_1.transport.loseConnection()
        self.assertEqual(self.factory.getClientNum(), 0)

class LiveProtocolTestCase(unittest.TestCase):
    """unit test for LiveProtocol"""
    
    def setUp(self):
        self.factory = LiveServer()
        self.transport = proto_helpers.StringTransportWithDisconnection()
        self.protocol = self.factory.buildProtocol(('127.0.0.1', 1557))
        self.transport.protocol = self.protocol
        self.protocol.makeConnection(self.transport)

        self.data = ('\x00\x00\x00\x01\x67\x42\x00\x0c\xe9\x02\x83\xf2\x00\x00\x00\x01'
                    '\x68\xce\x01\x0f\x20\x00\x00\x00\x01\x65\xb8\x40\x57\xbb\xef\x00'
                    '\x1b\xfc\x48\x00\x08\xc0\x73\x8c\x09\xec\x8b\xe4\x6b\x21\x3c\x96'
                    '\x1a\x3f\xc0\x63\xe5\x0d\x38\x44\x7d\x89\xec\xde\x77\x76\x34\x0b'
                    '\x98\xd0\x75\xcf\xc1\x40\x0c\x70\x00\x10\x04\xf9\x8c\x68\x28\x06'
                    '\xb7\x1c\x5c\x19\xf0\xfd\xca\x9b\x0b\xc2\x50\x00\x85\xf0\x96\x36'
                    '\xfe\x17\x86\x98\xe3\xc7\x66\xec\x50\xbd\x4b\x4b\x17\x29\x39\xa8'
                    '\x18\x01\x68\x30\x00\x10\x0e\x31\x0a\x24\x88\x54\x8e\x44\x38\x19'
                    '\x34\x67\x2a\x19\x19\xdf\x81\xe1\xe4\xa2\x8f\x0c\x1e\x6c\x4b\x59'
                    '\x0d\x18\x00\x04\x00\x00\x7f\xe1\x84\x10\x0f\x82\x3a\xf6\xc5\x40'
                    '\x7f\xe6\x2a\x2d\x30\xb8\xbe\x75\x29\x69\x98\xe6\x31\x6e\x70\x1b'
                    '\x93\x34\x1e\x44\x69\xf4\x01\xa0\x90\x90\x12\x09\xe8\x48\xf3\xae'
                    '\xf7\x1b\xd2\x0e\x84\x0d\x65\x1b\x00\x00\x00\x01')

        
    def test_sourceName(self):
        self.assertEqual(self.protocol.getSource().getName(), 'stream_1')

    def test_lineReveived(self):
        self.protocol.dataReceived(self.data)
        self.assertNotEqual(self.protocol.getSource().getSDP(), '')


    def tearDown(self):
        self.protocol.transport.loseConnection()
       

