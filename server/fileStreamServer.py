#!/usr/bin/python
#-*- coding=utf-8 -*-

##
# @file fileStreamServer.py
# @brief server for local h.264 files 
# @author yy
# @version 0.1
# @date 2012-08-27

import os

from twisted.internet import protocol, reactor
from twisted.protocols import basic
from twisted.python import log

from source import FileSource
from source import SOURCEPATH


class FileServer(object):
    """docstring for FileServer"""
    def __init__(self):
        self._sources = []

        self._suffix = ['.264']


    def findSource(self, sourceName):
        fileNames = [fd for fd in os.listdir(SOURCEPATH) \
                     if os.path.splitext(fd)[-1] in self._suffix ]
        if sourceName in fileNames:
            log.msg("find the file source %s for the rtsp client" %(sourceName))
            fileSource = FileSource(server= self, name = sourceName)
            self.addSource(fileSource)
            return fileSource
     
    def addSource(self, source):
        self._sources.append(source)

    def removeSource(self, source):
        self._sources.remove(source)
