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

# FIXME: Use another graceful way to pass current_user to processors
current_user = user.User({})

# decorator that used for login_only pages
def require_login(func):
    def func_wrapper(*args, **kwargs):
        global current_user
        username = request.get_cookie('ssl_un')
        password = request.get_cookie('ssl_pw')
        logined = username and password
        if logined:
            current_user = user.open(username)
            logined = current_user and current_user.salted_password == password
        if not logined:
            response.set_cookie('ssl_un', '', expires=0)
            response.set_cookie('ssl_pw', '', expires=0)
            return redirect('/login')
        return func(*args, **kwargs)
    return func_wrapper


# Website


@route('/')
@require_login
def server_index():
    return template('home', user=current_user)

@get('/login')
def login():
    return template('login', salt=config.USER_SALT)

@post('/login')
def do_login():
    username = request.forms.get('username')
    password = request.forms.get('password')
    
    if not (request.forms.get('md5ed') == '1' and re.match(r'^[a-f\d]{32}$', password)):
        password = user.salt_password(password)
    
    current_user = user.open(username)
    logined = current_user and current_user.salted_password == password
    
    if logined:
        response.set_cookie('ssl_un', username)
        response.set_cookie('ssl_pw', password)
        return redirect('/')
    
    return template('login', 
        username=username, 
        message=u'PASSWORD is ' + password, 
        salt=config.USER_SALT
    )

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root=WEB_ROOT+'/static')

run(host='localhost', port=8080)