#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import atexit

import config
import logging
from web.wsgi import application as web_application
from service import getService
from shadowsocks import eventloop, daemon

main_loop = None

opts = {
    # 'daemon'  : 'restart',
    'pid-file': '/var/run/ssland.pid',
    'log-file': '/var/log/ssland.log',
    'no-http': False,
}

def print_help():
    print('''usage: ssland [OPTION]
A multi-in-one proxy provider

Proxy options:
  -d start/stop/restart     daemon mode
  -n , --no-http            disable built-in http server
''')

def parse_opts():
    import getopt
    shortopts = "hnd:s"
    longopts = ['help', 'no-http', 'daemon']
    optlist, _ = getopt.getopt(sys.argv[1:], shortopts, longopts)
    for key, value in optlist:
        if key == '-h' or key == '--help':
            print_help()
            sys.exit(0)
        elif key == '-n' or key == '--no-http':
            opts['no-http'] = True
        elif key == '-d' or key == '--daemon':
            opts['daemon'] = value

def init_all_service():
    from web.models import ProxyAccount
    accounts = {}  # "service": [account1, account2]
    for ac in ProxyAccount.objects.filter(enabled=True, user__is_active=True).all():
        name = ac.service
        if not name in accounts: accounts[name] = []
        accounts[name].append(ac.config)

    for name, service_config in config.MODULES.iteritems():
        if not name in accounts: accounts[name] = []
        service = getService(name)
        service.init(service_config)
        service.start(accounts[name], event_loop=main_loop)

def kill_all_service():
    for name in config.MODULES:
        getService(name).stop()

if __name__ == "__main__":

    parse_opts()
    daemon.daemon_exec(opts)

    if config.DEBUG:
        logging.basicConfig(level=logging.DEBUG,
            format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    main_loop = eventloop.EventLoop()
    
    init_all_service()
    atexit.register(kill_all_service)

    # WSGI App
    # this is slow. consider uWSGI or other backend
    if not opts['no-http']:
        logging.info('Starting HTTP Server on %d', config.HTTP_PORT)
        from core.httpserver import SlowHTTPServer
        server = SlowHTTPServer(wsgi_app=web_application, port=config.HTTP_PORT)
        server.add_to_loop(main_loop)
    
    # Quota supervisor
    from core.quota_supervisor import QuotaSupervisor
    quota_supervisor = QuotaSupervisor()
    quota_supervisor.add_to_loop(main_loop)

    # start the event loop
    main_loop.run()
