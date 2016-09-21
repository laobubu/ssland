# SSLand

A lightweight Shadowsocks multi-user web-frontend.

## Features

 - **Web Panel**: Manage Shadowsocks users, on the web.
 - **Statistic**: Use Shadowsocks manager API to stats.
 - **Quota**: Auto suspend accounts when they excceed the quota.

## How to Use

**Install**: <https://github.com/laobubu/ssland/wiki/Install>

**Config**: <https://github.com/laobubu/ssland/wiki/Config>

**Upgrade**: <https://github.com/laobubu/ssland/wiki/Install#upgrading>

### Use

These Python script are executable. You can run them:

 - `django-manager.py` DJango util. Debug only.
 - `ssland.py` Main system, the web server, Shadowsocks manager and account manager. 

Usually all you need is `./ssland.py -d start`
