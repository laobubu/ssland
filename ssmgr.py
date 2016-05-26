#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Shadowsocks Manager Module.
#

import json, os
from subprocess import Popen
import config
import user

def update_conf():
    '''
    Update Shadowsocks Config file.
    NOTICE! Before using this, call user.cache_all()
    '''
    j = json.load(open(config.SS_CONF, 'r'))
    pp = {}
    for id in user._USER_CACHE:
        u = user._USER_CACHE[id]
        if u.suspended: continue
        port = str(config.user_port(u.id))
        key  = u.sskey
        pp[port] = key
    j['port_password'] = pp
    json.dump(j, open(config.SS_CONF, 'w'))
    return j

def update_and_restart():
    '''
    Update Shadowsocks Config file, then restart shadowsocks.
    NOTICE! Before using this, call user.cache_all()
    '''
    update_conf()
    Popen(config.SS_EXEC + ["-d", "restart"])
