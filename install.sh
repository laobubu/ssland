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
    EXECCMD_SEDSAFE=$(echo "$EXECCMD" | sed 's/\//\\\//g')
    crontab -l | sed "/$EXECCMD_SEDSAFE/d" >$CRONFILE
    if confirm Use cronjob and traffic statistic; then
        echo "0 0,12 * * * $EXECCMD" >>$CRONFILE
        echo "Notice: the statistic updates at 00:00 and 12:00. Edit this with : crontab -e"
    fi
    cat $CRONFILE | crontab -
    rm -f $CRONFILE
    
    # Remove SSLand old version chain. sorry for that
    { ( iptables -L SSLAND | grep -q "SSLAND (1 reference" ) && iptables -F SSLAND && iptables -X SSLAND; } >/dev/null 2>&1

# WebSevice Install/Uninstall
    RCFILE=/etc/rc.d/rc.local
    RCTMP=/tmp/rclocal.tmp
    EXECCMD="(cd `pwd` && ./cli.py sys update)"
    if confirm Start web server and Shadowsocks when system boots; then
        grep -q "$EXECCMD" $RCFILE || (echo "$EXECCMD" >>$RCFILE)
    else
        EXECCMD_SEDSAFE=$(echo "$EXECCMD" | sed 's/\//\\\//g')
        sed "/$EXECCMD_SEDSAFE/d" $RCFILE >$RCTMP
        cat $RCTMP > $RCFILE
        rm -f $RCTMP
    fi

# End of Wizard    
    echo "Update and start Shadowsocks, SSLand web."
    nohup ./cli.py sys update </dev/null >/dev/null 2>&1 &
    
    echo "Everything shall be ok now. Thanks for using SSLand."
