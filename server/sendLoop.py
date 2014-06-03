#!/usr/bin/python
#-*- coding=utf-8 -*-

##
# @file sendLoop.py
# @brief send packed frames to rtp clients in a loop
# @author yy
# @version 0.1
# @date 2012-09-09

from twisted.internet import task
from twisted.python import log

class BufferSizeLoop(object):
    """show buffer size regularly, for debug only"""

    def __init__(self, name, frameBuffer):
        self._sourceName = name
        self._frameBuffer = frameBuffer
        self._loop = ''
        self._loopStoped = True

    def startLoop(self):
        self._loop = task.LoopingCall(self.printLoop)
        self._loop.start(1.0)
        self._loopStoped = False
    
    def stopLoop(self):
        if not self._loopStoped:
            self._loop.stop()
            self._loopStoped = True

    def printLoop(self):
        print "%s framebuffer size %d " %(self._sourceName, len(self._frameBuffer))
        
class SendLoop(object):

    def __init__(self):
        self._loop = ''
        #the connected rtp clients which are accepting the frames
        #for file source , each has actually one client
        self._clients = [] 
        self._loopStoped = True

    def getClients(self):
        return self._clients

    def registerObserver(self, observer):
        self._clients.append(observer)

    def removeObserver(self, observer):
        self._clients.remove(observer)

    def notifyObservers(self, frame):
        for client in self._clients:
            client.update(frame)

    def startSendLoop(self, fps):
        self._loop = task.LoopingCall( self.sendLoop )
        self._loop.start(1.0 / fps) 
        self._loopStoped = False

    def stopSendLoop(self):
        if not self._loopStoped:
            self._loop.stop()
            self._loopStoped = True

class LiveSendLoop(SendLoop):

    StartSendThres = 30

    def __init__(self, frameBuffer):
        super(LiveSendLoop, self).__init__()
        self._frameBuffer = frameBuffer
        self._paused = False 

    def isPaused(self):
        return self._paused


    def pauseProducing(self, proto):
        """When we've produce data too fast, pauseProducing will be called"""
        
        self._paused = True
        print 'Pausing pack frames from %s' %(proto.transport.getPeer())

    def resumeProducing(self, proto):
        self._paused = False
        print 'Resume pack frames from %s' %(proto.transport.getPeer())

    def stopProducing(self, proto):
        proto.transport.unregisterProducer()
 

    def cleanupClients(self):
        for client in self._clients:
            client.cleanRTPClient()
        self._clients = []

    def sendLoop(self):
        if not self._clients:
            if len(self._frameBuffer) < self.StartSendThres:
                pass
            else:
                self._frameBuffer.pop(0)
        else:
            if (len(self._frameBuffer) > 0):
                frames = self._frameBuffer.pop(0)
                for frame in frames:
                    self.notifyObservers(frame)

    
class FileSendLoop(SendLoop):
    def __init__(self, fileSource):
        self._clients = [] 
        self._fileSource = fileSource
        self.startSendLoop(self._fileSource.getFps())
    
    def sendLoop(self):
        if not self._clients:
            pass
        else:
            frame = self._fileSource.packFrame(self._fileSource.extractNalu())
            for each in frame:
                self.notifyObservers(each)

    def registerObserver(self, observer):
        super(FileSendLoop, self).registerObserver(observer)

    def removeObserver(self, observer):
        super(FileSendLoop, self).removeObserver(observer)

        assert self._clients == []
        self.stopSendLoop()

   

 


