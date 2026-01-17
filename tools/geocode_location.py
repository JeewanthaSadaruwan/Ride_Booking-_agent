"""Tool to convert location names to coordinates using OpenStreetMap Nominatim."""

import requests
import time
from strands import tool


@tool
def geocode_location(location_name: str) -> dict:
    """
    Convert a location name (address/place) to geographic coordinates using OpenStreetMap.
    
    This tool uses OpenStreetMap Nominatim API to geocode Sri Lankan locations.
    Essential for converting user's text addresses into lat/lon coordinates for routing.
    
    Args:
        location_name (str): Name of the location (e.g., "Colombo Fort", "Kandy", "BIA Airport")
    
    Returns:
        dict: Geocoded location with:
            - success: Whether geocoding succeeded
            - location_name: Original location name
            - coordinates: {latitude, longitude}
            - full_address: Complete formatted address from OSM
            - display_name: Full display name
            - confidence: Accuracy confidence
            - ambiguous: True if location is too broad/has multiple interpretations
            - alternatives: List of specific location suggestions if ambiguous
    
    Example usage:
        - Convert "Colombo Fort" to coordinates
        - Convert "Katunayake Airport" to lat/lon
        - Find exact location of "Galle Face Hotel"
    """
    try:
        # Check if location is too broad (just city name without specifics)
        is_broad = _is_location_too_broad(location_name)
        
        # Enhance Sri Lankan location names for better results
        enhanced_location = _enhance_sri_lankan_location(location_name)
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": enhanced_location,
            "format": "json",
            "limit": 5 if is_broad else 1,  # Get more results if location is broad
            "countrycodes": "lk",  # Restrict to Sri Lanka
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "vehicle-dispatch-agent/1.0 (sri-lanka-dispatch-service)"
        }
        
        # Respect rate limit (max 1 req/sec)
        time.sleep(1)
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                lat = float(result.get('lat', 0))
                lon = float(result.get('lon', 0))
                display_name = result.get('display_name', '')
                
                # If location was broad, provide alternatives
                if is_broad and len(data) > 1:
                    alternatives = _get_specific_alternatives(location_name)
                    return {
                        "success": False,
                        "ambiguous": True,
                        "location_name": location_name,
                        "alternatives": alternatives,
                        "message": f"'{location_name}' is too broad. Please specify a more exact location.",
                        "suggestion": "Choose from: " + ", ".join(alternatives)
                    }
                
                return {
                    "success": True,
                    "location_name": location_name,
                    "coordinates": {
                        "latitude": lat,
                        "longitude": lon
                    },
                    "full_address": display_name,
                    "display_name": display_name,
                    "confidence": "high",
                    "ambiguous": False,
                    "source": "OpenStreetMap Nominatim"
                }
            else:
                # Location not found - try fallback strategies
                logger.warning(f"⚠️ Location not found in OSM: {location_name}")
                
                # Try fallback: extract city/area and use that instead
                fallback_location = _get_fallback_location(location_name)
                if fallback_location:
                    logger.info(f"🔄 Trying fallback location: {fallback_location}")
                    # Recursive call with fallback
                    return geocode_location(fallback_location)
                
                return {
                    "success": False,
                    "location_name": location_name,
                    "error": "Location not found in OpenStreetMap",
                    "suggestion": "Please provide a nearby landmark, address, or well-known location (e.g., 'Colombo 4' instead of specific office names)"
                }
        else:
            return {
                "success": False,
                "location_name": location_name,
                "error": f"Geocoding API returned status {response.status_code}",
                "suggestion": "Service temporarily unavailable. Using approximate location."
            }
            
    except Exception as e:
        return {
            "success": False,
            "location_name": location_name,
            "error": str(e),
            "suggestion": "Could not geocode location. Using city name for calculations."
        }


