from __future__ import absolute_import, print_function

import socket
import json
import logging
import os

from shadowsocks import eventloop, common

# Shadowsocks Control socket
class ShadowsocksCtx(socket.socket):
    local_sock_file = None
    addr_remote = None
    addr_local = None

    def __init__(self, manager_address):
        try:
            # manager_address = config['manager-address']
            if ':' in manager_address:
                addr = manager_address.rsplit(':', 1)
                addr = addr[0], int(addr[1])
                addr_local = ('', 0)
                addrs = socket.getaddrinfo(addr[0], addr[1])
                if addrs:
                    family = addrs[0][0]
                else:
                    logging.error('invalid address: %s', manager_address)
                    exit(1)
            else:
                import uuid
                self.local_sock_file = '/var/run/ssland-%s.sock'%uuid.uuid4()
                addr = manager_address
                addr_local = self.local_sock_file
                family = socket.AF_UNIX
            
            self.addr_local = addr_local
            self.addr_remote = addr

            socket.socket.__init__(self, family, socket.SOCK_DGRAM)
        except (OSError, IOError) as e:
            logging.error(e)
            logging.error('can not connect to manager')
        
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, type, value, traceback):
        self.close()
    
    def connect(self):
        try:    os.unlink(self.local_sock_file)
        except: pass
        self.bind(self.addr_local)
        socket.socket.connect(self, self.addr_remote)

    def close(self):
        socket.socket.close(self)
        try:    os.unlink(self.local_sock_file)
        except: pass

    def command(self, cmd, payload=None):
        '''Send shadowsocks command'''
        pl = (cmd + ':' + json.dumps(payload)) if payload else cmd
        self.send(pl.encode())
        # self.recv(1506)

# Shadowsocks traffic statistic

class ShadowsocksStat:
    def __init__(self, manager_address, loop):
        self.loop = loop
        self.ctx = ShadowsocksCtx(manager_address)
        self.manager_address = manager_address
        self.callback=None
    
    def set_callback(self, callback):
        '''the callback when new traffic statistic data comes

        def callback(dict):...
        '''
        self.callback=callback

    def add_to_loop(self):
        self.ctx.connect()
        self.ctx.command('ping')
        self.loop.add(self.ctx, eventloop.POLL_IN, self)
    
    def handle_event(self, sock, fd, event):
        if sock == self.ctx and event == eventloop.POLL_IN:
            data = self.ctx.recv(4096)
            data = common.to_str(data)
            if data.startswith('stat:'):
                data = data.split('stat:')[1]
                stat_data = json.loads(data)
                if self.callback: self.callback(stat_data)
