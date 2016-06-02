#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Config Module.
#

from tempfile import gettempdir

# Your Shadowsocks Path
#  SS_EXEC     - The full command starting ssserver, without "-d start".
#  SS_CONF     - The Shadowsocks config file which SSLand will manage.
SS_EXEC = ["ssserver", "-c", "/etc/ss.conf"]
SS_CONF = "/etc/ss.conf"

# User Configuration
#  USER_ADMIN  - Administrator user ID. Ususally the first user, whose id is 1.
#  USER_SALT   - Account password hashing salt. Make it complex :)
USER_ADMIN = 1
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
