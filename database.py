#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Database Module.
#    
#

import sqlite3
import config

DB_FILENAME = config.USER_ROOT + "/ssland.db"

conn = sqlite3.connect(DB_FILENAME)

def install():
    '''
    Create basic tables
    '''
    c = conn.cursor()
    
    c.execute(
    '''CREATE TABLE IF NOT EXISTS `user` (
        `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        `username`	TEXT,
        `password`	TEXT,
        `sskey`	TEXT,
        `since`	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `suspended`	BOOLEAN,
        `meta`	TEXT
    );''')
    
    c.close()

install()
