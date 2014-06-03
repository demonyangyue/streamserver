#-*- coding=utf-8 -*-
#!/usr/bin/python

##
# @file fileStreamServer_test.py
# @brief  test file for fileStreamServer.py
# @author yy
# @version 0.1
# @date 2012-09-04

import os
from twisted.trial import unittest
from fileStreamServer import FileServer

class FileServerTestCase(unittest.TestCase):
    
    def setUp(self):
        self._server = FileServer()

    def test_findSource(self):
        os.chdir(r"..")
        source = self._server.findSource('stream.264')
        self.assertEqual(source.getName(), "stream.264")
        source._sourceLoop.stopSendLoop()

