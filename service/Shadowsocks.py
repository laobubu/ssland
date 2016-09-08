#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Shadowsocks service
#

from __future__ import absolute_import

from service.Base import ServiceBase
from core.util import get_stdout

class Shadowsocks(ServiceBase):
    config = {
        "executable": "ssserver",
        "config-file": "/etc/shadowsocks.json",
        "manager-address": "/var/run/shadowsocks-manager.sock",
    }
    executable = ()

    def __init__(self, config):
        self.config = config
        self.executable = tuple(self.config["executable"].split(' ')) + (
            '-c', self.config["config-file"], 
            '--manager-address', self.config['manager-address']
        )

    def start(self):
        get_stdout(self.executable + ('-d', 'start'))
    
    def stop(self):
        get_stdout(self.executable + ('-d', 'stop'))
