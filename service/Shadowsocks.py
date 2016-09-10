#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Shadowsocks service
#

from __future__ import absolute_import
import base64
import socket
import json
import logging
import time
import os
from core.util import get_stdout, encodeURIComponent

config = {
    "executable": "ssserver",
    "config-file": "/etc/shadowsocks.json",
    "manager-address": "/var/run/shadowsocks-manager.sock",
    "method": "aes-256-cfb",
    "server": "127.0.0.1"
}

'''
account_config format:
{
    "port": 1234,
    "sskey": "password",
}
'''

_executable = ('ssserver', )
_stat = None 

## Basic Control Function

def init(_config):
    global _executable
    config.update(_config)
    _executable = tuple(config["executable"].split(' ')) + (
        '-c', config["config-file"], 
        '--manager-address', config['manager-address']
    )

def start(accounts, event_loop=None):
    global _stat

    stop()
    
    # Read and update Shadowsocks conf file
    conf_filename = config["config-file"]
    try:    conf = json.load(open(conf_filename, 'r'))
    except: conf = {"server": "0.0.0.0", "timeout": 300, "method": "aes-256-cfb"}
    
    pps = conf['port_password'] if 'port_password' in conf else {}
    if "server_port" in conf and "password" in conf:
        logging.warn("removing server_port and password fields in %s", conf_filename)
        pps[conf["server_port"]] = conf["password"]
        del conf["server_port"]
        del conf["password"]
    
    # edge case: no active account
    # if so, create one account and remove it after shadowsocks starts 
    temp_port = 0
    if len(pps) == 0 :
        logging.warn('No active account in %s', conf_filename)
        temp_port = 54301
        pps[temp_port] = "ssland-temp-account"
    
    conf['port_password'] = pps
    json.dump(conf, open(conf_filename, 'w'))

    # start proxy server
    try: os.unlink(config['manager-address'])
    except: pass
    get_stdout(_executable + ('-d', 'restart'))

    # add to event_loop
    time.sleep(3)
    _stat = ShadowsocksStat(config['manager-address'], event_loop)
    _stat.add_to_loop()

    # active active accounts
    for account in accounts:
        add(account)

    # fixing the edge case
    if temp_port:
        logging.warn('Removing temp account')
        remove({'port': temp_port})

def stop():
    get_stdout(_executable + ('-d', 'stop'))



## Account Control Function

def add(ac):
    _manager_command('add', { "server_port": ac['port'], "password": ac['sskey'] })

def remove(ac):
    _manager_command('remove', { "server_port": ac['port'] })

def update(ac):
    remove(ac)
    add(ac)



## Web-panel Related

def html(account_config):
    ssurl = '%s:%s@%s:%d' % (
        config['method'],
        account_config['sskey'],
        config['server'],
        account_config['port']
    )
    imgurl = '/qr.svg?data=%s' % encodeURIComponent('ss://' + base64.b64encode(ssurl))
    return '\n'.join([
        '<a href="%s" target="_blank"><img src="%s" class="float"></a>' % (imgurl,imgurl),
        '<table class="strip">',
        '  <tr><th>server</th>      <td>%s</td></tr>' % config['server']          ,
        '  <tr><th>server_port</th> <td>%d</td></tr>' % account_config['port']    ,
        '  <tr><th>password</th>    <td>%s</td></tr>' % account_config['sskey']   ,
        '  <tr><th>method</th>      <td>%s</td></tr>' % config['method']          , 
        '</table>',
    ])


from django import forms
class UserForm(forms.Form):
    sskey = forms.CharField(label='Password', max_length=100)


# Other Shadowsocks specified functions

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

# Functions
def _manager_command(cmd, payload=None):
    _stat.ctx.command(cmd, payload)

# Shadowsocks traffic statistic
from shadowsocks import eventloop, common

class ShadowsocksStat:
    def __init__(self, manager_address, loop):
        self.loop = loop
        self.ctx = ShadowsocksCtx(manager_address)
        self.manager_address = manager_address
    
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
                print('got stat!!!!')
                print(data)
