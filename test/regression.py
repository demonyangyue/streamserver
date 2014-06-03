#!/usr/bin/python
#-*- coding=utf-8 -*-

import os, sys
import unittest


suffix = "test.py"   

def regressionTest():
    ''' Automatically run all the tests in the files named as  "*test" '''
    path = os.path.abspath(os.path.dirname(sys.argv[0]))
    files = [file for file in os.listdir(path) if file.endswith(suffix)]
    module_names = [os.path.splitext(file)[0]for file in files]
    modules = map(__import__, module_names)
    load = unittest.defaultTestLoader.loadTestsFromModule
    return unittest.TestSuite(map(load, modules))

if __name__ == '__main__':
    unittest.main(defaultTest = 'regressionTest')
