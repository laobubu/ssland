#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Shadowsocks service
#

from __future__ import absolute_import, print_function
import base64
import json
import logging
import time
import os
from collections import OrderedDict
from core.util import get_stdout, encodeURIComponent
from core.ssutil import ShadowsocksStat
from web.models import ProxyAccount, TrafficStat

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
    _stat.set_callback(_stat_updated)
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
    from core.util import html_strip_table
    
    ssurl = '%s:%s@%s:%d' % (
        config['method'],
        account_config['sskey'],
        config['server'],
        account_config['port']
    )
    imgurl = '/qr.svg?data=%s' % encodeURIComponent('ss://' + base64.b64encode(ssurl))
    
    table = OrderedDict()
    table['server']         = config['server']
    table['server_port']    = account_config['port']
    table['password']       = account_config['sskey']
    table['method']         = config['method']

    return '\n'.join(
        ['<a href="%s" target="_blank"><img src="%s" class="float"></a>' % (imgurl, imgurl)] + 
        html_strip_table(table)
    )


from django import forms
class UserForm(forms.Form):
    sskey = forms.CharField(label='Password', max_length=100)

# Other Shadowsocks specified functions

def _manager_command(cmd, payload=None):
    _stat.ctx.command(cmd, payload)

def _stat_updated(stat_data):
    print('got stat!!!!')
    print(stat_data)
