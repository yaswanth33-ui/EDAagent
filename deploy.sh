#!/bin/bash

# Production deployment script for EDA Agent

set -e  # Exit on any error

echo "🚀 Starting EDA Agent deployment..."

# Check if .env file exists
if [ ! -f "server/.env" ]; then
    echo "❌ Error: server/.env file not found!"
    echo "Please create a .env file with your environment variables."
    exit 1
fi

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations/setup if needed
echo "🗃️  Setting up database..."
cd server
python -c "from database import Database; db = Database(); print('Database initialized')"

# Start the application
echo "🎯 Starting application..."
if command -v gunicorn &> /dev/null; then
    echo "Starting with Gunicorn..."
    gunicorn --config ../gunicorn.conf.py app:app
else
    echo "Gunicorn not found, starting with Flask development server..."
    python app.py
fi
