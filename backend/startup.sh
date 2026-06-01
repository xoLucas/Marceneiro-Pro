#!/bin/sh
set -e
python manage.py migrate --settings=marcenaria.settings
python manage.py seed_dados --settings=marcenaria.settings
gunicorn marcenaria.wsgi:application --bind 0.0.0.0:$PORT
