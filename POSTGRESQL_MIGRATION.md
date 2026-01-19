# PostgreSQL Migration & Deployment Guide

## What Changed

Your ride booking agent has been migrated from SQLite to PostgreSQL for deployment compatibility. SQLite is file-based and doesn't work well in cloud deployments where the file system is ephemeral.

## Changes Made

### 1. Database Driver
- **Old**: `sqlite3` (built-in Python library)
- **New**: `psycopg2-binary` (PostgreSQL adapter)

### 2. Configuration
- Added `DATABASE_URL` environment variable in `config/settings.py`
- Created `.env.example` with database configuration template

### 3. Modified Files
- `db/database.py` - All database queries converted to PostgreSQL syntax (`%s` instead of `?`)
- `db/init_db.py` - Table creation and data loading adapted for PostgreSQL
- `auth/auth.py` - Authentication queries converted to PostgreSQL
- `requirements.txt` - Added `psycopg2-binary>=2.9.9`

## Local Development Setup

### Step 1: Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**macOS (using Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Windows:**
Download and install from: https://www.postgresql.org/download/windows/

### Step 2: Create Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE ride_booking;
CREATE USER ride_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ride_booking TO ride_user;
\q
```

### Step 3: Configure Environment

Create a `.env` file in your project root:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```
DATABASE_URL=postgresql://ride_user:your_secure_password@localhost:5432/ride_booking
OPENAI_API_KEY=your_openai_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Initialize Database

```bash
python -m db.init_db
```

This will create all tables and load vehicle data from CSV.

## Production Deployment Options

### Option 1: Railway (Recommended - Easiest)

1. **Create Railway Account**: https://railway.app/

2. **Deploy PostgreSQL**:
   - Click "New Project"
   - Select "Provision PostgreSQL"
   - Railway automatically generates `DATABASE_URL`

3. **Deploy Your Agent**:
   - Create new service from GitHub repo
   - Add environment variables:
     - `DATABASE_URL` (copy from PostgreSQL service)
     - `OPENAI_API_KEY`
     - `GOOGLE_MAPS_API_KEY`
   - Railway will auto-deploy on git push

4. **Initialize Database**:
   ```bash
   # In Railway console or locally with production DB URL
   python -m db.init_db
   ```

### Option 2: Render

1. **Create Render Account**: https://render.com/

2. **Create PostgreSQL Database**:
   - Dashboard → New → PostgreSQL
   - Copy the "Internal Database URL"

3. **Create Web Service**:
   - New → Web Service
   - Connect your GitHub repository
   - Add environment variables:
     - `DATABASE_URL` (Internal Database URL)
     - `OPENAI_API_KEY`
     - `GOOGLE_MAPS_API_KEY`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py` (or your main file)

### Option 3: AWS (More Complex)

**Database: AWS RDS PostgreSQL**
1. Create RDS PostgreSQL instance in AWS Console
2. Note the endpoint, port, username, password, and database name
3. Security group must allow inbound traffic on port 5432

**Application: AWS Elastic Beanstalk / ECS / Lambda**
1. Package your application
2. Set `DATABASE_URL` environment variable:
   ```
   postgresql://username:password@your-rds-endpoint.rds.amazonaws.com:5432/dbname
   ```

### Option 4: Heroku

1. Create Heroku app: `heroku create your-app-name`
2. Add PostgreSQL: `heroku addons:create heroku-postgresql:mini`
3. Heroku automatically sets `DATABASE_URL`
4. Deploy: `git push heroku main`
5. Initialize DB: `heroku run python -m db.init_db`

### Option 5: DigitalOcean App Platform

1. Create Managed PostgreSQL Database
2. Create App from GitHub
3. Link database to app (automatically sets `DATABASE_URL`)
4. Add other environment variables

## Database URL Format

```
postgresql://[username]:[password]@[host]:[port]/[database]
```

**Examples:**
- Local: `postgresql://postgres:password@localhost:5432/ride_booking`
- Railway: `postgresql://postgres:random_pass@containers-us-west-xyz.railway.app:1234/railway`
- Render: `postgresql://user:pass@dpg-xyz.oregon-postgres.render.com/dbname`
- AWS RDS: `postgresql://admin:pass@mydb.abc123.us-east-1.rds.amazonaws.com:5432/ride_booking`

## Anthropic Model Context Protocol (AMP) Deployment

If deploying as an MCP server:

1. **Database must be external** - Your PostgreSQL should run on a separate service
2. **Set DATABASE_URL** - Configure in MCP environment variables
3. **Connection pooling** - Consider using connection pooling for better performance:
   ```python
   from psycopg2 import pool
   db_pool = pool.SimpleConnectionPool(1, 20, DATABASE_URL)
   ```

## Troubleshooting

### Connection Errors

**Error**: `could not connect to server`
- Check DATABASE_URL is correct
- Verify PostgreSQL is running
- Check firewall/security groups allow connection
- For cloud: Ensure you're using the internal/private URL if available

**Error**: `password authentication failed`
- Verify username and password in DATABASE_URL
- Check user has proper permissions

### Table/Column Errors

**Error**: `relation "tablename" does not exist`
- Run database initialization: `python -m db.init_db`

**Error**: `column does not exist`
- Tables may be out of date, drop and recreate:
  ```sql
  DROP DATABASE ride_booking;
  CREATE DATABASE ride_booking;
  ```
- Then re-run `python -m db.init_db`

### Migration from SQLite

If you have existing SQLite data to migrate:

```bash
# Install pgloader
sudo apt install pgloader  # Ubuntu/Debian
brew install pgloader       # macOS

# Convert and load data
pgloader vehicles.db postgresql://user:pass@localhost:5432/ride_booking
```

## Performance Optimization

### 1. Connection Pooling
Use connection pooling for production to avoid creating new connections on every request.

### 2. Indexes
Add indexes for frequently queried columns:
```sql
CREATE INDEX idx_vehicles_status ON vehicles(status);
CREATE INDEX idx_bookings_user_id ON bookings(user_id);
CREATE INDEX idx_bookings_status ON bookings(status);
```

### 3. Environment-Specific Settings
Consider setting different pool sizes based on deployment:
```python
import os
pool_min = int(os.getenv('DB_POOL_MIN', '1'))
pool_max = int(os.getenv('DB_POOL_MAX', '10'))
```

## Security Best Practices

1. **Never commit .env files** - Already in `.gitignore`
2. **Use strong passwords** - Generate with: `openssl rand -base64 32`
3. **SSL/TLS in production** - Most cloud providers enable this by default
4. **Rotate credentials** - Especially after development
5. **Principle of least privilege** - Database user should only have necessary permissions

## Cost Considerations

**Free Tiers Available:**
- **Railway**: $5 free credits monthly, PostgreSQL included
- **Render**: Free PostgreSQL (90 days data retention)
- **Supabase**: 500MB PostgreSQL free forever
- **Neon**: Generous free tier with modern Postgres

**Paid Options** (when scaling):
- Railway: ~$5/month for basic PostgreSQL
- Render: $7/month for persistent PostgreSQL
- AWS RDS: ~$15/month (t3.micro)
- DigitalOcean: $15/month (basic cluster)

## Next Steps

1. ✅ Choose a deployment platform
2. ✅ Set up PostgreSQL database
3. ✅ Configure DATABASE_URL environment variable
4. ✅ Deploy your application
5. ✅ Run database initialization
6. ✅ Test with a booking to verify everything works

## Support

For database-specific issues:
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Railway: https://docs.railway.app/
- Render: https://render.com/docs

For deployment platform issues, consult their respective documentation.
