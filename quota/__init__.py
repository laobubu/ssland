#!/usr/bin/python
# -*- coding: utf-8 -*-

def getQuotaModule(name):
    import importlib
    Module = importlib.import_module("quota." + name)
    return Module

def getQuotaTypes():
    ''' return all types of Quota and their names.

    getQuotaTypes() -> (('Name', 'Friendly Name'), (...) ...)
    '''
    import pkgutil, os
    import importlib
    p = os.path.dirname(__file__)
    retval = []

    for importer, name, ispkg in pkgutil.iter_modules([p]):
        Module = importlib.import_module("quota." + name)
        retval.append( (name, Module.FRIENDLY_NAME) )
    
    return retval
