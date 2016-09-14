#!/usr/bin/python
# -*- coding: utf-8 -*-

def getQuotaModule(name):
    import importlib
    Module = importlib.import_module("quota." + name)
    return Module
