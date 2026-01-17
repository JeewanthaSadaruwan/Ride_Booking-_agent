"""Database helper functions for vehicle dispatch system."""

import sqlite3
from typing import List, Dict, Optional

DB_PATH = "vehicles.db"


def get_db_connection():
    """Get a connection to the database."""
    return sqlite3.connect(DB_PATH)


def get_available_vehicles(location: str = "", vehicle_type: str = "") -> List[Dict]:
    """
    Get list of available vehicles from database.
    
    Args:
        location: Optional location filter
        vehicle_type: Optional vehicle type filter
        
    Returns:
        List of vehicle dictionaries
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM vehicles WHERE status = 'available'"
    params = []
    
    if location:
        query += " AND current_location LIKE ?"
        params.append(f"%{location}%")
    
    if vehicle_type:
        query += " AND type = ?"
        params.append(vehicle_type)
    
    cursor.execute(query, params)
    vehicles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return vehicles


def get_vehicle_by_id(vehicle_id: str) -> Optional[Dict]:
    """Get a specific vehicle by ID."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def create_trip(pickup: str, dropoff: str, passengers: int, 
                requested_time: str, requirements: str = "", user_id: str = None) -> str:
    """Create a new trip in the database."""
    import uuid
    from datetime import datetime
    
    trip_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO trips (trip_id, user_id, pickup_location, dropoff_location, 
                          passenger_count, requested_time, special_requirements, 
                          status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
    """, (trip_id, user_id, pickup, dropoff, passengers, requested_time, 
          requirements, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()
    
    return trip_id


def create_dispatch(vehicle_id: str, trip_id: str, driver_name: str,
                   driver_contact: str, estimated_arrival: str,
                   pickup_location: str = "", dropoff_location: str = "",
                   passenger_count: int = 1, special_requirements: str = "",
                   user_id: str = None) -> str:
    """Create a dispatch record (trip_id is optional for dynamic bookings)."""
    import uuid
    from datetime import datetime
    
    dispatch_id = f"D-{uuid.uuid4().hex[:8]}"
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert dispatch with route details and user_id
    cursor.execute("""
        INSERT INTO dispatches (dispatch_id, vehicle_id, trip_id, user_id, driver_name,
                               driver_contact, dispatch_time, status, estimated_arrival)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'dispatched', ?)
    """, (dispatch_id, vehicle_id, trip_id, user_id, driver_name, driver_contact,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S"), estimated_arrival))
    
    # Update vehicle status to on_trip
    cursor.execute("""
        UPDATE vehicles SET status = 'on_trip' WHERE vehicle_id = ?
    """, (vehicle_id,))
    
    # Update trip status only if trip_id exists (backward compatibility)
    if trip_id:
        cursor.execute("""
            UPDATE trips SET status = 'dispatched' WHERE trip_id = ?
        """, (trip_id,))
    
    conn.commit()
    conn.close()
    
    return dispatch_id


def get_dispatch_by_id(dispatch_id: str) -> Optional[Dict]:
    """Get dispatch details by ID."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.*, v.make, v.model, v.license_plate, t.pickup_location, t.dropoff_location
        FROM dispatches d
        LEFT JOIN vehicles v ON d.vehicle_id = v.vehicle_id
        LEFT JOIN trips t ON d.trip_id = t.trip_id
        WHERE d.dispatch_id = ?
    """, (dispatch_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def get_all_dispatches(status: str = None) -> List[Dict]:
    """Get all dispatches, optionally filtered by status."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT d.*, v.make, v.model, v.license_plate, v.type,
               t.pickup_location, t.dropoff_location, t.passenger_count
        FROM dispatches d
        LEFT JOIN vehicles v ON d.vehicle_id = v.vehicle_id
        LEFT JOIN trips t ON d.trip_id = t.trip_id
    """
    
    if status:
        query += " WHERE d.status = ?"
        cursor.execute(query, (status,))
    else:
        cursor.execute(query)
    
    dispatches = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return dispatches


def create_booking(user_id: str, vehicle_id: str, pickup_location: str, 
                   dropoff_location: str, pickup_time: str, passenger_count: int,
                   distance_km: float = None, duration_minutes: int = None,
                   estimated_cost: float = None, special_requirements: str = "",
                   calendar_event_id: str = None) -> str:
    """
    Create a complete booking record.
    
    Args:
        user_id: User's ID
        vehicle_id: Vehicle ID
        pickup_location: Pickup address
        dropoff_location: Dropoff address
        pickup_time: Scheduled pickup time
        passenger_count: Number of passengers
        distance_km: Trip distance
        duration_minutes: Estimated duration
        estimated_cost: Estimated cost
        special_requirements: Special requirements
        calendar_event_id: Google Calendar event ID
        
    Returns:
        Booking ID
    """
    import uuid
    from datetime import datetime
    
    booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO bookings (booking_id, user_id, vehicle_id, pickup_location,
                            dropoff_location, pickup_time, passenger_count,
                            distance_km, duration_minutes, estimated_cost,
                            special_requirements, status, created_at, calendar_event_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'confirmed', ?, ?)
    """, (booking_id, user_id, vehicle_id, pickup_location, dropoff_location,
          pickup_time, passenger_count, distance_km, duration_minutes,
          estimated_cost, special_requirements, 
          datetime.now().strftime("%Y-%m-%d %H:%M:%S"), calendar_event_id))
    
    conn.commit()
    conn.close()
    
    return booking_id


def get_user_bookings(user_id: str, status: str = None, limit: int = 10) -> List[Dict]:
    """
    Get user's booking history.
    
    Args:
        user_id: User's ID
        status: Optional status filter (confirmed, cancelled, completed)
        limit: Maximum number of bookings to return
        
    Returns:
        List of booking dictionaries
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT b.*, v.make, v.model, v.type, v.license_plate
        FROM bookings b
        LEFT JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        WHERE b.user_id = ?
    """
    
    params = [user_id]
    
    if status:
        query += " AND b.status = ?"
        params.append(status)
    
    query += " ORDER BY b.created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    bookings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return bookings


def get_booking_by_id(booking_id: str) -> Optional[Dict]:
    """Get a specific booking by ID."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT b.*, v.make, v.model, v.type, v.license_plate, v.features,
               u.full_name, u.email, u.phone
        FROM bookings b
        LEFT JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        LEFT JOIN users u ON b.user_id = u.user_id
        WHERE b.booking_id = ?
    """, (booking_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def cancel_booking(booking_id: str) -> bool:
    """Cancel a booking."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE bookings SET status = 'cancelled' WHERE booking_id = ?
        """, (booking_id,))
        
        conn.commit()
        conn.close()
        return True
    except:
        return False


def get_user_stats(user_id: str) -> Dict:
    """Get user's booking statistics."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Total bookings
    cursor.execute("""
        SELECT COUNT(*) as total FROM bookings WHERE user_id = ?
    """, (user_id,))
    total = cursor.fetchone()['total']
    
    # Completed bookings
    cursor.execute("""
        SELECT COUNT(*) as completed FROM bookings 
        WHERE user_id = ? AND status = 'completed'
    """, (user_id,))
    completed = cursor.fetchone()['completed']
    
    # Total spent
    cursor.execute("""
        SELECT SUM(estimated_cost) as total_spent FROM bookings 
        WHERE user_id = ? AND status IN ('completed', 'confirmed')
    """, (user_id,))
    total_spent = cursor.fetchone()['total_spent'] or 0
    
    conn.close()
    
    return {
        "total_bookings": total,
        "completed_bookings": completed,
        "total_spent": round(total_spent, 2)
    }
