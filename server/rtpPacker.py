#!/usr/bin/python
#-*- coding=utf-8 -*-

##
# @file rtpPacker.py
# @brief use rtp protocol to packet the nalu
# @author yy
# @version 0.1
# @date 2012-08-16
import random, struct

class RTPPackHelper(object):
    """the information associated with the source which is needed when do RTP packing"""
    def __init__(self, fps = 10):
        self._payloadType = 96
        self._seqNum = 1
        self._timeStamp = 0
        self._timeStampStep = 90000/fps
        self._ssrc = ''.join([str(random.randint(0,9)) for i in range(8)])


    def getPayloadType(self):
        return self._payloadType

    def genPayloadType(self, marked):
        if marked:
            return chr(self._payloadType | 0x80)
        else:
            return chr(self._payloadType)

    def getSeqNum(self):
        return self._seqNum

    def getTimeStamp(self):
        return self._timeStamp

    #for test only
    def setTimeStamp(self, num):
        self._timeStamp = num

    def getSSRC(self):
        return self._ssrc

    #for test only
    def setSeqNum(self, num):
        self._seqNum = num
    
    def transTimeStamp(self):
        """transfer timestamp to 32 bit big-endian string"""
        return struct.pack(">L", self._timeStamp)

    def transSeqNum(self):
        """transfer SeqNum to 16 bit big-endian string"""
        return struct.pack(">H", self._seqNum)

    def num2Ascii(self, num):
        #for instance:'12' -> '\x12'
        hexString = ''.join(['0x', num])
        return chr(int(hexString, base=16))

    def transSSRC(self):
        # for instance:if the ssrc is '12345678' then 
        # the result is '\x12\x34\x56\x78'
        asciiList = [self.num2Ascii(self._ssrc[i:i+2]) for i in range(0,len(self._ssrc), 2)]
        ssrc_new = "".join(asciiList)
        return ssrc_new

    def increaseTimeStamp(self):
        self._timeStamp += self._timeStampStep

    def increaseSeqNum(self):
        self._seqNum += 1

    def genRTPHead(self, marked):
        return ''.join(['\x80', self.genPayloadType(marked), self.transSeqNum(), \
                        self.transTimeStamp(), self.transSSRC()])

class RTPPacker(object):
    """generate rtp packets for the origional nalu"""
    def __init__(self, helper, mtu):
        self._helper = helper
        self._mtu = mtu

    def packNalu(self, nalu):
        pass

class SingleFramePacker(RTPPacker):
    """generate rtp packet for frame shorter than mtu"""
        
    def packNalu(self, nalu):
        RTPPackets = []
        frame = ''.join([self._helper.genRTPHead(marked=True), nalu])
        self._helper.increaseSeqNum()
        self._helper.increaseTimeStamp()
        RTPPackets.append(frame)
        return RTPPackets
        

class SlicedFramePacker(RTPPacker):
    """generate rtp packets for frame longer than mtu"""
        
    def genFuIndicator(self, naluHead):
        fuType = 28
        return chr((ord(naluHead) & 0x60) + fuType)

    def genFuHead(self, naluHead, flag):
        if flag == 'first' :
            return chr( (2 << 6) + (ord(naluHead) & 0x1f))
        elif  flag == 'last' :
            return chr( (1 << 6) + (ord(naluHead) & 0x1f))
        elif  flag == 'middle' :
            return chr( (0 << 6) + (ord(naluHead) & 0x1f))


    def packNalu(self, nalu):
        RTPPackets = []
        naluHead = nalu[0]
        fuIndicator = self.genFuIndicator(naluHead)
        nalus = [nalu[i:i + self._mtu] for i in range(0, len(nalu), self._mtu)]
        for piece_num in range(len(nalus)):
            if piece_num == 0:
                fuHead = self.genFuHead(naluHead, 'first')
                marked = False
                payLoad = nalus[piece_num][1:]
            elif piece_num == len(nalus) - 1:
                fuHead = self.genFuHead(naluHead, 'last')
                marked = True
                payLoad = nalus[piece_num]
            else:
                fuHead = self.genFuHead(naluHead, 'middle')
                marked = False
                payLoad = nalus[piece_num]
            
            packet = ''.join([self._helper.genRTPHead(marked), fuIndicator, fuHead, payLoad])
            RTPPackets.append(packet)
            self._helper.increaseSeqNum()

        self._helper.increaseTimeStamp()

        return RTPPackets



class InterLeavedPacker(object):
    """generate rtp over tcp packets from the origional rtp packet"""

    def __init__(self):
        self._magicNum = '\x24'
        self._channel = '\x00'
        
    def packFrame(self, frame):
        """transfer frame length to 16 bit big-endian string"""
        frameLength = struct.pack( ">H", len(frame))
        return ''.join([self._magicNum, self._channel, frameLength, frame])
