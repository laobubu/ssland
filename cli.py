#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  CLI
#

import config, user
import sys
import getpass

def print_help():
  print(
  '''
  Usage:

    user list
    user add {username}
    user add {username} {password}
    user add {username} {password} {sskey}
    user del {username}
    user passwd {username}
    user passwd {username} {password}
    user sskey {username}
    user sskey {username} {sskey}

    sys update
  ''')
  sys.exit(0)

def run(scope, action, argv):
    if scope == 'user':
        user.cache_all();
        if   action == 'list':
            for un in user._USER_CACHE.keys():
                print(un)
        elif action == 'add':
            username = argv[0] if len(argv) > 0 else raw_input('Username: ')
            password = argv[1] if len(argv) > 1 else getpass.getpass()
            sskey    = argv[2] if len(argv) > 2 else getpass.getpass('Shadowsocks Key: ')
            u = user.User(username, password)
            u.sskey = sskey
            u.write()
        elif action == 'del':
            for un in argv:
                os.remove(user.user_filename(un))
        elif action == 'passwd':
            username = argv[0] if len(argv) > 0 else raw_input('Username: ')
            password = argv[1] if len(argv) > 1 else getpass.getpass()
            u = user.open(username)
            u.set_password(password)
            u.write()
        elif action == 'sskey':
            username = argv[0] if len(argv) > 0 else raw_input('Username: ')
            sskey    = argv[1] if len(argv) > 1 else getpass.getpass('Shadowsocks Key: ')
            u = user.open(username)
            u.sskey = sskey
            u.write()
    elif scope == 'sys':
        if   action == 'update':
            import ssmgr
            ssmgr.update_and_restart()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print_help()

    scope = sys.argv[1]
    action = sys.argv[2]
    argv = sys.argv[3:]
    
    run(scope, action, argv)
