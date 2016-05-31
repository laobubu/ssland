#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Cronjob Script / Module.
#   Check, update and (un)suspend users.
#

import config, time, os, sys
from subprocess import Popen

TIME_FILE = config.TMP_ROOT + "/ssland.cron.ts"   # next avaliable time
FLAG_FILE = config.TMP_ROOT + "/ssland.cron.rst"  # a flag file for "update config and restart SS"
PID_FILE  = config.TMP_ROOT + "/ssland.cron.pid"  # current running item pid

def get_cd():
    '''
    get cron cool-down time (in sec.)
    '''
    result = 0
    
    try:
        f = open(TIME_FILE, 'r')
        last = float(f.read())
        result = last - time.time()
        f.close()
    except:
        pass
        
    if result <= 0:
        result = 0
        
    return result

def update_cd():
    '''
    Update CD time
    '''
    f = open(TIME_FILE, 'w')
    f.write(str(time.time() + config.UPDATE_INTERVAL))
    f.close()

def start():
    '''
    starting a background updating proces.
    returns cool-down time (in sec.)
    '''
    cd = get_cd()
    
    open(FLAG_FILE, 'a').close()
    
    try: # if the cron is already running, just return CD time.
        pid = int(open(PID_FILE, 'r').read())
        os.kill(pid, 0)
    except:
        Popen([sys.executable, __file__])
        
    return cd

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Update statistic, account status and Shadowsocks config.')
    parser.add_argument('-i', '--instant', action='store_true',  help="Don't wait for the cool-down time.")
    parser.add_argument('-s', '--stat',    action='store_true',  help="Update traffic statistic.")
    parser.add_argument('-f', '--force',   action='store_true',  help="Forcibly update and restart Shadowsocks.")
    flags = parser.parse_args(sys.argv[1:])
    
    # Execute Cronjob tasks
    pid = os.getpid()
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))
    
    if flags.instant:
        cd = get_cd()
        time.sleep(cd)
    
    # use -f argument to forcly update configuration and restart Shadowsocks 
    restart_ss = flags.force
    if os.path.isfile(FLAG_FILE):
        restart_ss = True
        os.remove(FLAG_FILE)
    
    if flags.stat:
        import traffic, limiter
        traffic.stat()
        lr = limiter.update_all()
        if len(lr):
            for username in lr:
                print("[Limiter] Suspend %s : %s"%(username, lr[username]))
            restart_ss = True
        
    if restart_ss:
        import traceback
        try:
            import ssmgr
            ssmgr.update_and_restart()
        except:
            print("Cannot update_and_restart SS.")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
    
    update_cd()
    os.remove(PID_FILE)
