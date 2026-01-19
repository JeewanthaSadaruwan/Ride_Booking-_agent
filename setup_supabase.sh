#!/bin/bash

echo "🔧 Supabase PostgreSQL Setup"
echo "================================"
echo ""
echo "Go to your Supabase dashboard and:"
echo "1. Click 'Project Settings' (⚙️ icon)"
echo "2. Click 'Database'"
echo "3. Find 'Connection String' section"
echo "4. Copy the URI format connection string"
echo "5. Replace [YOUR-PASSWORD] with your database password"
echo ""
read -p "Paste your Supabase DATABASE_URL here: " DATABASE_URL

if [ -z "$DATABASE_URL" ]; then
    echo "❌ No DATABASE_URL provided"
    exit 1
fi

echo ""
echo "📝 Updating .env file..."

# Backup existing .env
cp .env .env.backup

# Remove old DATABASE_URL if exists
grep -v "DATABASE_URL=" .env > .env.tmp 2>/dev/null || echo "" > .env.tmp
mv .env.tmp .env

# Add new DATABASE_URL
echo "" >> .env
echo "# Supabase PostgreSQL Database" >> .env
echo "DATABASE_URL=$DATABASE_URL" >> .env

echo "✅ .env updated!"
echo ""
echo "🏗️  Initializing database tables..."
python3 -m db.init_db

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Success! Your database is ready!"
    echo ""
    echo "Next steps:"
    echo "1. Start backend: python3 backend_api.py"
    echo "2. Start frontend: cd frontend && npm run dev"
    echo ""
    echo "Your app will now use Supabase PostgreSQL!"
else
    echo ""
    echo "❌ Database initialization failed"
    echo "Check your DATABASE_URL and try again"
    exit 1
fi
