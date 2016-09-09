#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Shadowsocks service
#

from __future__ import absolute_import
import base64
from core.util import get_stdout, encodeURIComponent

config = {
    "executable": "ssserver",
    "config-file": "/etc/shadowsocks.json",
    "manager-address": "/var/run/shadowsocks-manager.sock",
    "method": "aes-256-cfb",
    "server": "127.0.0.1"
}

executable = ('ssserver', )

def init(_config):
    global executable
    config.update(_config)
    executable = tuple(config["executable"].split(' ')) + (
        '-c', config["config-file"], 
        '--manager-address', config['manager-address']
    )
    
def html(account_config):
    ssurl = '%s:%s@%s:%d' % (
        config['method'],
        account_config['sskey'],
        config['server'],
        account_config['port']
    )
    imgurl = '/qr.svg?data=%s' % encodeURIComponent('ss://' + base64.b64encode(ssurl))
    return '\n'.join([
        '<a href="%s" target="_blank"><img src="%s" class="float"></a>' % (imgurl,imgurl),
        '<table class="strip">',
        '  <tr><th>server</th>      <td>%s</td></tr>' % config['server']          ,
        '  <tr><th>server_port</th> <td>%d</td></tr>' % account_config['port']    ,
        '  <tr><th>password</th>    <td>%s</td></tr>' % account_config['sskey']   ,
        '  <tr><th>method</th>      <td>%s</td></tr>' % config['method']          , 
        '</table>',
    ])


from django import forms
class UserForm(forms.Form):
    sskey = forms.CharField(label='Password', max_length=100)

def start():
    get_stdout(executable + ('-d', 'restart'))

def stop():
    get_stdout(executable + ('-d', 'stop'))
