#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import atexit

import config
from web.wsgi import application as web_application
from service import getService
from shadowsocks import eventloop, daemon

main_loop = None

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
        service.start(accounts[name], event_loop=main_loop)

def kill_all_service():
    for name in config.MODULES:
        getService(name).stop()

class SlowHTTPServer():
    '''SSLand built-in but really slow WSGI server

    Works with shadowsocks.eventloop
    `server` is the WSGIServer instance.
    '''

    def __init__(self, wsgi_app):
        from web.urls import urlpatterns
        from wsgiref.simple_server import make_server
        from django.conf.urls import url
        def static_view(request, path):
            from django.http import HttpResponse
            from django.contrib.staticfiles.finders import find
            import mimetypes
            fp = find(path)
            if fp:
                return HttpResponse(
                    file(fp, 'rb').read(),
                    content_type = mimetypes.guess_type(path, strict=False)[0]
                )
        urlpatterns.append(url(r'^static/(?P<path>[^\?]+)$', static_view))
        self.server = make_server('', 8000, wsgi_app)
    
    def add_to_loop(self, loop):
        loop.add(self.server, eventloop.POLL_IN, self)
    
    def handle_event(self, sock, fd, event):
        if sock == self.server and event == eventloop.POLL_IN:
            self.server.handle_request()

if __name__ == "__main__":

    parse_opts()
    daemon.daemon_exec(opts)

    main_loop = eventloop.EventLoop()
    
    init_all_service()
    atexit.register(kill_all_service)

    # WSGI App
    # this is slow. consider uWSGI or other backend
    server = SlowHTTPServer(wsgi_app=web_application)
    server.add_to_loop(main_loop)
    
    # start the event loop
    main_loop.run()
