"""Tool for listing available vehicles in the fleet."""

from strands import tool
from db.database import get_available_vehicles


@tool
def list_available_vehicles(location: str = "", vehicle_type: str = "") -> list:
    """
    List all vehicles currently available for dispatch.
    
    Args:
        location: Optional location filter to find nearby vehicles
        vehicle_type: Optional vehicle type filter (sedan, suv, van, etc.)
        
    Returns:
        list: List of available vehicles with details
    """
    vehicles = get_available_vehicles(location, vehicle_type)
    return vehicles
