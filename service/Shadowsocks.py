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
from core.util import get_stdout, encodeURIComponent, random_password
from core.ssutil import ShadowsocksStat
from web.models import TrafficStat, ProxyAccount

config = {
    "executable": "ssserver",
    "config-file": "/etc/shadowsocks.json",
    "manager-address": "/var/run/shadowsocks-manager.sock",
    "statistic_interval": 7200,
    "port-range": (6789, 45678),  # used to generate new account

    "method": "aes-256-cfb", # will be overridded by config-file
    "server": "127.0.0.1",   # will be overridded by config-file
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
_stat_logger = None

## Basic Control Function

def init(_config):
    global _executable, _stat_logger
    config.update(_config)
    _executable = tuple(config["executable"].split(' ')) + (
        '-c', config["config-file"], 
        '--manager-address', config['manager-address']
    )
    _stat_logger = StatLogger(config["statistic_interval"])

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
    _stat_logger.commit()


## Account Control Function

def add(ac):
    _stat_logger.bind_port_and_account(ac['port'], ac['id'])
    _manager_command('add', { "server_port": ac['port'], "password": ac['sskey'] })

def remove(ac):
    _manager_command('remove', { "server_port": ac['port'] })

def update(ac):
    remove(ac)
    add(ac)

def skeleton():
    import random
    service_name = __name__.rsplit('.', 1)[1]
    bad_port = [ acc.config['port'] for acc in ProxyAccount.objects.filter(service=service_name) ]
    portrng = config["port-range"]
    while True:
        port = random.randint(*portrng)
        if not port in bad_port: break
    return {
        "port": port,
        "sskey": random_password()
    }

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
    sskey = forms.CharField(label='Password', max_length=64, help_text='Used to encrypt your data. Make it complex!')
class AdminForm(forms.Form):
    port = forms.IntegerField(label='Port')
    sskey = forms.CharField(label='Password', max_length=64, help_text='Used to encrypt your data. Make it complex!')
    def is_valid_for_account(self, account):
        # check duplicated port
        portpart = '"port":%d\\D' % self.cleaned_data['port']
        query = ProxyAccount.objects.exclude(pk=account.pk).filter(config__regex=portpart, service=account.service)
        if query.count() > 0: 
            self._errors['port'] = ["Port taken by %s" % query[0].user.username]
        
        return len(self._errors)==0

# Other Shadowsocks specified functions

def _manager_command(cmd, payload=None):
    _stat.ctx.command(cmd, payload)

class StatLogger:
    def __init__(self, commit_interval=7200):
        self.cache={}
        self.port_to_account={}
        self.commit_interval=commit_interval
        self.next_report_time=time.time()

    def bind_port_and_account(self,port,account_id):
        self.port_to_account[str(port)] = account_id
    
    def handle_report(self, stat_data):
        '''Handle data from Shadowsocks'''
        for port_raw, amount in stat_data.iteritems():
            port=str(port_raw)
            if not port in self.cache: 
                self.cache[port] = amount
            else:
                self.cache[port] += amount
        if self.commit_interval and time.time() > self.next_report_time:
            self.commit()
            self.next_report_time = time.time() + self.commit_interval

    def commit(self):
        '''Write current stat into database, and reset the counter'''
        for port, amount in self.cache.iteritems():
            if not amount: continue
            logitem = TrafficStat(amount=amount)
            logitem.account_id = self.port_to_account[port]
            logitem.save()
        self.cache = {}

def _stat_updated(stat_data):
    '''Callback when Shadowsocks reports''' 
    _stat_logger.handle_report(stat_data)
