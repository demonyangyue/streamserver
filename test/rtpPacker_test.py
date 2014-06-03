#!/usr/bin/python
#-*- coding=utf-8 -*-

##
# @file rtpPacker_test.py
# @brief unit test for rtpPacker.py
# @author yy
# @version 0.1
# @date 2012-08-20

import struct
from twisted.trial import unittest

from rtpPacker import RTPPackHelper, SingleFramePacker, SlicedFramePacker

class RTPPackerHelperTestCase(unittest.TestCase):
        
    def setUp(self):
        self._packHelper = RTPPackHelper()

    def test_transTimeStamp(self):
        self._packHelper.setTimeStamp(0)
        self.assertEqual( self._packHelper.transTimeStamp(), '\x00\x00\x00\x00')


        self._packHelper.setTimeStamp(9000)
        self.assertEqual( self._packHelper.transTimeStamp(), '\x00\x00#(')

        self._packHelper.setTimeStamp(90000)
        self.assertEqual( self._packHelper.transTimeStamp(), '\x00\x01_\x90')

        self.assertEqual( struct.unpack('>L',self._packHelper.transTimeStamp())[0], 90000)

    def test_transSeqNum(self):
        self._packHelper.setSeqNum(1)
        self.assertEqual( self._packHelper.transSeqNum(), '\x00\x01')

        self._packHelper.setSeqNum(99)
        self.assertEqual( self._packHelper.transSeqNum(), '\x00\x63')

        self._packHelper.setSeqNum(65535)
        self.assertEqual( self._packHelper.transSeqNum(), '\xff\xff')

    def test_num2Ascii(self):
        self.assertEqual(self._packHelper.num2Ascii('00'), '\x00')
        self.assertEqual(self._packHelper.num2Ascii('0f'), '\x0f')
        self.assertEqual(self._packHelper.num2Ascii('12'), '\x12')
        self.assertEqual(self._packHelper.num2Ascii('cd'), '\xcd')
        self.assertEqual(self._packHelper.num2Ascii('ff'), '\xff')

    def test_genPayloadType(self):
        self.assertEqual( self._packHelper.genPayloadType(True), '\xe0')
        self.assertEqual( self._packHelper.genPayloadType(False), '\x60')

class SingleFramePackerTestCase(unittest.TestCase):
        
    def setUp(self):
        self._helper = RTPPackHelper()
        self._mtu = 1200
        self._singleFramePacker = SingleFramePacker(self._helper, self._mtu)

    def test_packNalu(self):
        nalu = '\x61\xea\x31'
        packets = []
        packets.append(''.join(['\x80','\xe0', self._helper.transSeqNum(), \
                          self._helper.transTimeStamp(), self._helper.transSSRC(), nalu]))
        self.assertEqual( packets, self._singleFramePacker.packNalu(nalu) )

        self.assertEqual( self._helper.getSeqNum(), 2)
        self.assertEqual( self._helper.getTimeStamp(), 9000)

class SlicedFramePackerTestCase(unittest.TestCase):
        
    def setUp(self):
        self._helper = RTPPackHelper()
        self._mtu = 1200
        self._slicedFramePacker = SlicedFramePacker(self._helper, self._mtu)

    def test_genFuIndicator(self):
        self.assertEqual(self._slicedFramePacker.genFuIndicator('\x61'), '\x7c')
    
    def test_genFuHead(self):
        self.assertEqual(self._slicedFramePacker.genFuHead('\x61', 'first'), '\x81')
        self.assertEqual(self._slicedFramePacker.genFuHead('\x61', 'last'), '\x41')

    def test_packNalu(self):
        nalu = ''.join(['\x61', '\x2f'*4000])
        RTPPackets = []
        RTPPackets.append(''.join(['\x80',self._helper.genPayloadType(False),\
                          self._helper.transSeqNum(), self._helper.transTimeStamp(),\
                          self._helper.transSSRC(),'\x7c','\x81',nalu[1:self._mtu]]))
        self._helper.increaseSeqNum()

        RTPPackets.append(''.join(['\x80',self._helper.genPayloadType(False),\
                          self._helper.transSeqNum(), self._helper.transTimeStamp(),\
                          self._helper.transSSRC(),'\x7c','\x01',nalu[self._mtu:2*self._mtu]]))

        self._helper.increaseSeqNum()

        RTPPackets.append(''.join(['\x80',self._helper.genPayloadType(False),\
                          self._helper.transSeqNum(), self._helper.transTimeStamp(),\
                          self._helper.transSSRC(),'\x7c','\x01',nalu[2*self._mtu:3*self._mtu]]))

        self._helper.increaseSeqNum()

        RTPPackets.append(''.join(['\x80',self._helper.genPayloadType(True),\
                          self._helper.transSeqNum(), self._helper.transTimeStamp(),\
                          self._helper.transSSRC(),'\x7c','\x41',nalu[3*self._mtu:]]))

        self._helper.setSeqNum(1)
        self.assertEqual(RTPPackets, self._slicedFramePacker.packNalu(nalu))


