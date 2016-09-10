#!/bin/bash

if [ ! -d web ]; then cd ..; fi

sudo pip install -r requirements.txt
./django-manage.py makemigrations web
./django-manage.py migrate
