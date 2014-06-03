#!/usr/bin/python
#-*- coding=utf-8 -*-

##
# @file parser_test.py
# @brief test file for parser.py
# @author yy
# @version 0.1
# @date 2012-08-31

from twisted.trial import unittest
from parser import NaluParser

class NaluParserTestCase(unittest.TestCase):

    def setUp(self):
        self._parser = NaluParser()

    def test_transAscii(self):
        self.assertEqual(self._parser.transAscii("\x66"), '66')
        self.assertEqual(self._parser.transAscii("\x0a"), '0a')
        self.assertEqual(self._parser.transAscii("\x00"), '00')
        self.assertEqual(self._parser.transAscii("\xff"), 'ff')

    def test_genProfileLevelId(self):
        self.assertEqual(self._parser.genProfileLevelId('\x42\x00\x0c'), '42000c')
        self.assertEqual(self._parser.genProfileLevelId('\x00\x00\x00'), '000000')
        self.assertEqual(self._parser.genProfileLevelId('\xff\xff\xff'), 'ffffff')
