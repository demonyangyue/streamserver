#!/usr/bin/python
#-*- coding=utf-8 -*-

##
# @file parser.py
# @brief extract the SDP and from the nalu
# @author y
# @version 0.1
# @date 2012-07-12

import base64

class NaluParser(object):
    """generate SDP """
       
    def generateSDP(self, sps, pps):
        sps_enc = base64.encodestring(sps)[:-1] 
        pps_enc = base64.encodestring(pps)[:-1] 

        m = 'm=video 0 RTP/AVP 96'
        a0 = 'a=control:trackID=1'
        a1 = 'a=rtpmap:96 H264/90000'
        a2 = ('a=fmtp:96 packetization-mode=1;profile-level-id=%s;'
                'sprop-parameter-sets=%s,%s') %(self.genProfileLevelId(sps[1:4]),sps_enc, pps_enc) 

        return '\r\n'.join([m, a0, a1, a2])
    
    def transAscii(self, letter):
        #for instance:'\x66'->'66'
        result =  hex(ord(letter))[2:]
        if len(result) == 1:
            return ''.join(['0', result])
        else:
            return result

    def genProfileLevelId(self, data):
        result = []
        for letter in data:
            result.append(self.transAscii(letter))
        return ''.join(result)

