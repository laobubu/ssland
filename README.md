# SSLand

A lightweight Shadowsocks multi-user web-frontend.

## Features

 - **Lightweight**: No heavy frameworks! Only requires Python2.7 and `bottle.py`
 - **User**: Update the shadowsocks key on the web.

## How to Use

### Install

```bash
#if you don't have shadowsocks
sudo pip install shadowsocks

git clone https://github.com/laobubu/ssland.git
cd ssland
./install.sh
```

### Config

Read <https://github.com/laobubu/ssland/wiki/Config>

### Use

These Python script are executable. You can run them:

 - `web.py` start the web server, where user can modify their Shadowsocks configuration.
 - `cli.py` add/modify/delete a user. Don't forget `./cli.py sys update` after making modification.
 - `cron.py` update statistic, account status and Shadowsocks config.
