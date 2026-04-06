#!/usr/bin/env bash


python manage.py migrate --noinput
python manage.py populate_topics
daphne -b 0.0.0.0 -p 8000 core.asgi:application