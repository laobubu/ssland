#!/bin/sh
# Linux Install script

[ ! $EUID = 0 ] &&   { echo "The root privilege is required. Aborting." >&2;   exit 1; }
type python   >/dev/null 2>&1 || { echo "Python not found. Aborting." >&2;     exit 1; }
type pip      >/dev/null 2>&1 || { echo "Python pip not found. Aborting." >&2; exit 1; }
type ssserver >/dev/null 2>&1 || { pip install shadowsocks; }



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


read2 () {
    read -p "$1 [ default: $2 ] = " xi
    echo ${xi:-$2}
}


pip install -r requirements.txt

if grep -q WIZARD_GENERATED config.py; then

    echo "Found WIZARD_GENERATED mark. Skipping wizard."

else

    cfg=$(read2   "Shadowsocks config file" "/etc/ss.conf"  )

    if [ ! -f $cfg ] || confirm "File already exists. Delete and create again"; then
        ssip=`ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p'`
        ssip=$(read2 "Server IP"            "$ssip"         )
        ssm=$( read2 "Cipher method"        "aes-256-cfb"   )
        ssto=$(read2 "Timeout"              "300"           )
        echo "You can change this later, by editing $cfg"
        echo "{\"server\": \"$ssip\", \"port_password\": {}, \"timeout\": $ssto, \"method\": \"$ssm\"}"  >$cfg
    fi
    
    port=$( read2 "User port formular"      "6580+id"      )
    wport=$(read2 "SSLand web port"         "8080"         )

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
    RCFILE=/etc/rc.local
    RCTMP=/tmp/rclocal.tmp
    EXECCMD="(cd `pwd` && ./cli.py sys init)"
    EXECCMD_SEDSAFE=$(echo "$EXECCMD" | sed 's/\//\\\//g')
    cat $RCFILE > $RCTMP
    if confirm Start web server and Shadowsocks when system boots; then
        sed -i "/exit\\b/i$EXECCMD" $RCTMP
        grep -q "$EXECCMD" $RCTMP || (echo "$EXECCMD" >>$RCTMP)
    else
        sed -i "/$EXECCMD_SEDSAFE/d" $RCTMP
    fi
    cat $RCTMP > $RCFILE
    rm -f $RCTMP

# End of Wizard    
    echo "Update and start Shadowsocks, SSLand web."
    nohup ./cli.py sys update </dev/null >/dev/null 2>&1 &
    
    echo "Everything shall be ok now. Thanks for using SSLand."
