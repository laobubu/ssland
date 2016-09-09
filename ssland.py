#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import importlib
import signal
import sys

import config
from core import daemon, util
from service import getService

opts = {
    'daemon'  : 'restart',
    'pid-file': '/var/run/ssland.pid',
    'log-file': '/var/log/ssland.log',
}

def print_help():
    print('''usage: ssland [OPTION]
A multi-in-one proxy provider

Proxy options:
  -d start/stop/restart     daemon mode
''')

def parse_opts():
    import getopt
    shortopts = "hd:s"
    longopts = ['help', 'daemon']
    optlist, _ = getopt.getopt(sys.argv[1:], shortopts, longopts)
    for key, value in optlist:
        if key == '-h' or key == '--help':
            print_help()
            sys.exit(0)
        elif key == '-d' or key == '--daemon':
            opts['daemon'] = value

def init_all_service():
    for (name, config) in config.MODULES.items():
        service = getService(name)
        service.init(config)
        service.start()

def kill_all_service():
    for name in config.MODULES:
        getService(name).stop()

if __name__ == "__main__":
    parse_opts()
    daemon.daemon_exec(opts)
    
    init_all_service()
    signal.signal(getattr(signal, 'SIGQUIT', signal.SIGTERM), kill_all_service)

    # main loop
