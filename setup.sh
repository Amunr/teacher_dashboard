#!/bin/bash

# KEF Teacher Dashboard - Production Setup Script
# This script sets up the application for production deployment

echo "=== KEF Teacher Dashboard - Production Setup ==="

# Check if Python 3.8+ is available
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
if [ -z "$python_version" ]; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated (Linux/Mac)"
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
    echo "✅ Virtual environment activated (Windows)"
else
    echo "❌ Failed to create virtual environment"
    exit 1
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create necessary directories
echo "Creating application directories..."
mkdir -p logs
mkdir -p instance
echo "✅ Directories created"

# Set up environment configuration
if [ ! -f ".env" ]; then
    echo "Setting up environment configuration..."
    cp .env.example .env
    echo "✅ Environment file created from template"
    echo "⚠️  IMPORTANT: Edit .env file and set a secure SECRET_KEY!"
else
    echo "✅ Environment file already exists"
fi

# Database initialization
echo "Initializing database..."
python3 -c "
from app import create_app
app = create_app('production')
with app.app_context():
    app.db_manager.init_database()
    print('✅ Database initialized')
"

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Edit .env file and set a secure SECRET_KEY"
echo "2. Configure your web server (see DEPLOYMENT.md)"
echo "3. Start the application:"
echo "   - Development: python3 run.py"
echo "   - Production: gunicorn --bind 0.0.0.0:5000 run:app"
echo ""