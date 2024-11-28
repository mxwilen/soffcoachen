#!/bin/bash -v 
echo "-- UPGRADING PIP --"
pip install --upgrade pip

echo "-- INSTALLING REQUIREMENTS --"
pip install -r requirements.txt
echo "-- DONE INSTALLING --"

export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')

echo "-- UPGRADING DB --"
flask db upgrade
echo "-- DONE UPGRADING --"

echo "-- STARTING APPLICATION --"
echo "Using Python: $(which python)"
echo "Python version: $(python --version)"
gunicorn --bind=0.0.0.0:8000 --timeout 120 app:app
