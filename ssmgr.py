#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Shadowsocks Manager Module.
#

from __future__ import print_function
import json, os, sys
import utils
import config
import user

conf_cache = None

def read_conf(force=False):
    global conf_cache
    if conf_cache and not force: return
    try:
        conf_cache = json.load(open(config.SS_CONF, 'r'))
    except:
        conf_cache = {"server": "0.0.0.0", "port_password": {}, "timeout": 300, "method": "aes-256-cfb"}
        print("Cannot read Shadowsocks config file. File not exist or SSLand has no permission.", file=sys.stderr)

def write_conf():
    read_conf()
    json.dump(conf_cache, open(config.SS_CONF, 'w'))

def update_conf():
    '''
    Read Shadowsocks Config file, fill with users' port and sskey, and save it.
    '''
    read_conf(True)
    pp = {}
    for u in user.get_all(only_active=True):
        if not len(u.sskey): continue
        port = str(u.get_port())
        pp[port] = u.sskey
    conf_cache['port_password'] = pp
    write_conf()

def update_and_restart():
    '''
    Update Shadowsocks Config file, then restart shadowsocks.
    '''
    update_conf()
    utils.get_stdout(config.SS_EXEC + ["-d", "restart"])
