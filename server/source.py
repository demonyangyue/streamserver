#!/usr/bin/python
#-*- coding=utf-8 -*-

##
# @file source.py
# @brief LiveSource and FileSource
# @author yy
# @version 0.1
# @date 2012-07-11

import os , subprocess

from zope.interface import implements
from twisted.internet import interfaces, reactor
from zope.interface import Interface
from twisted.python import log

from rtpPacker import SingleFramePacker, SlicedFramePacker, RTPPackHelper
from sourceState import NoSDPState, SDPState
from sendLoop import LiveSendLoop, FileSendLoop, BufferSizeLoop

#SOURCEPATH = r'/home/wwwfox/programme/streamserver/media/'
#SOURCEPATH = os.path.abspath('../media/')
SOURCEPATH = os.path.join(os.path.dirname(os.path.dirname(__file__)) , "media")


class ISubject(Interface):
    """subject interface , for the observer pattern"""
        
    def registerObserver(observer):
        """
        register observer in the subject
        """

    def removeObserver(observer):
        """
        remove observer from subject
        """

    def notifyObservers():
        """
        when state changed, notify the registed observers
        """
        
class Source(object):
    """super class for live source and file source"""
    def __init__(self, name):
        self._name = name

        self._state = NoSDPState()

        self._fps = self.getFps()
        self._rtpPackHelper = RTPPackHelper(self._fps)

        self._mtu = 1200
        self._singleFramePacker = SingleFramePacker(self._rtpPackHelper, self._mtu)
        self._slicedFramePacker = SlicedFramePacker(self._rtpPackHelper, self._mtu)

        self._sourceLoop = ''

    def getName(self):
        return self._name

    def getState(self):
        return self._state

    def setState(self, state):
        self._state = state
    
    def getFps(self):
        pass

    def getSSRC(self):
        return self._rtpPackHelper.getSSRC()

    def getClients(self):
        return self._sourceLoop.getClients()

    def registerObserver(self, observer):
        self._sourceLoop.registerObserver(observer)

    def removeObserver(self, observer):
        self._sourceLoop.removeObserver(observer)

    def notifyObservers(self, frame):
        self._sourceLoop.notifyObservers(frame)

    def packFrame(self, line):
        if len(line) < self._mtu:
            frame = self._singleFramePacker.packNalu(line)
        else:
            frame = self._slicedFramePacker.packNalu(line)
        return frame

    
class LiveSource(Source):
    """generate live stream source"""

    implements(interfaces.IPushProducer, ISubject)

    PausePackThres = 60
    ResumePackThres = 30
    NotEnoughFramesThres = 20

    def __init__(self, proto = '' , name = ''):
        super(LiveSource, self).__init__(name)
        self._proto = proto
        self._SDP = ''
        self._frameBuffer = []
        self._sourceLoop = LiveSendLoop(self._frameBuffer)
        #for debug only
        self._printLoop = BufferSizeLoop(self._name, self._frameBuffer)

    def getSDP(self):
        return self._SDP

    def setSDP(self, sdp):
        self._SDP = sdp
        self.setState(SDPState())
        self.startSendLoop()

    def getFps(self):
        """"return frame rate, default is 10"""
        #TODO automatically generate the frame rate
        return 10
    
    def getStartSendThres(self):
        return self._sourceLoop.StartSendThres
    

    def startSendLoop(self):
        self._sourceLoop.startSendLoop(self._fps)
        self._printLoop.startLoop()
        #reactor.callLater(2, self.playSource)

    #def playSource(self):
    #    reactor.callInThread(self.playInVlc)


    def playInVlc(self):
        url = "".join(["rtsp://127.0.0.1:1556/",self._name])
        subprocess.call(["vlc", url])

    def stopSendLoop(self):
        try:
            self._printLoop.stopLoop()
            self._sourceLoop.stopSendLoop()
        except Exception, e:
            pass

    def isPaused(self):
        return self._sourceLoop.isPaused()

    def pauseProducing(self):
        self._sourceLoop.pauseProducing(self._proto) 

    def resumeProducing(self):
        self._sourceLoop.resumeProducing(self._proto)

    def stopProducing(self):
        self._sourceLoop.stopProducing(self._proto)
 

    def cleanupClients(self):
        self._sourceLoop.cleanupClients()
    
    def parseNalu(self, line):
        self._state.parseNalu(self, line)

    def packFrame(self, line):
        if not self.isPaused():
            frame = super(LiveSource, self).packFrame(line)
            self._frameBuffer.append(frame)

            if len(self._frameBuffer) > self.PausePackThres:
                self.pauseProducing()
                log.msg('pack frame paused')
            
            #because of the Fluctuations in the sender , 
            #we need to interpolation when there is no enough frames
            elif len(self._frameBuffer) < self.NotEnoughFramesThres:

                frame = super(LiveSource, self).packFrame(line)
                self._frameBuffer.append(frame)
                print 'not enough frames, we insert one frame'

        else:
            #too many frames in the buffer, we pause pack frame
            #until the buffer size is less than ResumePackThres
            if len(self._frameBuffer) < self.ResumePackThres:
                self.resumeProducing()
                log.msg('pack frame resumed')
            

class FileSource(Source):
    """generate file stream source"""

    implements(ISubject)
        
    def __init__(self, server = '', name = ''):
        super(FileSource, self).__init__(name)
        self._server = server
        self._SDP = ''
        self._dataBuffer = ''
       
        self._delimiter = '\x00\x00\x00\x01'
        self._chunckSize = 4096

        self._fp = self.openFile()

        self._sourceLoop = FileSendLoop(self)

    def getSDP(self):
        if not self._SDP:
            self.genSDP()
        return self._SDP

    def setSDP(self, sdp):
        self._SDP = sdp
        self.setState(SDPState())

    def setState(self, state):
        self._state = state
    
    def getState(self):
        return self._state

    def getFps(self):
        """"return frame rate, default is 25"""
        #TODO automatically generate the frame rate
        return 25

    def openFile(self):
        fullName = os.path.join(SOURCEPATH, self._name)
        fp = open(fullName, 'rb')
        return fp
    
    def _fillDataBuffer(self):
        #when the data buffer has less than one frame data, fill it
        while True:
            data = self._fp.read(self._chunckSize)
            if not data:
                self._fp.close()
                self.stopSendLoop()
                break
            self._dataBuffer += data
            if self._delimiter in data:
                break

    def lessThanOneFrame(self):
        return self._delimiter not in self._dataBuffer

    def extractNalu(self):
        #extract the Nalu from the 264 file
        if self.lessThanOneFrame():
            self._fillDataBuffer()
        dataSplited = self._dataBuffer.split( self._delimiter,  1)
        if len(dataSplited) == 1:
            #the last piece of nalu
            self._dataBuffer = ''
        else:
            self._dataBuffer = dataSplited[1]
        return dataSplited[0]
        
    def genSDP(self):
        for i in range(3):
            self._state.parseNalu(self, self.extractNalu())

    def removeObserver(self, observer):
        super(FileSource, self).removeObserver(observer)
        self._server.removeSource(self)

    def stopSendLoop(self):
        self._sourceLoop.stopSendLoop()
