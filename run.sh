#!/bin/bash
echo "========================================"
echo "  AI Study Assistant - Startup Script"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Check if requirements are installed
echo "Checking dependencies..."
if ! pip show Flask > /dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env file and add your SECRET_KEY"
    echo "   (OpenAI API key is optional)"
    echo ""
    read -p "Press enter to continue..."
fi

# Start the application
echo "========================================"
echo "  Starting AI Study Assistant..."
echo "========================================"
echo ""
echo "🚀 Application will be available at:"
echo "   http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
python3 app.py
