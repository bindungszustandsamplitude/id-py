#!/bin/sh

cp id_py/settings_template.py id_py/settings.py
python3 manage.py makemigrations id_py
python3 manage.py migrate