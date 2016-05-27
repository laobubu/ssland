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

bottle.debug(True)

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

# get salted password from request.forms
def get_salted_password():
    password = request.forms.get('password')
    if not (request.forms.get('md5ed') == '1' and re.match(r'^[a-f\d]{32}$', password)):
        password = user.salt_password(password)
    return password

# Website

@post('/passwd')
@require_login
def passwd():
    password = get_salted_password()
    
    u = current_user
    if (u.id == 0): u = user.open(request.forms.get('username'))
    
    u.salted_password = password
    u.write()
    return redirect('/')

@post('/sskey')
@require_login
def sskey():
    sskey = request.forms.get('sskey')
    
    u = current_user
    if (u.id == 0): u = user.open(request.forms.get('username'))
    
    u.sskey = sskey
    u.write()
    
    import cron;
    cd = cron.start()
    if cd <= 0.5:
        msg = "Your Shadowsocks key is changed!"
    else:
        msg = "The Shadowsocks key will be changed in %.2f sec" % cd
    
    return template(
        'home', 
        config=config, 
        user=current_user,
        message=msg, 
        users=(user._USER_CACHE if current_user.id == 0 else {})
    )

@post('/cli')
@require_login
def cli():
    if (current_user.id != 0):
        return redirect('/')
    
    argv = request.forms.get('cmd').split(' ')
    import cli
    cli.run(argv[0], argv[1], argv[2:])
    
    return template(
        'home', 
        config=config, 
        user=current_user,
        message="EXECUTED",
        users=user._USER_CACHE
    )

@route('/updateServer')
@require_login
def updateServer():
    if (current_user.id != 0):
        return redirect('/')
    
    import cron;
    cd = cron.start()
    msg = "The Shadowsocks will be updated in %.2f sec" % cd
    
    return template(
        'home', 
        config=config, 
        user=current_user,
        message=msg, 
        users=user._USER_CACHE
    )

@route('/suspend/<suspend>/<username>')
@require_login
def suspend(suspend, username):
    if (current_user.id != 0):
        return redirect('/')
    
    u = user.open(username)
    u.suspended = suspend != "0"
    u.write()
    
    msg = 'User %s status changed. Please click [Update SSConfig].' % username
    return template(
        'home', 
        config=config, 
        user=current_user,
        message=msg, 
        users=(user._USER_CACHE if current_user.id == 0 else {})
    )

@route('/')
@require_login
def server_index():
    if (current_user.id == 0):
        user.cache_all()
        
    return template(
        'home', 
        config=config, 
        user=current_user,
        users=(user._USER_CACHE if current_user.id == 0 else {})
    )

# Login and Logout

@get('/logout')
def logout():
    response.set_cookie('ssl_un', '', expires=0)
    response.set_cookie('ssl_pw', '', expires=0)
    return redirect('/login')

@get('/login')
def login():
    return template('login', salt=config.USER_SALT)

@post('/login')
def do_login():
    username = request.forms.get('username')
    password = get_salted_password()
    
    current_user = user.open(username)
    logined = current_user and current_user.salted_password == password
    
    if logined:
        response.set_cookie('ssl_un', username)
        response.set_cookie('ssl_pw', password)
        return redirect('/')
    
    return template('login', 
        username=username, 
        message='User not found.' if not current_user else 'Password is incorrect.', 
        salt=config.USER_SALT
    )

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root=WEB_ROOT+'/static')

run(host=config.WEB_HOST, port=config.WEB_PORT)
