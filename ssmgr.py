#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Shadowsocks Manager Module.
#

from __future__ import print_function
import json, os, sys
from subprocess import Popen
import config
import user

def update_conf():
    '''
    Update Shadowsocks Config file.
    '''
    try:
        j = json.load(open(config.SS_CONF, 'r'))
    except:
        # Cannot read config file. Use default
        print("Cannot read Shadowsocks config file. File not exist or SSLand has no permission.", file=sys.stderr)
        j = {"server": "0.0.0.0", "port_password": {"6789": "aba"}, "timeout": 300, "method": "aes-256-cfb"}
    pp = {}
    for u in user.get_all():
        if u.suspended: continue
        port = str(config.user_port(u.id))
        key  = u.sskey
        if len(key) > 0: pp[port] = key
    j['port_password'] = pp
    json.dump(j, open(config.SS_CONF, 'w'))
    return j

def update_and_restart():
    '''
    Update Shadowsocks Config file, then restart shadowsocks.
    '''
    update_conf()
    Popen(config.SS_EXEC + ["-d", "restart"])
