#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  CLI
#

import config, user
import traffic
import ssmgr
from utils import *
import sys, os, getpass

def print_help():
  print(
  '''
  Usage:

    user list
    user add [username] [password] [sskey]
    user del username [username2] [...]
    user suspend username [username2] [...]
    user unsuspend username [username2] [...]
    user passwd [username] [password]
    user sskey [username] [sskey]

    sys update
    
    tx query      (tx = traffic)
    tx update
  ''')
  sys.exit(0)

def run(scope, action, argv):
    if scope == 'user':
        if   action == 'list':
            print("id\tusername\tsuspended\tport\tsskey")
            for u in user.get_all():
                print('\t'.join(( str(item) for item in 
                    (u.id, u.username, 'True' if u.suspended else 'False', u.get_port(), u.sskey)
                )))
        elif action == 'add':
            username = argv[0] if len(argv) > 0 else raw_input('Username: ')
            password = argv[1] if len(argv) > 1 else getpass.getpass()
            sskey    = argv[2] if len(argv) > 2 else getpass.getpass('Shadowsocks Key: ')
            u = user.User()
            u.username = username
            u.set_password(password)
            u.sskey = sskey
            u.create()
            u.write()
        elif action == 'del':
            user.delete_users(*argv)
        elif action in ['suspend', 'unsuspend']:
            user.batch_update(*argv, suspended=(1 if action == 'suspend' else 0))
        elif action == 'passwd':
            username = argv[0] if len(argv) > 0 else raw_input('Username: ')
            password = argv[1] if len(argv) > 1 else getpass.getpass()
            u = user.get_by_username(username)
            u.set_password(password)
            u.write()
        elif action == 'sskey':
            username = argv[0] if len(argv) > 0 else raw_input('Username: ')
            sskey    = argv[1] if len(argv) > 1 else raw_input('Shadowsocks Key: ')
            u = user.get_by_username(username)
            u.sskey = sskey
            u.write()
        else:
            print_help()
    elif scope == 'sys':
        if   action == 'update':
            ssmgr.update_and_restart()
            get_stdout(["./web.py", "-d", "restart"])
        elif action == 'init':
            # RUN THIS WHEN SYSTEM BOOTS ONLY !
            traffic.update_iptables()
            get_stdout(["./web.py", "-d", "restart"])
            ssmgr.update_and_restart()
        else:
            print_help()
    elif scope == 'tx' or scope == 'traffic':
        if   action == 'query':
            un = {}
            for u in user.get_all():
                un[u.id] = u.username
            for r in traffic.query(sum=traffic.QS_DAY):
                print("%s\t%s\t%s"%(un[r[0]], r[3], sizeof_fmt(r[2])))
        elif action == 'update':
            traffic.stat()
        else:
            print_help()
    else:
        print_help()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print_help()

    scope = sys.argv[1]
    action = sys.argv[2]
    argv = sys.argv[3:]
    
    run(scope, action, argv)
