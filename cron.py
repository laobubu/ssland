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
    if "-h" in sys.argv:
      print('''
  SSLand cronjob script
  
    Update statistic, account status and Shadowsocks config.
  
  Usage:
  
    [-f]        Forcibly update and restart Shadowsocks.
      ''')
      sys.exit(0)
    
    # Execute Cronjob tasks
    pid = os.getpid()
    with open(PID_FILE, 'w') as f:
        f.write(str(pid))
    
    cd = get_cd()
    time.sleep(cd)
    
    # use -f argument to forcly update configuration and restart Shadowsocks 
    restart_ss = "-f" in sys.argv
    if os.path.isfile(FLAG_FILE):
        restart_ss = True
        os.remove(FLAG_FILE)
        
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
