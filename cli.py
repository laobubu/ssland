#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  CLI
#

import config, user
import sys
import getpass

def _print_help():
    print(
'''
Usage:

 user list
 user add {username}
 user add {username} {password}
 user del {username}
 user passwd {username}
 user passwd {username} {password}
 
 sys update
''')
    sys.exit(0)

if len(sys.argv) < 3:
    _print_help()

scope = sys.argv[1]
action = sys.argv[2]
argv = sys.argv[3:]

if scope == 'user':
    user.cache_all();
    if   action == 'list':
        for un in user._USER_CACHE.keys():
            print(un)
    elif action == 'add':
        username = argv[0] if len(argv) > 0 else raw_input('Username: ')
        password = argv[1] if len(argv) > 1 else getpass.getpass()
        user.User(username, password).write()
    elif action == 'del':
        for un in argv:
            os.remove(user.user_filename(un))
    elif action == 'passwd':
        username = argv[0] if len(argv) > 0 else raw_input('Username: ')
        password = argv[1] if len(argv) > 1 else getpass.getpass()
        u = user.open(username)
        u.set_password(password)
        u.write()
elif scope == 'sys':
    if   action == 'update':
        import ssmgr
        ssmgr.update_and_restart()
