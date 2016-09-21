if   [ -f ../ssland.py ]; then cd .. ; fi

[ ! -f ssland.py ] && { echo "Please run this script on SSLand directory." >&2; exit 1; }
[ ! $EUID = 0 ] && { echo "The root privilege is required. Aborting." >&2; exit 1; }

type python >/dev/null 2>&1 || {
    >&2 echo "Python not found. Aborting."
    exit 1
}
type pip >/dev/null 2>&1 || {
    >&2 echo "Python pip not found. Aborting."
    exit 1
}
python -c "from shadowsocks import daemon" >/dev/null 2>&1 || \
(type ssserver >/dev/null 2>&1 && {
    >&2 echo "Shadowsocks server installed, but not Python version. Aborting."
    exit 1
})

confirm () {
    read -p "${1:-Are you sure?} [y/N] " response
    case $response in
        [yY]*) true;;
        *) false;;
    esac
}

read2 () {
    read -p "$1 [ default: $2 ] = " xi
    echo ${xi:-$2}
}
