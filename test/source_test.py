#!/usr/bin/python
#-*- coding=utf-8 -*-

##
# @file source_test.py
# @brief unit test for source.py
# @author yy
# @version 0.1
# @date 2012-07-12

import os

from twisted.trial import unittest
from twisted.test import proto_helpers

from liveStreamServer import LiveServer
from source import LiveSource, NoSDPState, SDPState, FileSource



class LiveSourceTestCase(unittest.TestCase):

    def setUp(self):
        factory = LiveServer()
        self.protocol = factory.buildProtocol(('127.0.0.1', 1557))
        self.transport = proto_helpers.StringTransportWithDisconnection()
        self.transport.protocol = self.protocol
        self.protocol.makeConnection(self.transport)
        self._shortNalu = '\x61\xea\x31'
        self._longNalu = ''.join(['\x61', '\x2f'*4000])
    
    def test_parseNalu(self):
        #send sps
        self.protocol._source.parseNalu('\x67\x42\x00\x0c\xe9\x02\x83\xf2')
        #send pps
        self.protocol._source.parseNalu('\x68\xce\x01\x0f\x20')
        
        self.assertNotEqual(self.protocol._source.getSDP(), '')
        self.assertTrue(isinstance(self.protocol._source.getState(), SDPState) )

    def test_sendLoop(self):
        #TODO we need a time period, how to test?
        pass


    def test_packFrames(self):
        for i in range(self.protocol._source.getStartSendThres()):
            self.protocol._source.packFrame(self._shortNalu)
        self.assertEqual(len(self.protocol._source._frameBuffer), \
                        self.protocol._source.getStartSendThres() + self.protocol._source.NotEnoughFramesThres/2)

        for i in range(self.protocol._source.PausePackThres):
            self.protocol._source.packFrame(self._longNalu)
        self.assertEqual(self.protocol._source.isPaused(), True) 

    def tearDown(self):
        self.protocol.transport.loseConnection()


class FileSourceTestCase(unittest.TestCase):

    def setUp(self):
        self._fileSource = FileSource(name = r'stream.264')

    def test_openFile(self):
        self.assertTrue(self._fileSource._fp.name.endswith('stream.264'))

        
    def test_extractNalu(self):
        nalu = self._fileSource.extractNalu()
        self.assertEqual(nalu, '')

        length = 0
        nalu = self._fileSource.extractNalu()
        length += len(nalu) 
        self.assertEqual(nalu, '\x67\x42\x00\x0c\xe9\x02\x83\xf2')

        nalu = self._fileSource.extractNalu()
        length += len(nalu) 
        self.assertEqual(nalu, '\x68\xce\x01\x0f\x20')
        
        self.assertEqual(len(self._fileSource._dataBuffer), self._fileSource._chunckSize-length-12)

    def test_genSDP(self):
        self._fileSource.genSDP()
        self.assertTrue("trackID" in self._fileSource.getSDP())
        self.assertTrue(isinstance(self._fileSource.getState(), SDPState))

    def tearDown(self):
        self._fileSource._sourceLoop.stopSendLoop()
