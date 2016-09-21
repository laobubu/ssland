#!/bin/bash

source common.sh

if grep -Ps 'WIZARD_GENERATED' config.py; then
    echo "SSLand setup script was executed before."
    confirm "Still continue?" || exit 0
else
    # Generate random salt
    sed config.py -r -i -e "s|^SECRET_KEY.+$|SECRET_KEY = '`openssl rand -base64 32`'|"
fi

echo "[ALLOWED_HOSTS]"

if grep -Ps 'ALLOWED_HOSTS\s*=\s*\[\s*\]' web/settings.py; then
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

SITE_NAME = $(read2 "Site name" "SSLand" )
HTTP_PORT = $(read2 "HTTP Port" "8000" )

sed config.py -r -i                                             \
    -e "s|^SITE_NAME.+$|SITE_NAME = '${SITE_NAME}'|"            \
    -e "s|^HTTP_PORT.+$|HTTP_PORT = ${HTTP_PORT}|"              \
    -e "s|^DEBUG = True|DEBUG = False|"                         \
    -e "7a# WIZARD_GENERATED = '`date`'"

echo "[DJANGO]"

./tools/init_django.sh

[ -d .git ] && git commit -am "Finish the setup wizard."

echo "[FINISHED]"

echo "To start SSLand daemon, please execute  ./ssland.py -d start"
confirm "Start now?" && ./ssland.py -d restart
