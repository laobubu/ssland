#!/bin/sh
# Linux Install script

[ ! $EUID = 0 ] &&   { echo "The root privilege is required. Aborting." >&2;   exit 1; }
type python   >/dev/null 2>&1 || { echo "Python not found. Aborting." >&2;     exit 1; }
type pip      >/dev/null 2>&1 || { echo "Python pip not found. Aborting." >&2; exit 1; }
type ssserver >/dev/null 2>&1 || { pip install shadowsocks; }

pip install -r requirements.txt

if grep -q WIZARD_GENERATED config.py; then

    echo "Found WIZARD_GENERATED mark. Skipping wizard."

else

    default_cfg=/etc/ss.conf
    read -p "Shadowsocks config file [ default: $default_cfg ] = " cfg
    cfg=${cfg:-$default_cfg}

    [ -f $cfg ] && echo "WARNING: File exists." || \
        echo "The encrypt method is aes-256-cfb. You can change this later by editing $cfg"

    read -p "User port formular [ default: 6580+id ] = " port
    port=${port:-6580+id}
    
    read -p "SSLand web port [ default: 8080 ] = " wport
    wport=${wport:-8080}

    sed config.py -r -i                                             \
        -e "s|^USER_SALT.+$|USER_SALT='`openssl rand -base64 16`'|" \
        -e "s|^WEB_PORT .+$|WEB_PORT=${wport}|"                     \
        -e "s|^user_port.+$|user_port=lambda id:${port}|"           \
        -e "s|/etc/ss.conf|${cfg}|"                                 \
        -e "7a# WIZARD_GENERATED = '`date`'"

    echo "Creating the first user, which is also the administrator."
    ./cli.py user add

    git commit -am "Custom configuration snapshot" >/dev/null 2>&1

fi

confirm () {
    while true; do
        read -p "$*? (yes/no): " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

# CRONJOB Install/Uninstall
    CRONFILE=/tmp/ssland.cron.tmp
    EXECCMD="cd `pwd` && ./cron.py -s"
    crontab -l | sed "/$EXECCMD/d" >$CRONFILE
    if confirm Use cronjob and traffic statistic; then
        echo "0 0 * * * $EXECCMD" >>$CRONFILE
    fi
    cat $CRONFILE | crontab -
    rm -f $CRONFILE

# WebSevice Install/Uninstall
    RCFILE=/etc/rc.local
    EXECCMD="(cd `pwd` && ./web.py -d start)"
    if confirm Start web server when system boots; then
        grep -q "$EXECCMD" $RCFILE || (echo "$EXECCMD" >>$RCFILE)
    else
        sed -i "/$EXECCMD/d" $RCFILE
    fi

# End of Wizard    
    echo "Update and start Shadowsocks, SSLand web."
    nohup ./cli.py sys update </dev/null >/dev/null 2>&1 &
    
    echo "Everything shall be ok now. Thanks for using SSLand."
