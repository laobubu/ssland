#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import signal
import sys
import os
import json

import config
from core import daemon, util
from web.wsgi import application as web_application
from service import getService

opts = {
    # 'daemon'  : 'restart',
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
    from web.models import ProxyAccount
    accounts = {}  # "service": [account1, account2]
    for ac in ProxyAccount.objects.filter(enabled=True).all():
        name = ac.service
        if not name in accounts: accounts[name] = []
        accounts[name].append(ac.config)

    for (name, service_config) in config.MODULES.items():
        if not name in accounts: accounts[name] = []
        service = getService(name)
        service.init(service_config)
        service.start(accounts[name])

def kill_all_service():
    for name in config.MODULES:
        getService(name).stop()

if __name__ == "__main__":

    parse_opts()
    daemon.daemon_exec(opts)
    
    init_all_service()
    signal.signal(getattr(signal, 'SIGQUIT', signal.SIGTERM), kill_all_service)

    # main loop
    try:
        from wsgiref.simple_server import make_server
        httpd = make_server('', 8000, web_application)
        httpd.serve_forever()
    except:
        kill_all_service()
