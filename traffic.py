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
IPTABLES = ('/sbin/iptables',)
CHAIN_NAME = 'SSLAND2'

def stat():
    '''
    Get the stat data and storage into database.
    '''
    update_iptables()
    cs, ec = get_stdout(IPTABLES + ('-nxvL', CHAIN_NAME)) # get current stat
    if ec == 3: return False   # No privilege
    get_stdout(IPTABLES + ('-Z',CHAIN_NAME)) # empty IPTABLES stat
    
    t  = {}  # dict PORT=>(pkgs, bytes)
    for i in re.findall(r"^\s*(\d+)\s+(\d+).+[sd]pt:(\d+)", cs, re.M):
        # i = Pkgs   Traffic(byte)   port
        port = int(i[2])
        if not port in t: t[port] = [0, 0]
        t[port][0] += int(i[0])
        t[port][1] += int(i[1])
        
    query = []
    users = user.get_all(only_active=True)
    for u in users:
        port = config.user_port(u.id)
        if port in t:
            ti = t[port]
            if ti[0] and ti[1]: query.append((u.id, ti[0], ti[1]))      # skip empty record
            
    cursor = database.conn.cursor()
    cursor.executemany('INSERT INTO traffic(user,packages,traffic) VALUES (?, ?, ?)', query)
    cursor.close()
    database.conn.commit()

def update_iptables():
    '''
    Add IPTABLES rules if necessary.
    '''
    cs, ec = get_stdout(IPTABLES + ('-nxvL', CHAIN_NAME)) # get current stat
    if ec == 3: return False   # No privilege
    if ec == 1: # chain not found
        # create the chain
        get_stdout(IPTABLES + ('-N',CHAIN_NAME))
        get_stdout(IPTABLES + ('-I','INPUT','1','-j',CHAIN_NAME))
        get_stdout(IPTABLES + ('-I','OUTPUT','1','-j',CHAIN_NAME))
    
    sport = set(int(r) for r in re.findall(r"\bspt:(\d+)", cs, re.M))
    dport = set(int(r) for r in re.findall(r"\bdpt:(\d+)", cs, re.M))
    
    users = user.get_all(only_active=True)
    for u in users:
        port = config.user_port(u.id)
        if not port in sport:   get_stdout(IPTABLES + ('-A',CHAIN_NAME,'-p','tcp','--sport',str(port)))
        if not port in dport:   get_stdout(IPTABLES + ('-A',CHAIN_NAME,'-p','tcp','--dport',str(port)))

QS_NONE=0
QS_ALL=1
QS_MONTH=2
QS_DAY=3
QS_YEAR=4

def query(uid=-1, min_time=None, max_time=None, sum=QS_NONE):
    '''
    Query database, returning Array of tuples (userID, pkgs, bytes, str_time)
    '''
    cond = []
    if uid>=1:    cond.append('user = %d'%uid)
    if min_time:  cond.append('datetime(time) >= \'%s\''%min_time)  # format: 2016-05-10 12:59:00
    if max_time:  cond.append('datetime(time) <= \'%s\''%max_time)
    
    q_where = (' WHERE '+' AND '.join(cond)) if len(cond) else ''
    if sum:
        sumfunc = "time"                        if sum == QS_ALL    else \
                  "strftime('%Y', time)"        if sum == QS_YEAR   else \
                  "strftime('%Y-%m', time)"     if sum == QS_MONTH  else \
                  "date(time)"                  if sum == QS_DAY    else \
                  "time"
        query = 'SELECT user, sum(packages), sum(traffic), %s AS t FROM traffic %s GROUP BY user' % (sumfunc, q_where)
        if sumfunc != "time": query = query + ', t'
    else:
        query = 'SELECT user, packages, traffic, time FROM traffic' + q_where
    
    cursor = database.conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    
    return result
