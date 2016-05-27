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
pip install -r requirements.txt

# Create the first user as the administrator
./cli.py user add

# Modify config.py
# Then you can start web server now.
```

### Config

Read <https://github.com/laobubu/ssland/wiki/Config>

### Use

These Python script are executable. You can run them:

 - `web.py` start the web server, where user can modify their Shadowsocks configuration.
 - `cli.py` add/modify/delete a user. After using this, you **must** restart `web.py` and run `cron.py`
 - `cron.py` update Shadowsocks configration file and restart Shadowsocks.
