# Quick Reference - PostgreSQL Commands

## Local Development Setup

### 1. Quick Start (Automated)
```bash
./setup_postgresql.sh
```

### 2. Manual Setup

**Create Database:**
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# In psql:
CREATE DATABASE ride_booking;
CREATE USER ride_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ride_booking TO ride_user;
\q
```

**Configure Environment:**
```bash
# Create .env file
echo "DATABASE_URL=postgresql://ride_user:secure_password@localhost:5432/ride_booking" > .env
echo "OPENAI_API_KEY=your_key_here" >> .env
echo "GOOGLE_MAPS_API_KEY=your_key_here" >> .env
```

**Initialize Tables:**
```bash
python -m db.init_db
```

---

## Useful PostgreSQL Commands

### Connection
```bash
# Connect to database
psql -U ride_user -d ride_booking

# Or with password
PGPASSWORD=password psql -U ride_user -d ride_booking
```

### Database Management
```sql
-- List all databases
\l

-- Connect to database
\c ride_booking

-- List all tables
\dt

-- Describe table structure
\d users
\d vehicles
\d bookings

-- Show table sizes
\dt+

-- Count records
SELECT COUNT(*) FROM vehicles;
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM bookings;
```

### Querying Data
```sql
-- View all vehicles
SELECT * FROM vehicles LIMIT 10;

-- Check available vehicles
SELECT vehicle_id, make, model, type, current_location 
FROM vehicles 
WHERE status = 'available';

-- View recent bookings
SELECT booking_id, pickup_location, dropoff_location, status, created_at
FROM bookings 
ORDER BY created_at DESC 
LIMIT 10;

-- User statistics
SELECT 
    u.full_name,
    COUNT(b.booking_id) as total_bookings,
    SUM(b.estimated_cost) as total_spent
FROM users u
LEFT JOIN bookings b ON u.user_id = b.user_id
GROUP BY u.user_id, u.full_name;
```

### Maintenance
```sql
-- Reset database (DELETE ALL DATA!)
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS dispatches CASCADE;
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS vehicles CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Then reinitialize:
-- Exit psql and run: python -m db.init_db

-- Vacuum database (optimize)
VACUUM ANALYZE;

-- Check database size
SELECT pg_size_pretty(pg_database_size('ride_booking'));
```

### Backup & Restore
```bash
# Backup database
pg_dump -U ride_user -d ride_booking > backup.sql

# Backup with compression
pg_dump -U ride_user -d ride_booking | gzip > backup.sql.gz

# Restore database
psql -U ride_user -d ride_booking < backup.sql

# Restore from compressed backup
gunzip -c backup.sql.gz | psql -U ride_user -d ride_booking
```

---

## Environment Variables

### Local Development
```env
DATABASE_URL=postgresql://ride_user:password@localhost:5432/ride_booking
```

### Production Examples

**Railway:**
```env
DATABASE_URL=postgresql://postgres:xyzABC123@containers-us-west-123.railway.app:5432/railway
```

**Render:**
```env
DATABASE_URL=postgresql://user:pass@dpg-abc123.oregon-postgres.render.com/dbname
```

**AWS RDS:**
```env
DATABASE_URL=postgresql://admin:password@mydb.abc123.us-east-1.rds.amazonaws.com:5432/ride_booking
```

**Heroku:**
```env
DATABASE_URL=postgres://user:pass@ec2-xxx.compute-1.amazonaws.com:5432/dbname
```

---

## Troubleshooting

### Can't Connect
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Check if listening
sudo netstat -plunt | grep postgres
```

### Permission Issues
```sql
-- Grant all permissions to user
GRANT ALL PRIVILEGES ON DATABASE ride_booking TO ride_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ride_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ride_user;
```

### Reset Password
```sql
-- As postgres user
ALTER USER ride_user WITH PASSWORD 'new_password';
```

### View Active Connections
```sql
SELECT pid, usename, application_name, client_addr, state
FROM pg_stat_activity
WHERE datname = 'ride_booking';
```

### Kill Stuck Connections
```sql
-- Find PIDs from above query, then:
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'ride_booking' AND pid <> pg_backend_pid();
```

---

## Python Database Operations

### Test Connection
```python
import psycopg2
from config.settings import DATABASE_URL

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Connected to PostgreSQL!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Initialize Database
```bash
python -m db.init_db
```

### Check Tables
```python
import psycopg2
from config.settings import DATABASE_URL

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
""")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])
cursor.close()
conn.close()
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] PostgreSQL database created on cloud platform
- [ ] DATABASE_URL obtained
- [ ] All environment variables configured
- [ ] Code pushed to repository

### Deployment
- [ ] Application deployed to cloud platform
- [ ] Environment variables set in platform settings
- [ ] Database connection tested
- [ ] Run `python -m db.init_db` in production console

### Post-Deployment
- [ ] Test user signup/login
- [ ] Test vehicle search
- [ ] Test booking creation
- [ ] Test calendar integration
- [ ] Monitor logs for errors

---

## Performance Tips

### Connection Pooling (for production)
```python
from psycopg2 import pool

# Create connection pool
db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL
)

# Get connection from pool
def get_db_connection():
    return db_pool.getconn()

# Return connection to pool
def close_db_connection(conn):
    db_pool.putconn(conn)
```

### Indexes (add after deployment)
```sql
-- Speed up common queries
CREATE INDEX idx_vehicles_status ON vehicles(status);
CREATE INDEX idx_vehicles_location ON vehicles(current_location);
CREATE INDEX idx_bookings_user_id ON bookings(user_id);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_created_at ON bookings(created_at DESC);
```

---

## Support Resources

- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **psycopg2 Docs**: https://www.psycopg.org/docs/
- **Railway Docs**: https://docs.railway.app/
- **Render Docs**: https://render.com/docs/databases

---

**Quick help**: For detailed deployment instructions, see [POSTGRESQL_MIGRATION.md](POSTGRESQL_MIGRATION.md)
