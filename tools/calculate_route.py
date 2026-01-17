"""Tool to calculate route, distance, and ETA using OpenStreetMap OSRM."""

import requests
import time
from strands import tool


@tool
def calculate_route(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
    origin_name: str = "",
    destination_name: str = ""
) -> dict:
    """
    Calculate route, distance, and estimated travel time between two locations using OSRM.
    
    This tool uses OpenStreetMap's OSRM (Open Source Routing Machine) to calculate
    the actual driving route, distance, and duration between two geographic points.
    
    Args:
        origin_lat (float): Origin latitude
        origin_lon (float): Origin longitude
        destination_lat (float): Destination latitude
        destination_lon (float): Destination longitude
        origin_name (str, optional): Origin location name for reference
        destination_name (str, optional): Destination location name for reference
    
    Returns:
        dict: Route information including:
            - success: Whether routing succeeded
            - distance_km: Distance in kilometers
            - distance_meters: Distance in meters
            - duration_minutes: Duration in minutes
            - duration_seconds: Duration in seconds
            - origin: Origin details
            - destination: Destination details
            - route_summary: Text summary
    
    Example usage:
        - Calculate distance from Colombo to Kandy
        - Get ETA from current location to airport
        - Estimate travel time for vehicle dispatch
    """
    try:
        # OSRM public demo server (free, no API key)
        url = f"http://router.project-osrm.org/route/v1/driving/{origin_lon},{origin_lat};{destination_lon},{destination_lat}"
        
        params = {
            "overview": "false",  # Don't need full geometry
            "steps": "false"      # Don't need turn-by-turn
        }
        
        # Small delay to be respectful to free service
        time.sleep(0.5)
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('code') == 'Ok' and 'routes' in data and len(data['routes']) > 0:
                route = data['routes'][0]
                
                distance_meters = route.get('distance', 0)  # meters
                duration_seconds = route.get('duration', 0)  # seconds
                
                distance_km = round(distance_meters / 1000, 2)
                duration_minutes = round(duration_seconds / 60, 1)
                
                return {
                    "success": True,
                    "distance_km": distance_km,
                    "distance_meters": distance_meters,
                    "duration_minutes": duration_minutes,
                    "duration_seconds": duration_seconds,
                    "origin": {
                        "name": origin_name or "Origin",
                        "latitude": origin_lat,
                        "longitude": origin_lon
                    },
                    "destination": {
                        "name": destination_name or "Destination",
                        "latitude": destination_lat,
                        "longitude": destination_lon
                    },
                    "route_summary": f"{distance_km} km, approximately {duration_minutes} minutes",
                    "source": "OSRM (OpenStreetMap)"
                }
            else:
                # OSRM couldn't find route, use haversine fallback
                return _calculate_haversine_fallback(
                    origin_lat, origin_lon, destination_lat, destination_lon,
                    origin_name, destination_name
                )
                
        else:
            # API error, use fallback
            return _calculate_haversine_fallback(
                origin_lat, origin_lon, destination_lat, destination_lon,
                origin_name, destination_name
            )
            
    except Exception as e:
        # Any error, use fallback
        return _calculate_haversine_fallback(
            origin_lat, origin_lon, destination_lat, destination_lon,
            origin_name, destination_name
        )


def _calculate_haversine_fallback(
    lat1: float, lon1: float, lat2: float, lon2: float,
    origin_name: str = "", destination_name: str = ""
) -> dict:
    """Calculate straight-line distance using Haversine formula (fallback)."""
    from math import radians, sin, cos, sqrt, atan2
    
    # Earth radius in km
    R = 6371.0
    
    # Convert to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance_km = round(R * c, 2)
    
    # Estimate duration (assume average 50 km/h in Sri Lanka with traffic)
    duration_minutes = round((distance_km / 50) * 60, 1)
    
    return {
        "success": True,
        "distance_km": distance_km,
        "distance_meters": distance_km * 1000,
        "duration_minutes": duration_minutes,
        "duration_seconds": duration_minutes * 60,
        "origin": {
            "name": origin_name or "Origin",
            "latitude": lat1,
            "longitude": lon1
        },
        "destination": {
            "name": destination_name or "Destination",
            "latitude": lat2,
            "longitude": lon2
        },
        "route_summary": f"~{distance_km} km (straight-line), approximately {duration_minutes} minutes",
        "source": "Haversine formula (fallback)",
        "note": "Routing service unavailable. Using straight-line distance estimate."
    }
