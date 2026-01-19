#!/bin/bash

echo "🔍 Supabase Connection String Format"
echo "===================================="
echo ""
echo "Your connection string should look like this:"
echo ""
echo "postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres"
echo ""
echo "Example:"
echo "postgresql://postgres.abcdefghijk:MySecurePass123@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
echo ""
echo "Where to find each part:"
echo "  - PROJECT-REF: Your unique project identifier (found in URL)"
echo "  - PASSWORD: Database password you created"
echo "  - REGION: Your project region (e.g., us-east-1)"
echo ""
echo "Still can't find it? Let's build it manually!"
echo ""
read -p "What's your Supabase project URL? (copy from browser): " PROJECT_URL

if [[ $PROJECT_URL =~ supabase\.com/project/([^/]+) ]]; then
    PROJECT_REF="${BASH_REMATCH[1]}"
    echo ""
    echo "✅ Found project reference: $PROJECT_REF"
    echo ""
    read -sp "Enter your database password: " DB_PASSWORD
    echo ""
    echo ""
    echo "📝 Your DATABASE_URL is:"
    echo ""
    echo "DATABASE_URL=postgresql://postgres.$PROJECT_REF:$DB_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    echo ""
    read -p "Does this look right? (y/n): " CONFIRM
    
    if [ "$CONFIRM" = "y" ]; then
        DATABASE_URL="postgresql://postgres.$PROJECT_REF:$DB_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
        
        # Backup and update .env
        cp .env .env.backup 2>/dev/null
        grep -v "DATABASE_URL=" .env > .env.tmp 2>/dev/null || echo "" > .env.tmp
        mv .env.tmp .env
        echo "" >> .env
        echo "# Supabase PostgreSQL Database" >> .env
        echo "DATABASE_URL=$DATABASE_URL" >> .env
        
        echo "✅ .env updated!"
        echo ""
        echo "🏗️  Testing connection and initializing database..."
        python3 -m db.init_db
    fi
else
    echo "❌ Could not extract project reference from URL"
    echo "Please copy the full Supabase dashboard URL from your browser"
fi
