#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Limiter Module.
#   Suspend users automatically
#

import config, database, user, traffic
import utils
import datetime

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def check_user(u):
    '''
    Check if one user shall be suspended. Returning the reason why suspend, or None.
    @type u: user.User
    '''
    if u.suspended: return None
    
    msg = None
    
    for r in u.get_meta("limit", []):
        if not 'type'   in r : continue
        if not 'amount' in r : continue
        if not 'since'  in r : continue 
        type, amount, since = r['type'], r['amount'], r['since']
        
        now   = datetime.datetime.now()
        
        since = datetime.datetime(now.year, now.month, 1)                       if since == 'this-month'  else \
                datetime.datetime(now.year, now.month, now.day - now.weekday()) if since == 'this-week'   else \
                datetime.datetime.strptime(since, DATE_FORMAT)
        
        if   type == 'time':     # Time-to-expire rule. amount: useless
            if now >= since:
                msg = "Expired: %s" % r['since']
                break
        elif type == 'traffic':  # Traffic-limited rule. amount: traffic in bytes.
            tq = traffic.query(uid=u.id, min_time=since.strftime(DATE_FORMAT), sum=traffic.QS_ALL)
            if tq[0][2] > amount:
                msg = "Traffic: %s excceed %s" % (utils.sizeof_fmt(tq[0][2]), utils.sizeof_fmt(amount))
                break
        
    return msg

def update_all():
    '''
    Suspend users who exceed the limitation.
    '''
    results = {}
    datestr = datetime.datetime.now().strftime(DATE_FORMAT)
    for u in user.get_all(only_active=True):
        reason = check_user(u)
        if reason:
            u.suspended = True
            u.set_meta("limiter_log", "%s: %s"%(datestr, reason))
            u.write(commit=False)
            results[u.username] = reason
    database.conn.commit()
    return results

if __name__ == "__main__":
    lr = update_all()
    if len(lr):
        for username in lr:
            print("[Limiter] Suspend %s : %s"%(username, lr[username]))
