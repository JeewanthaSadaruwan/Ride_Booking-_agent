#!/bin/bash

# Ride Booking Agent - Startup Script
# This script runs the Streamlit application

echo "🚗 Starting Ride Booking Agent..."
echo "=================================="
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
fi

# Check if requirements are installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Installing requirements..."
    pip install -r requirements.txt
fi

# Set environment variables for better performance
export STRANDS_TOOL_CONSOLE_MODE="enabled"

# Run the application
echo "🚀 Launching Streamlit app..."
echo "📍 App will open at: http://localhost:8501"
echo ""
streamlit run app_complete.py --server.port 8501 --server.address localhost

