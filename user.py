#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  User Module.
#   Including User class and reading/writing implementations
#

import re, json, time
import config
from hashlib import md5

class User:
    def __init__(self, username):
        self.username = username
        self.salted_password = ''
        self.join_since = time.time()
        self.name = ''
        self.comment = ''
        self.port = 0
        
    def write(self):
        _USER_CACHE[self.username] = self
        f = file(user_filename(self.username), 'w')
        json.dump(self.__dict__, f)
        f.close()

salt_password = lambda password: md5(password + config.USER_SALT).hexdigest()
user_filename = lambda username: config.USER_ROOT + '/' + username + '.json'

# Every user info will be cached here to reduce harddisk IO
_USER_CACHE = {}

def open(username):
    try:
        if not _USER_CACHE.has_key(username):
            f = file(user_filename(username), 'r')
            j = json.load(f)
            u = User(username)
            for k in u.__dict__.keys():
                u[k] = j[k]
            _USER_CACHE[username] = u
            f.close()
        return _USER_CACHE[username]
    except:
        return None
