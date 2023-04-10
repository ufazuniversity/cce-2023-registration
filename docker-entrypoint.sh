#!/bin/bash

python manage.py collectstatic --noinput &&\
python manage.py makemigrations &&\
python manage.py migrate &&\
python manage loaddata tickets.yaml

gunicorn cce_2023_registration.wsgi:application \
         --bind 0.0.0.0:8000 \
         --workers 4 \
         --access-logfile - \
         --error-logfile - \
         --log-level info \
         --capture-output