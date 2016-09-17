#!/bin/bash

if [ ! -d web ]; then cd ..; fi

confirm () {
    # call with a prompt string or use a default
    read -r -p "${1:-Are you sure?} [y/N] " response
    case $response in
        [yY][eE][sS]|[yY]) 
            true
            ;;
        *)
            false
            ;;
    esac
}

sudo pip install -r requirements.txt
./django-manage.py makemigrations web
./django-manage.py migrate

if confirm "Create one super user?"; then
    ./django-manage.py createsuperuser
    echo "Notice: the super user will not have proxy account; you may create later."
fi

echo "Run ./ssland.py to start SSLand"
