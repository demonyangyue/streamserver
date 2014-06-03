#!/usr/bin/python
#-*- coding=utf-8 -*-

##
# @file rpc.py
# @brief the proxy for doing xmlrpc
# @author yy
# @version 1.0
# @date 2012-11-22

import xmlrpclib

class RPCProxy(object):
    def __init__(self):
        self._proxy = xmlrpclib.ServerProxy('http://localhost:8001/xmlrpc/')
    
    def getProxy(self):
        return self._proxy
