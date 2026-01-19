"""Initialize the vehicle dispatch database with tables and mock data."""

import psycopg2
import csv
from pathlib import Path
from config.settings import DATABASE_URL

CSV_DIR = Path(__file__).parent.parent / "csv"


def init_database():
    """Create database tables and populate with data from CSV files."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check and add missing columns (migration)
    def add_column_if_not_exists(table_name, column_name, column_type):
        """Add a column to a table if it doesn't exist."""
        try:
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name=%s AND column_name=%s
            """, (table_name, column_name))
            
            if not cursor.fetchone():
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                conn.commit()
                print(f"✅ Added column '{column_name}' to table '{table_name}'")
        except psycopg2.Error as e:
            # Table might not exist yet, that's okay
            conn.rollback()
            pass
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
    """)
    
    # Create vehicles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            features TEXT,
            current_location TEXT,
            status TEXT NOT NULL,
            license_plate TEXT,
            year INTEGER,
            make TEXT,
            model TEXT
        )
    """)
    
    # Create trips table with user_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            trip_id TEXT PRIMARY KEY,
            user_id TEXT,
            pickup_location TEXT NOT NULL,
            dropoff_location TEXT NOT NULL,
            passenger_count INTEGER NOT NULL,
            requested_time TEXT NOT NULL,
            special_requirements TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Create dispatches table with user_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dispatches (
            dispatch_id TEXT PRIMARY KEY,
            vehicle_id TEXT NOT NULL,
            trip_id TEXT,
            user_id TEXT,
            driver_name TEXT NOT NULL,
            driver_contact TEXT NOT NULL,
            dispatch_time TEXT NOT NULL,
            estimated_arrival TEXT NOT NULL,
            status TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
            FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Create bookings table for complete booking records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            vehicle_id TEXT NOT NULL,
            pickup_location TEXT NOT NULL,
            dropoff_location TEXT NOT NULL,
            pickup_time TEXT NOT NULL,
            passenger_count INTEGER NOT NULL,
            distance_km REAL,
            duration_minutes INTEGER,
            estimated_cost REAL,
            special_requirements TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            calendar_event_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
        )
    """)
    
    # Migration: Add user_id to dispatches if it doesn't exist
    add_column_if_not_exists('dispatches', 'user_id', 'TEXT')
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    vehicle_count = cursor.fetchone()[0]
    
    if vehicle_count > 0:
        print("⚠️  Database already contains data. Clearing existing data...")
        cursor.execute("DELETE FROM vehicles")
        conn.commit()
        print("✅ Existing data cleared.")
    
    # Load vehicles from CSV
    vehicles_csv = CSV_DIR / "vehicles.csv"
    if vehicles_csv.exists():
        with open(vehicles_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            vehicles = []
            for row in reader:
                # Convert semicolon-separated features to comma-separated
                features = row['features'].replace(';', ',')
                vehicles.append((
                    row['vehicle_id'],
                    row['type'],
                    int(row['capacity']),
                    features,
                    row['current_location'],
                    row['status'],
                    row['license_plate'],
                    int(row['year']),
                    row['make'],
                    row['model']
                ))
            
            cursor.executemany("""
                INSERT INTO vehicles (vehicle_id, type, capacity, features, current_location, 
                                    status, license_plate, year, make, model)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, vehicles)
            print(f"   ✅ Loaded {len(vehicles)} vehicles from CSV")
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"\n✅ Database initialized successfully!")


if __name__ == "__main__":
    init_database()
