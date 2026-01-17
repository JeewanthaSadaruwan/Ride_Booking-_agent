#!/bin/bash

# Ride Booking Agent - Frontend Setup Script
# This script sets up and runs the React frontend

echo "🚗 Ride Booking Agent - Frontend Setup"
echo "======================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "✓ Node.js version: $(node -v)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✓ npm version: $(npm -v)"

# Navigate to frontend directory
cd "$(dirname "$0")"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the development server, run:"
echo "   npm run dev"
echo ""
echo "📝 To build for production, run:"
echo "   npm run build"
echo ""
echo "⚙️  Make sure the backend server is running on http://localhost:8000"
echo ""
