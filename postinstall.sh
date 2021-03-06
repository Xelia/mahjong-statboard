#!/bin/bash

cd server &&
export PIPENV_VENV_IN_PROJECT=1 &&
pipenv install &&
export DJANGO_SETTINGS_MODULE=mahjong_statboard.settings_prod &&
pipenv run python manage.py migrate &&
pipenv run python manage.py collectstatic --noinput &&

cd ../client &&
npm install &&
npm run build &&
cd .. &&

sudo supervisorctl restart mahjong_statboard