def _is_location_too_broad(location: str) -> bool:
    """Check if a location name is too broad and needs clarification."""
    location_lower = location.lower().strip()
    
    # If it has specific landmarks/places, it's NOT too broad
    specifics = ["bus stand", "railway", "station", "fort", "hospital", 
               "airport", "hotel", "mall", "junction", "road", "street",
               "temple", "church", "mosque", "beach", "park", "market"]
    
    if any(spec in location_lower for spec in specifics):
        return False  # Has specifics, so it's fine
    
    # List of broad city/district names that need specifics
    broad_locations = [
        "colombo", "gampaha", "kandy", "galle", "negombo", "kurunegala",
        "anuradhapura", "jaffna", "trincomalee", "batticaloa", "matara",
        "ratnapura", "badulla", "nuwara eliya", "kalutara", "hambantota"
    ]
    
    # Check if it's just a city name without specifics
    words = location_lower.split()
    if len(words) <= 2:
        for broad in broad_locations:
            if location_lower == broad:
                return True
    
    return False


def _get_specific_alternatives(location: str) -> list:
    """Get specific location alternatives for broad location names."""
    location_lower = location.lower().strip()
    
    alternatives_map = {
        "colombo": [
            "Colombo Fort (Railway Station)",
            "Pettah (Market Area)",
            "Bambalapitiya",
            "Kollupitiya",
            "Colombo 7 (Cinnamon Gardens)",
            "Dehiwala"
        ],
        "gampaha": [
            "Gampaha Bus Stand",
            "Gampaha Railway Station",
            "Gampaha Town Center",
            "Gampaha Hospital"
        ],
        "kandy": [
            "Kandy City Center",
            "Kandy Railway Station",
            "Kandy Bus Stand",
            "Temple of the Tooth",
            "Peradeniya"
        ],
        "negombo": [
            "Negombo Bus Stand",
            "Negombo Beach",
            "Negombo City Center"
        ],
        "galle": [
            "Galle Fort",
            "Galle Bus Stand",
            "Galle Railway Station"
        ]
    }
    
    for key, alternatives in alternatives_map.items():
        if location_lower == key or location_lower.startswith(key):
            return alternatives
    
    # Default alternatives
    return [f"{location} Bus Stand", f"{location} Railway Station", f"{location} Town Center"]


def _get_fallback_location(location: str) -> str:
    """
    Extract a fallback location when specific place not found in OSM.
    
    Examples:
    - "WSO2 Colombo" -> "Colombo 4, Sri Lanka"
    - "Some Hotel Gampaha" -> "Gampaha, Sri Lanka"
    - "XYZ Office Kandy" -> "Kandy, Sri Lanka"
    """
    location_lower = location.lower()
    
    # Map of keywords to fallback locations
    fallback_map = {
        "wso2": "105 Bauddhaloka Mawatha, Colombo 4, Sri Lanka",
        "colombo 1": "Colombo 01, Fort, Sri Lanka",
        "colombo 2": "Colombo 02, Slave Island, Sri Lanka",
        "colombo 3": "Colombo 03, Kollupitiya, Sri Lanka",
        "colombo 4": "Colombo 04, Bambalapitiya, Sri Lanka",
        "colombo 5": "Colombo 05, Narahenpita, Sri Lanka",
        "colombo 6": "Colombo 06, Wellawatta, Sri Lanka",
        "colombo 7": "Colombo 07, Cinnamon Gardens, Sri Lanka",
        "colombo fort": "Fort, Colombo, Sri Lanka",
        "pettah": "Pettah, Colombo, Sri Lanka",
        "bambalapitiya": "Bambalapitiya, Colombo, Sri Lanka",
        "wellawatta": "Wellawatta, Colombo, Sri Lanka",
        "mount lavinia": "Mount Lavinia, Dehiwala-Mount Lavinia, Sri Lanka",
    }
    
    # Check for specific fallbacks
    for keyword, fallback in fallback_map.items():
        if keyword in location_lower:
            return fallback
    
    # Extract city name if present
    major_cities = ["colombo", "gampaha", "kandy", "galle", "negombo", "kurunegala",
                   "anuradhapura", "jaffna", "matara", "ratnapura", "badulla"]
    
    for city in major_cities:
        if city in location_lower:
            return f"{city.title()}, Sri Lanka"
    
    return ""  # No fallback found


