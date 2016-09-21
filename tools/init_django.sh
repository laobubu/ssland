#!/bin/bash

if [ ! -f ssland.py ] && [ -f ../ssland.py ]; then cd ..

pip install -r requirements.txt
./django-manage.py makemigrations web
./django-manage.py migrate

if confirm "Create one super user?"; then
    ./django-manage.py createsuperuser
    echo "Notice: the super user will not have proxy account; you may create later."
fi
