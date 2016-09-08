#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  service base
#

from abc import ABCMeta, abstractmethod

class ServiceBase(object):
    '''Base Service Class'''
    
    __metaclass__  = ABCMeta
    
    @abstractmethod
    def start(self):
        '''Start the server process'''
    
    @abstractmethod
    def stop(self):
        '''Stop the server process'''
