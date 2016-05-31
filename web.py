#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  WebServer Module.
#   Use `web.run(host='127.0.0.1', port=8080)` to start
#

import re
import config, user
import bottle
import json, sys, os
import utils
from bottle import route, get, post, run, template, redirect, static_file, response, request
from functools import wraps

WEB_ROOT = config.WEB_ROOT
bottle.TEMPLATE_PATH.insert(0, WEB_ROOT)

bottle.debug(True)

# FIXME: Use another graceful way to pass current_user to processors
current_user = user.User()
is_admin = False

# decorator that used for login_only pages
def require_login(func):
    def func_wrapper(*args, **kwargs):
        global current_user, is_admin
        uid_str = request.get_cookie('ssl_uid')
        password = request.get_cookie('ssl_pw')
        logined = uid_str and password
        if logined:
            current_user = user.get_by_id(int(uid_str))
            logined = current_user and current_user.salted_password == password
            is_admin = logined and current_user.id == config.USER_ADMIN
        if not logined:
            response.set_cookie('ssl_uid', '', expires=0)
            response.set_cookie('ssl_pw', '', expires=0)
            return redirect('/login')
        return func(*args, **kwargs)
    return func_wrapper

# decorator that used for user json APIs. Decorated function shall return a dict.
def json_api(func):
    def func_wrapper(*args, **kwargs):
        rs = func(*args, **kwargs)
        try:
            ds = json.dumps(rs)
            response.content_type = 'application/json; charset=utf-8'
            return ds
        except:
            return rs
    return func_wrapper
    
# decorator for admin APIs
def admin_api(uri):
    def admin_api_out(func):
        @wraps(func)
        @post(uri)
        @require_login
        @json_api
        def func_wrapper(*args, **kwargs):
            if not is_admin: return {"error": "not_admin"}
            return func(*args, **kwargs)
    return admin_api_out

# get salted password from request.forms
def get_salted_password():
    password = request.forms.get('password')
    if not (request.forms.get('md5ed') == '1' and re.match(r'^[a-f\d]{32}$', password)):
        password = user.salt_password(password)
    return password

# home panel Generator
get_home_content = lambda msg=None: template('home', config=config, user=current_user, is_admin=is_admin, message=msg)



# Website for normal User

@route('/')
@require_login
def server_index():
    return get_home_content()

@post('/passwd')
@require_login
def set_passwd():
    u = current_user    
    u.salted_password = get_salted_password()
    u.write()
    return get_home_content("Password has changed.")

@post('/sskey')
@require_login
def set_sskey():
    u = current_user
    u.sskey = request.forms.get('sskey')
    u.write()
    
    import cron;
    cd = cron.start()
    if cd <= 0.5:
        msg = "Your Shadowsocks key is changed!"
    else:
        msg = "The Shadowsocks key will be changed in %.2f sec" % cd
    
    return get_home_content(msg)



# Website for Administrator

@route('/admin')
@require_login
def server_admin():
    if not is_admin:    return redirect('/')
    return static_file('admin.html', root=WEB_ROOT)

@admin_api('/admin/cli')
def admin_cli():
    argv = request.forms.get('cmd').split(' ')
    out, rtn = utils.get_stdout([sys.executable, './cli.py'] + argv)
    return {
        "retval": rtn,
        "output": out
    }

@admin_api('/admin/restart')
def admin_restart():
    import cron
    cd = cron.start()
    return { "time": cd }

@admin_api('/admin/basic')
def admin_basic():
    return { "user_salt": config.USER_SALT }

@admin_api('/admin/user/add')
def admin_user_add():
    u = user.User()
    u.username, u.salted_password, u.sskey = [request.forms.get(n) for n in ('username', 'password', 'sskey')]
    u.create()
    u.write()
    return { "id": u.id }

@admin_api('/admin/user/del')
def admin_user_del():
    username = request.forms.get('username')
    user.delete_users(username)
    return { "status": "ok" }

@admin_api('/admin/user/list')
def admin_user_list():
    list = [ u.__dict__ for u in user.get_all()]
    for i in range(len(list)):
        list[i]['port'] = config.user_port(list[i]['id'])
    return { "list": list }

