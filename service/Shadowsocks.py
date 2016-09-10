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
_control_socket = None

## Basic Control Function

def init(_config):
    global _executable, _control_socket
    config.update(_config)
    _executable = tuple(config["executable"].split(' ')) + (
        '-c', config["config-file"], 
        '--manager-address', config['manager-address']
    )

def start(accounts):
    stop()
    
    conf_filename = config["config-file"]
    try:    conf = json.load(open(conf_filename, 'r'))
    except: conf = {"server": "0.0.0.0", "timeout": 300, "method": "aes-256-cfb"}
    
    pps = conf['port_password'] if 'port_password' in conf else {}
    if "server_port" in conf and "password" in conf:
        logging.warn("removing server_port and password fields in %s", conf_filename)
        pps[conf["server_port"]] = conf["password"]
        del conf["server_port"]
        del conf["password"]

    for account in accounts:
        pps[account['port']] = account['sskey']
    
    # edge case: no active account
    # if so, create one account and remove it after shadowsocks starts 
    temp_port = 0
    if len(pps) == 0 :
        logging.warn('No active account in %s', conf_filename)
        temp_port = 54301
        pps[temp_port] = "ssland-temp-account"
    
    conf['port_password'] = pps
    json.dump(conf, open(conf_filename, 'w'))

    try: os.unlink(config['manager-address'])
    except: pass

    get_stdout(_executable + ('-d', 'restart'))
    time.sleep(3)

    _manager_connect()

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

def _manager_connect():
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
            addr_local = '/var/run/ssland.sock'
            family = socket.AF_UNIX
            try:
                os.unlink(addr_local)
            except:
                pass
        _control_socket = socket.socket(family, socket.SOCK_DGRAM)
        _control_socket.bind(addr_local)
        _control_socket.connect(addr)
    except (OSError, IOError) as e:
        logging.error(e)
        logging.error('can not connect to manager')
        exit(1)

def _manager_command(cmd, payload=None):
    pl = (cmd + ':' + json.dumps(payload)) if payload else cmd
    _control_socket.send(pl.encode())
    _control_socket.recv(1506)
