#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  User Module.
#   Including User class and reading/writing implementations
#

import re, os, json, time
import config
import database
from hashlib import md5

cursor = database.conn.cursor()

class User:
    def __init__(self, dbRow=None):
        '''
        Create one User instance from a Dict or String object.
        '''
        self.id = -1
        self.username = ''
        self.salted_password = ''
        self.sskey = ''
        self.since = 0
        self.suspended = False
        self.meta = {}
        if dbRow:
            [self.id, self.username, self.salted_password, self.sskey, self.since, self.suspended, meta] = dbRow
            self.meta = json.loads(meta)
    
    def create(self):
        if self.id == -1:
            cursor.execute('INSERT INTO user (username, password, sskey, meta) VALUES ("", "", "", "{}")')
            self.id = cursor.lastrowid
        return self.id
    
    def get_meta(self, name, default_value=None):
        try:
            return self.meta[name]
        except:
            return default_value
            
    def set_meta(self, name, value):
        self.meta[name] = value
        
    def set_password(self, password):
        self.salted_password = salt_password(password)
    
    def read(self):
        dc = cursor.execute('SELECT * FROM user WHERE id = %d' % self.id).fetchall()
        if len(dc) == 1:
            User.__init__(self, dc[0])
    
    def write(self):
        cursor.execute('UPDATE user SET username=?, password=?, sskey=?, since=?, suspended=?, meta=? WHERE id = ?',
        (
            self.username, self.salted_password, self.sskey, self.since, (1 if self.suspended else 0), json.dumps(self.meta), self.id
        ))
        database.conn.commit()
    
    def delete(self):
        cursor.execute('DELETE FROM user WHERE id = %d' % self.id)
        database.conn.commit()

def get_by_username(username):
    if not is_good_username(username): return None
    dc = cursor.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchall()
    if len(dc) == 0: return None
    return User(dc[0])

def get_by_id(id):
    dc = cursor.execute('SELECT * FROM user WHERE id = %d' % id).fetchall()
    if len(dc) == 0: return None
    return User(dc[0])
    
def get_all(only_active=False):
    where = []
    if only_active: where.append("suspended = 0")
    
    query = 'SELECT * FROM user'
    if len(where): query = query + ' WHERE ' + ' '.join(where)
    
    dc = cursor.execute(query).fetchall()
    return [User(row) for row in dc]

def delete_users(*username):
    if len(username) <= 0: return
    query = 'DELETE FROM user WHERE username IN %s' % str(username)
    if query[-2:] == ',)': query = query[:-2] + ')'
    cursor.execute(query)
    database.conn.commit()

def batch_update(*usernames, **dict):
    if len(usernames) <= 0: return
    qdata = ', '.join(["%s=:%s"%(id,id) for id in dict.keys()])
    qwhere = 'WHERE username IN %s' % str(usernames)
    if qwhere[-2:] == ',)': qwhere = qwhere[:-2] + ')'
    query = 'UPDATE user SET %s %s' % (qdata, qwhere)
    cursor.execute(query, dict)
    database.conn.commit()

is_good_username = lambda username: re.match(r'^[\w\-\.]+$', username)
salt_password = lambda password: md5(password + config.USER_SALT).hexdigest()
