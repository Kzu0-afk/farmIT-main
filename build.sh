#!/bin/bash
# Vercel build script for Django
# This script runs migrations and collects static files

set -e  # Exit on error

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running database migrations..."
python farmIT/manage.py migrate --noinput

echo "Collecting static files..."
python farmIT/manage.py collectstatic --noinput

echo "Build completed successfully!"