@admin_api('/admin/user/passwd')
def admin_user_passwd():
    username, password = [request.forms.get(n) for n in ('username', 'password')]
    u = user.get_by_username(username)
    u.salted_password = password
    u.write()
    return { "status": "ok" }

@admin_api('/admin/user/sskey')
def admin_user_sskey():
    username, sskey = [request.forms.get(n) for n in ('username', 'sskey')]
    u = user.get_by_username(username)
    u.sskey = sskey
    u.write()
    return { "status": "ok" }

@admin_api('/admin/user/limit')
def admin_user_limit():
    username, limit = [request.forms.get(n) for n in ('username', 'limit')]
    limit = json.loads(limit)
    u = user.get_by_username(username)
    u.set_meta("limit", limit)
    u.write()
    return { "status": "ok" }

@admin_api('/admin/user/suspend')
def admin_user_suspend():
    username, suspend = [request.forms.get(n) for n in ('username', 'suspend')]
    
    u = user.get_by_username(username)
    u.suspended = suspend == "1"
    u.write()
    return { "username": username, "suspended": u.suspended }

# Login and Logout

@get('/logout')
def logout():
    response.set_cookie('ssl_uid', '', expires=0)
    response.set_cookie('ssl_pw', '', expires=0)
    return redirect('/login')

@get('/login')
def login():
    return template('login', salt=config.USER_SALT)

@post('/login')
def do_login():
    username = request.forms.get('username')
    password = get_salted_password()
    
    current_user = user.get_by_username(username)
    logined = current_user and current_user.salted_password == password
    
    if logined:
        response.set_cookie('ssl_uid', str(current_user.id))
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

if __name__ == "__main__":
    import argparse, os, sys, time, signal
    parser = argparse.ArgumentParser(description='SSLand Web Server')
    parser.add_argument('-d', '--daemon',  action='store', required=False, help="Control web server daemon")
    flags = parser.parse_args(sys.argv[1:])
    
    DAEMON_PID_FILE = config.TMP_ROOT + "/ssland.web.pid"
    
    if flags.daemon in ('stop', 'restart'):
        try:
            with open(DAEMON_PID_FILE, 'r') as f:
                pid = int(f.read())
                os.kill(pid, signal.SIGTERM)
            os.remove(DAEMON_PID_FILE)
        except:
            pass
        if flags.daemon == 'stop': sys.exit(0)
    
    if flags.daemon in ('start', 'restart'):
        
        def freopen(f, mode, stream):
            oldf = open(f, mode)
            oldfd = oldf.fileno()
            newfd = stream.fileno()
            os.close(newfd)
            os.dup2(oldfd, newfd)
            
        def handle_exit(signum, _):
            if signum == signal.SIGTERM:
                sys.exit(0)
            sys.exit(1)
        signal.signal(signal.SIGINT, handle_exit)
        signal.signal(signal.SIGTERM, handle_exit)
        
        already_running=False
        try:
            with open(DAEMON_PID_FILE, 'r') as f:
                pid = int(f.read())
                os.kill(pid, 0)
                print("Already running daemon with PID %d" % pid)
                already_running=True
        except:
            pass
            
        if already_running:
            sys.exit(0)
        else:
            # Thread not found. Create
            pid = os.fork()
            assert pid != -1
            if pid > 0:
                # parent waits for its child
                time.sleep(5)
                sys.exit(0)
                
            # child signals its parent to exit
            ppid = os.getppid()
            pid = os.getpid()
            
            with open(DAEMON_PID_FILE, 'w') as f:
                f.write(str(pid))
            
            os.setsid()
            signal.signal(signal.SIGHUP, signal.SIG_IGN)
            
            print("Daemon running, PID %d" % pid)
            os.kill(ppid, signal.SIGTERM)
            
            sys.stdin.close()
            try:
                log_file = "/var/log/ssland.web.log"
                freopen(log_file, 'a', sys.stdout)
                freopen(log_file, 'a', sys.stderr)
            except:
                pass
    
    run(host=config.WEB_HOST, port=config.WEB_PORT)
