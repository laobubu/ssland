#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Config Module.
#

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
