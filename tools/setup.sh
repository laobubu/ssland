#!/bin/bash

echo "Starting SSLand Setup..."

source $(dirname "$0")/common.sh

if grep -P 'WIZARD_GENERATED' config.py; then
    echo "SSLand setup script was executed before."
    confirm "Still continue?" || exit 0
else
    # Generate random salt
    RAND_KEY="$(2>/dev/null openssl rand -base64 32)"
    sed config.py -r -i -e "s|^SECRET_KEY.+$|SECRET_KEY = '${RAND_KEY}'|"
fi

echo "[ALLOWED_HOSTS]"

if grep -Pq 'ALLOWED_HOSTS\s*=\s*\[\s*\]' web/settings.py; then
    echo "You must set the allowed hostname (domain or IP)."
    echo "If you don't want to filter (not recommended), just press Enter key."
    read -r -p "Hostname: " domain
    sed web/settings.py -i -e "/ALLOWED_HOSTS/{aALLOWED_HOSTS = [\n    '${domain:-*}',\n]
    d}"
    echo "You may edit web/settings.py file to add more"
else
    echo "ALLOWED_HOSTS is modified. Skipping."
fi

echo "[SITE_CONFIG]"

SITE_NAME="$(read2 'Site name' 'SSLand' )"
HTTP_PORT="$(read2 'HTTP Port' '8000' )"

sed config.py -r -i                                             \
    -e "s|^SITE_NAME.+$|SITE_NAME = '${SITE_NAME}'|"            \
    -e "s|^HTTP_PORT.+$|HTTP_PORT = ${HTTP_PORT}|"              \
    -e "s|^DEBUG = True|DEBUG = False|"                         \
    -e "7a# WIZARD_GENERATED = '`date`'"

echo "[SHADOWSOCKS]"

SS_CFG=`grep -Po 'config-file": "([^"]+)' service/Shadowsocks.py`
SS_CFG=${SS_CFG:15}
touch $SS_CFG && {
    echo "Using $SS_CFG as ssserver configuration."
} || {
    SS_CFG2="ssserver.json"
    SRV_IPS=`ifconfig | awk '/inet6? (\S+)/{ gsub(/^[^\:]+\:\s*/,""); gsub(/\//," "); print $1 }'`
    SRV_IP=`echo $SRV_IPS | awk '{print $1}'`
    echo "File $SS_CFG not accessible."
    echo "I can generate $SS_CFG2 and use it now, otherwise, you must use create $SS_CFG manually."
    confirm "Create $SS_CFG2 and continue ? (recommended)" && {
        echo "Your server has these IP address: "
        for ip in $SRV_IPS ; do echo " + $ip"; done
        echo "Please choose one as the Shadowsocks server IP."
        SRV_IP=`read2 'Server IP' $SRV_IP`
        
        >$SS_CFG2 cat <<EOF
{
    "server": "$SRV_IP",
    "port_password": {},
    "timeout": 300,
    "method": "aes-256-cfb"
}
EOF
        echo "$SS_CFG2 is generated."
        [ -d .git ] && (2>&1 type git) && git add $SS_CFG2

        sed service/Shadowsocks.py -i -e "s|$SS_CFG|$SS_CFG2|"
        echo "File service/Shadowsocks.py is updated."
    } || echo "[!!] You shall create $SS_CFG manually."
}

echo "[DJANGO]"

./tools/init_django.sh

[ -d .git ] && (2>&1 type git) && git commit -am "Finish the setup wizard." >/dev/null 

echo "[FINISHED]"

echo "To start SSLand daemon, please execute  ./ssland.py -d start"
if confirm "Start now?"; then 
    ./ssland.py -d stop >/dev/null 2>&1 #not necessary
    
    ./ssland.py -d start
fi
