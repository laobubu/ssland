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
from core.util import get_stdout, encodeURIComponent

config = {
    "executable": "ssserver",
    "config-file": "/etc/shadowsocks.json",
    "manager-address": "/var/run/shadowsocks-manager.sock",
    "method": "aes-256-cfb",
    "server": "127.0.0.1"
}

_executable = ('ssserver', )
_control_socket = None

## Basic Control Function

def init(_config):
    global _executable, _control_socket
    config.update(_config)
    _executable = tuple(config["executable"].split(' ')) + (
        '-c', config["config-file"], 
        '--manager-address', config['manager-address']
    )
    try:
        manager_address = config['manager-address']
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
            addr = manager_address
            addr_local = '/tmp/ssland.sock'
            family = socket.AF_UNIX
        _control_socket = socket.socket(family, socket.SOCK_DGRAM)
        _control_socket.bind(addr_local)
        _control_socket.connect(addr)
    except (OSError, IOError) as e:
        logging.error(e)
        logging.error('can not bind to manager address')
        exit(1)

def start(accounts):
    print get_stdout(_executable + ('-d', 'restart'))

def stop():
    print get_stdout(_executable + ('-d', 'stop'))



## Account Control Function

def add(ac):
    pl = {"server_port": ac['port'], "password": ac['sskey']}
    _control_socket.send(('add: '+json.dumps(pl)).encode())
    _control_socket.recv(1506)

def remove(ac):
    pl = {"server_port": ac['port']}
    _control_socket.send(('remove: '+json.dumps(pl)).encode())
    _control_socket.recv(1506)

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
