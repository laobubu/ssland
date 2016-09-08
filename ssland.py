#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import config
import importlib

services = {}

if __name__ == "__main__":
    for (name, config) in config.MODULES.items():
        ServiceModule = importlib.import_module("service." + name)
        ServiceClass = getattr(ServiceModule, name)
        serviceInstance = ServiceClass(config)
        serviceInstance.start()
        services[name] = serviceInstance
