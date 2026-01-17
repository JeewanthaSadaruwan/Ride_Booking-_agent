"""Tool to get user's booking history from database."""

from strands import tool
from db.database import get_user_bookings


@tool
def get_my_bookings(user_id: str, limit: int = 10) -> dict:
    """
    Get the authenticated user's booking history from the database.
    
    Shows bookings made by the user with complete details including:
    - Booking ID
    - Vehicle information
    - Route (pickup → dropoff)
    - Pickup time
    - Passenger count
    - Distance, duration, cost
    - Booking status
    
    Args:
        user_id: User's unique ID (extract from context)
        limit: Maximum number of bookings to return (default: 10)
        
    Returns:
        dict: List of user's bookings with all details
    """
    try:
        bookings = get_user_bookings(user_id, limit=limit)
        bookings = [b for b in bookings if b.get("status") != "cancelled"]
        
        if not bookings:
            return {
                "success": True,
                "count": 0,
                "bookings": [],
                "message": "You don't have any active bookings yet."
            }
        
        # Format bookings for better presentation
        formatted_bookings = []
        for booking in bookings:
            formatted = {
                "booking_id": booking['booking_id'],
                "vehicle": f"{booking['make']} {booking['model']} ({booking['type']})",
                "license_plate": booking['license_plate'],
                "route": f"{booking['pickup_location']} → {booking['dropoff_location']}",
                "pickup_location": booking['pickup_location'],
                "dropoff_location": booking['dropoff_location'],
                "pickup_time": booking['pickup_time'],
                "passenger_count": booking['passenger_count'],
                "distance_km": booking['distance_km'],
                "duration_minutes": booking['duration_minutes'],
                "estimated_cost": booking['estimated_cost'],
                "special_requirements": booking['special_requirements'],
                "status": booking['status'],
                "created_at": booking['created_at']
            }
            formatted_bookings.append(formatted)
        
        return {
            "success": True,
            "count": len(formatted_bookings),
            "bookings": formatted_bookings,
            "message": f"Found {len(formatted_bookings)} booking(s) in your account."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to retrieve bookings: {str(e)}"
        }
