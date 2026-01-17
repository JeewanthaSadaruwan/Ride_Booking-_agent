#!/bin/bash

# Quick Start Script for Ride Booking Agent Frontend

echo "=========================================="
echo "🚗 Ride Booking Agent - Quick Start"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: frontend directory not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo -e "${YELLOW}📋 Installation Guide:${NC}"
echo ""
echo "1. Frontend (React):"
echo "   cd frontend"
echo "   npm install"
echo "   npm run dev"
echo ""
echo "2. Backend API (Required):"
echo "   pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt]"
echo "   python backend_api.py"
echo ""
echo "3. Open browser:"
echo "   http://localhost:3000"
echo ""
echo "=========================================="
echo ""

# Ask if user wants to install frontend dependencies
read -p "Install frontend dependencies now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd frontend
    echo ""
    echo -e "${GREEN}📦 Installing dependencies...${NC}"
    npm install
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Installation successful!${NC}"
        echo ""
        echo -e "${YELLOW}To start the frontend:${NC}"
        echo "   npm run dev"
        echo ""
        echo -e "${YELLOW}To start the backend API:${NC}"
        echo "   cd .."
        echo "   python backend_api.py"
    else
        echo -e "${RED}❌ Installation failed${NC}"
        exit 1
    fi
else
    echo ""
    echo "Skipped installation. Run 'cd frontend && npm install' when ready."
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✨ Setup complete!${NC}"
echo ""
echo "📚 Documentation:"
echo "   - SETUP_GUIDE.md (Complete setup instructions)"
echo "   - FRONTEND_SUMMARY.md (Feature overview)"
echo "   - frontend/README.md (Frontend documentation)"
echo "=========================================="
