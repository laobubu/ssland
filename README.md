# SSLand

A lightweight Shadowsocks multi-user web-frontend.

## Features

 - **Lightweight**: No heavy frameworks! Only requires Python and `bottle.py`
 - **Web Panel**: Manage Shadowsocks users, on the web.
 - **Statistic**: Use `iptables` to stats users' traffic.
 - **Limiter**: Auto suspend users when they excceed the limitation.

## How to Use

### Install

```bash
git clone https://github.com/laobubu/ssland.git
cd ssland
./install.sh
```

### Upgrade

```bash
git pull
./cli.py sys update
```

### Config

Read <https://github.com/laobubu/ssland/wiki/Config>

### Use

These Python script are executable. You can run them:

 - `web.py` start the SSLand web server.
 - `cli.py` the command-line interface. Don't forget `./cli.py sys update` after making modification.
 - `cron.py` update statistic, account status and Shadowsocks config.
