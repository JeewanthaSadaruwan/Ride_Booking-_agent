"""Tool for booking a vehicle for a trip."""

from strands import tool
from db.database import create_dispatch, get_vehicle_by_id, create_booking
import random


@tool
def book_vehicle(
    vehicle_id: str,
    pickup_location: str,
    dropoff_location: str,
    passenger_count: int = 1,
    requested_time: str = "now",
    special_requirements: str = "",
    distance_km: float = None,
    duration_minutes: int = None,
    estimated_cost: float = None,
    user_id: str = None
) -> dict:
    """
    Book selected vehicle for any route (anywhere to anywhere).
    
    Args:
        vehicle_id: ID of vehicle to book
        pickup_location: Pickup location (any address, coordinates, or place name)
        dropoff_location: Dropoff location (any address, coordinates, or place name)
        passenger_count: Number of passengers (default: 1)
        requested_time: Requested time (ISO format or 'now')
        special_requirements: Special requirements (wheelchair, child seat, luggage, etc.)
        distance_km: Trip distance in km
        duration_minutes: Estimated trip duration
        estimated_cost: Estimated trip cost
        user_id: User ID for personalized booking
        
    Returns:
        dict: Booking confirmation with tracking details
    """
    # Get vehicle details
    vehicle = get_vehicle_by_id(vehicle_id)
    
    if not vehicle:
        return {
            "status": "error",
            "message": f"Vehicle {vehicle_id} not found"
        }
    
    if vehicle['status'] != 'available':
        return {
            "status": "error",
            "message": f"Vehicle {vehicle_id} is not available"
        }
    
    try:
        # Mock driver assignment
        drivers = [
            ("John Doe", "+94771234567"),
            ("Jane Smith", "+94771234568"),
            ("Mike Johnson", "+94771234569"),
            ("Sarah Williams", "+94771234570"),
            ("David Brown", "+94771234571"),
        ]
        driver_name, driver_contact = random.choice(drivers)
        
        # Estimate arrival (mock)
        estimated_arrival = f"{random.randint(5, 15)} minutes"
        
        # Create booking record if user_id is provided
        booking_id = None
        if user_id:
            try:
                booking_id = create_booking(
                    user_id=user_id,
                    vehicle_id=vehicle_id,
                    pickup_location=pickup_location,
                    dropoff_location=dropoff_location,
                    pickup_time=requested_time,
                    passenger_count=passenger_count,
                    distance_km=distance_km,
                    duration_minutes=duration_minutes,
                    estimated_cost=estimated_cost,
                    special_requirements=special_requirements
                )
                print(f"✅ Booking record created: {booking_id}")
            except Exception as e:
                print(f"⚠️ Warning: Could not create booking record: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️ No user_id provided - booking will not be saved to user account")
        
        # Create dispatch in database
        dispatch_id = create_dispatch(
            vehicle_id=vehicle_id,
            trip_id=None,  # No longer required - dynamic booking
            driver_name=driver_name,
            driver_contact=driver_contact,
            estimated_arrival=estimated_arrival,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            passenger_count=passenger_count,
            special_requirements=special_requirements,
            user_id=user_id
        )
        
        print(f"✅ Dispatch created: {dispatch_id}")
        print(f"✅ Booking details: Vehicle {vehicle_id}, {pickup_location} → {dropoff_location}")
        
        return {
            "success": True,
            "booking_id": booking_id if booking_id else dispatch_id,
            "dispatch_id": dispatch_id,
            "vehicle_id": vehicle_id,
            "vehicle_info": f"{vehicle['year']} {vehicle['make']} {vehicle['model']}",
            "license_plate": vehicle['license_plate'],
            "status": "booked",
            "driver_name": driver_name,
            "driver_contact": driver_contact,
            "estimated_arrival": estimated_arrival,
            "route": f"{pickup_location} → {dropoff_location}",
            "pickup_location": pickup_location,
            "dropoff_location": dropoff_location,
            "passenger_count": passenger_count,
            "distance_km": distance_km,
            "duration_minutes": duration_minutes,
            "estimated_cost": estimated_cost,
            "message": f"✅ Booking confirmed! Your {vehicle['make']} {vehicle['model']} will arrive in {estimated_arrival}. Booking ID: {booking_id if booking_id else dispatch_id}"
        }
    
    except Exception as e:
        print(f"❌ ERROR in book_vehicle: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "status": "error",
            "message": f"Booking failed: {str(e)}"
        }
