#!/bin/bash

# Quick Setup Script for PostgreSQL Local Development

echo "🚀 Setting up PostgreSQL for Ride Booking Agent..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed."
    echo "Please install PostgreSQL first:"
    echo "  Ubuntu/Debian: sudo apt install postgresql"
    echo "  macOS: brew install postgresql@15"
    exit 1
fi

echo "✅ PostgreSQL found"

# Get database credentials
read -p "Enter PostgreSQL username (default: postgres): " DB_USER
DB_USER=${DB_USER:-postgres}

read -sp "Enter PostgreSQL password: " DB_PASS
echo

read -p "Enter database name (default: ride_booking): " DB_NAME
DB_NAME=${DB_NAME:-ride_booking}

read -p "Enter host (default: localhost): " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "Enter port (default: 5432): " DB_PORT
DB_PORT=${DB_PORT:-5432}

# Create .env file
echo "📝 Creating .env file..."
cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# API Keys (replace with your actual keys)
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
EOF

echo "✅ .env file created"

# Try to create database
echo "🗄️  Creating database..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -tc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" | grep -q 1 || \
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE ${DB_NAME}"

if [ $? -eq 0 ]; then
    echo "✅ Database created or already exists"
else
    echo "⚠️  Could not create database automatically"
    echo "Please create it manually:"
    echo "  psql -U $DB_USER"
    echo "  CREATE DATABASE ${DB_NAME};"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Initialize database
echo "🏗️  Initializing database tables..."
python -m db.init_db

if [ $? -eq 0 ]; then
    echo "✅ Database initialized successfully!"
    echo ""
    echo "🎉 Setup complete! You can now run your application."
    echo ""
    echo "Next steps:"
    echo "1. Edit .env and add your API keys"
    echo "2. Run your application: python app.py"
else
    echo "❌ Failed to initialize database"
    exit 1
fi
