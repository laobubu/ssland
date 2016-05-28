#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Config Module.
#

from tempfile import gettempdir

# Your Shadowsocks Path
#  SS_EXEC     - The full command starting ssserver, without "-d start".
#  SS_CONF     - The Shadowsocks config file which SSLand will manage.
SS_EXEC = ["sudo", "ssserver", "-c", "/etc/ss.conf"]
SS_CONF = "/etc/ss.conf"

# User account password hashing salt. Make it complex :)
USER_SALT = "~amADmANiNabLUEbOX!"

# The formular to generate User Shadowsocks Port
user_port = lambda id: 6580 + int(id * 1.5)

# Minimal interval for Shadowsocks restarting
UPDATE_INTERVAL = 30.0

# Directories
USER_ROOT = "user"
WEB_ROOT = "www"
TMP_ROOT = gettempdir() 

# WebServer Config
WEB_HOST = "0.0.0.0"
WEB_PORT = 8080
