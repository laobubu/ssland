#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Traffic Module.
#   Stat traffic
#

import database, user, config
import re
from utils import get_stdout

# the command that runs iptables
IPTABLES = ('iptables')

def stat():
    '''
    Get the stat data and storage into database.
    Add IPTABLES rules if necessary.
    '''
    cs, ec = get_stdout(IPTABLES + ('-nxvL', 'SSLAND')) # get current stat
    if ec == 3: return False   # No privilege
    if ec == 1: # chain not found
        # create the chain
        get_stdout(IPTABLES + ('-N','SSLAND'))
        get_stdout(IPTABLES + ('-I','OUTPUT','1','-j','SSLAND'))
    get_stdout(IPTABLES + ('-Z','SSLAND')) # empty IPTABLES stat
    
    t  = {}  # dict PORT=>(pkgs, bytes)
    for i in re.findall(r"^\s*(\d+)\s+(\d+).+dpt:(\d+)", cs, re.M):
        # i = Pkgs   Traffic(byte)   port
        t[int(i[2])] = ( int(i[0]) , int(i[1]) )
        
    query = []
    users = user.get_all()
    for u in users:
        if u.suspended: continue
        port = config.user_port(u.id)
        if port in t:
            ti = t[port]
            query.append((u.id, ti[0], ti[1]))
        else:
            get_stdout(IPTABLES + ('-A','SSLAND','-p','tcp','--dport',str(port)))
            
    cursor = database.conn.cursor()
    cursor.executemany('INSERT INTO traffic(user,packages,traffic) VALUES (?, ?, ?)', query)
    cursor.close()
    database.conn.commit()

def query_all(least_time=None):
    '''SELECT user, sum(packages), sum(traffic) FROM traffic WHERE time >= datetime('2016-05-29 07:59:00') GROUP BY user'''
