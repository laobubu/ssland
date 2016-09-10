#!/usr/bin/python
# -*- coding: utf-8 -*-

def getService(name):
    import importlib
    ServiceModule = importlib.import_module("service." + name)
    return ServiceModule
