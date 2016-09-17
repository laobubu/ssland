#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Config Module.
#

DEBUG = True

SITE_NAME = 'SSLand'

SECRET_KEY = 'gxj&%ogdyg*%=814tl*gr4^3#m+3(3z0px*8@acs*o$*61q4_+'
DATABASE_FILENAME = 'db.sqlite3'

# Note: more setting about Django can be configured in `web/settings.py`

MODULES = {
    "Shadowsocks": {
        "executable": "ssserver",
        "config-file": "/etc/shadowsocks.json",
        "manager-address": "/var/run/shadowsocks-manager.sock",
    },

    # # Uncomment these to enable pptpd
    # "PPTP": {
    #     "executable": "service pptpd",
    #     "config-file": "/etc/ppp/chap-secrets"
    # }
}