def _enhance_sri_lankan_location(location: str) -> str:
    """Enhance location name for better OpenStreetMap results in Sri Lanka."""
    location_lower = location.lower().strip()
    
    # Common Sri Lankan location aliases
    enhancements = {
        "bia": "Bandaranaike International Airport, Katunayake, Sri Lanka",
        "katunayake airport": "Bandaranaike International Airport, Katunayake, Sri Lanka",
        "colombo fort": "Fort, Colombo, Sri Lanka",
        "fort": "Fort, Colombo 01, Sri Lanka",
        "galle face": "Galle Face, Colombo, Sri Lanka",
        "mount lavinia": "Mount Lavinia, Dehiwala-Mount Lavinia, Sri Lanka",
        "kandy city": "Kandy, Central Province, Sri Lanka",
        "peradeniya": "Peradeniya, Kandy, Sri Lanka",
        "nugegoda": "Nugegoda, Colombo, Sri Lanka",
        "maharagama": "Maharagama, Colombo, Sri Lanka",
        "negombo": "Negombo, Western Province, Sri Lanka",
        "galle": "Galle, Southern Province, Sri Lanka",
        "matara": "Matara, Southern Province, Sri Lanka",
        "jaffna": "Jaffna, Northern Province, Sri Lanka",
        "anuradhapura": "Anuradhapura, North Central Province, Sri Lanka",
        "polonnaruwa": "Polonnaruwa, North Central Province, Sri Lanka",
        "trincomalee": "Trincomalee, Eastern Province, Sri Lanka",
        "batticaloa": "Batticaloa, Eastern Province, Sri Lanka",
        "kurunegala": "Kurunegala, North Western Province, Sri Lanka",
        "ratnapura": "Ratnapura, Sabaragamuwa Province, Sri Lanka",
        "badulla": "Badulla, Uva Province, Sri Lanka",
        "nuwara eliya": "Nuwara Eliya, Central Province, Sri Lanka",
        "ella": "Ella, Badulla, Sri Lanka",
        "sigiriya": "Sigiriya, Matale, Sri Lanka",
        "dambulla": "Dambulla, Matale, Sri Lanka",
        "wso2": "105 Bauddhaloka Mawatha, Colombo 4, Sri Lanka",
        # Bus stands and stations
        "gampaha bus stand": "Gampaha Bus Stand, Gampaha, Sri Lanka",
        "gampaha railway station": "Gampaha Railway Station, Gampaha, Sri Lanka",
        "gampaha station": "Gampaha Railway Station, Gampaha, Sri Lanka",
        "colombo fort station": "Colombo Fort Railway Station, Sri Lanka",
        "fort station": "Colombo Fort Railway Station, Sri Lanka",
        "kandy bus stand": "Kandy Bus Stand, Kandy, Sri Lanka",
        "kandy railway station": "Kandy Railway Station, Sri Lanka",
        "pettah bus stand": "Pettah Bus Stand, Colombo, Sri Lanka",
    }
    
    # Check for exact matches first
    for key, value in enhancements.items():
        if location_lower == key or key in location_lower:
            return value
    
    # Handle generic "bus stand" or "railway station" patterns
    if "bus stand" in location_lower and ", " not in location:
        # Extract city name before "bus stand"
        parts = location_lower.replace(" bus stand", "")
        city = parts.strip()
        if city:
            return f"{city.title()} Bus Stand, {city.title()}, Sri Lanka"
    
    if "railway station" in location_lower and ", " not in location:
        parts = location_lower.replace(" railway station", "").replace(" station", "")
        city = parts.strip()
        if city:
            return f"{city.title()} Railway Station, {city.title()}, Sri Lanka"
    
    # If location mentions just a city name, ensure proper formatting
    if len(location.split()) <= 2:
        # Single or two-word location (likely city name)
        # For hotels/businesses that couldn't be found, fall back to city
        if "hotel" in location_lower or "land of the kings" in location_lower:
            # Extract city name
            if "gampaha" in location_lower:
                return "Gampaha, Western Province, Sri Lanka"
            elif "colombo" in location_lower:
                return "Colombo, Western Province, Sri Lanka"
            elif "kandy" in location_lower:
                return "Kandy, Central Province, Sri Lanka"
    
    # Add "Sri Lanka" if not present
    if "sri lanka" not in location_lower:
        return f"{location}, Sri Lanka"
    
    return location
