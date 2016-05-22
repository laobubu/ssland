#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  User Module.
#   Including User class and reading/writing implementations
#

import re, os, json, time
import config
from hashlib import md5

class User:
    def __init__(self, src, password=None):
        '''
        Create one User instance from a Dict or String object.
        '''
        self.username = ''
        self.salted_password = ''
        self.id = 0
        self.join_since = 0
        self.name = ''
        self.comment = ''
        if not type(src) in [str, unicode]:
            for k in self.__dict__.keys():
                setattr(self, k, src[k])
        else:
            self.username = src
            self.salted_password = salt_password(password)
            self.join_since = time.time()
            self.id = next_id()
        
    def write(self):
        _USER_CACHE[self.username] = self
        update_lookup_table()
        f = file(user_filename(self.username), 'w')
        json.dump(self.__dict__, f)
        f.close()

salt_password = lambda password: md5(password + config.USER_SALT).hexdigest()
user_filename = lambda username: config.USER_ROOT + '/' + username + '.json'

# Every user info will be cached here to reduce harddisk IO
_USER_CACHE = {}
_USER_CACHE_ID = {}

def open(username):
    '''
    Get an existing User() instance.
    '''
    try:
        if not _USER_CACHE.has_key(username):
            f = file(user_filename(username), 'r')
            j = json.load(f)
            u = User(j)
            _USER_CACHE[username] = u
            f.close()
        return _USER_CACHE[username]
    except:
        return None

def cache_all():
    '''
    Load and cache all existing user files. 
    '''
    for fn in os.listdir(config.USER_ROOT):
        if fn[-5:] == '.json':
            open(fn[:-5])
    update_lookup_table()

def update_lookup_table():
    '''
    Update ID -> User lookup table.
    '''
    global _USER_CACHE_ID
    _USER_CACHE_ID = {}
    for i in _USER_CACHE:
        u = _USER_CACHE[i]
        _USER_CACHE_ID[u.id] = u

def next_id():
    '''
    Get next avaliable ID.
    '''
    ids = _USER_CACHE_ID.keys()
    ids.sort()
    l = len(ids)
    for i in range(l):
        if ids[i] > i: return i
    return l
