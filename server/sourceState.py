#!/usr/bin/python
#-*- coding=utf-8 -*-

##
# @file sourceState.py
# @brief classify the source  state by whether it has SDP
# @author yy
# @version 0.1
# @date 2012-09-09

from parser import NaluParser

class NoSDPState(object):
    """source hasn't generate SDP yet"""
    def __init__(self):
        self._SPS = ''
        self._PPS = ''
        self._parser = NaluParser()

    def parseNalu(self, source, line):
        if not line:
            return

        naluType = ord(line[0]) & 0x1f
        
        if naluType == 7:
            if self._SPS == '':
                self._SPS = line
        elif naluType == 8:
            if self._PPS == '':
                self._PPS = line
        elif naluType == 6:
            print 'get SEI nalu '
        else:
            print 'no SDP, ignore the frame data'

        if self._SPS and self._PPS:
            source.setSDP(self._parser.generateSDP(self._SPS, self._PPS))

class SDPState(object):
    """ source has already got the SDP, so extract frame from the nalu """
    

    def parseNalu(self, source, line):
        naluType = ord(line[0]) & 0x1f
        if naluType == 1 or naluType == 5:
            # add a list of packed frames to the frameBuffer
            source.packFrame(line)
            #print "received frame of type %d" %(naluType)
        else:
            print "unsupported frame of type %d" %(naluType)



