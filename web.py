#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  WebServer Module.
#   Use `web.run(host='127.0.0.1', port=8080)` to start
#

import re
import config, user
import bottle
from bottle import route, get, post, run, template, redirect, static_file, response, request

WEB_ROOT = config.WEB_ROOT
bottle.TEMPLATE_PATH.insert(0, WEB_ROOT)

@route('/')
def server_index():
    return redirect('/login')

@get('/login')
def login():
    return template('login', salt=config.USER_SALT)

@post('/login')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    
    if not (request.forms.get('md5ed') == '1' and re.match(r'^[a-f\d]{32}$', password)):
        password = user.salt_password(password)
    
    return template('login', 
        username=username, 
        message=u'PASSWORD is ' + password, 
        salt=config.USER_SALT
    )

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root=WEB_ROOT+'/static')

run(host='localhost', port=8080)