#!/bin/bash -e
[ ! -d ssland_env ] && virtualenv ssland_env
EPATH="$(dirname $0)"
>.tmprc cat <<EOF
. $EPATH/ssland_env/bin/activate
rm $EPATH/.tmprc
cd $EPATH/..
EOF
chmod +x .tmprc
bash --rcfile .tmprc 
