"""Tool for estimating trip cost based on vehicle type and comfort."""

from strands import tool


@tool
def estimate_trip_cost(
    distance_km: float,
    duration_minutes: int,
    vehicle_type: str,
    surge_multiplier: float = 1.0
) -> dict:
    """
    Calculate estimated cost for the trip based on vehicle type, comfort, and capacity.
    
    Args:
        distance_km: Trip distance in kilometers
        duration_minutes: Estimated trip duration in minutes
        vehicle_type: Type of vehicle (Economy, Standard, Luxury, Van, SUV, etc.)
        surge_multiplier: Surge pricing multiplier if applicable
        
    Returns:
        dict: Cost estimate breakdown
    """
    # Base rates in LKR
    base_rate = 250  # Starting fare
    
    # Vehicle-specific pricing multipliers based on type, comfort, and capacity
    vehicle_multipliers = {
        # Economy vehicles (small cars, basic sedans)
        "economy": {"per_km": 80, "per_min": 15, "base_multiplier": 1.0, "comfort": "Basic"},
        "standard": {"per_km": 100, "per_min": 20, "base_multiplier": 1.0, "comfort": "Standard"},
        
        # Luxury/Premium vehicles (higher comfort, features like WiFi, leather seats)
        "luxury": {"per_km": 150, "per_min": 30, "base_multiplier": 1.5, "comfort": "Premium"},
        "premium": {"per_km": 140, "per_min": 28, "base_multiplier": 1.4, "comfort": "Premium"},
        
        # SUVs (more space, higher capacity, good for families/luggage)
        "suv": {"per_km": 120, "per_min": 25, "base_multiplier": 1.2, "comfort": "Comfort"},
        
        # Vans (large capacity for groups, more space)
        "van": {"per_km": 130, "per_min": 26, "base_multiplier": 1.3, "comfort": "Spacious"},
        "minivan": {"per_km": 125, "per_min": 25, "base_multiplier": 1.25, "comfort": "Spacious"},
        
        # Default fallback
        "sedan": {"per_km": 90, "per_min": 18, "base_multiplier": 1.0, "comfort": "Standard"},
    }
    
    # Determine vehicle category
    vehicle_lower = vehicle_type.lower()
    pricing = None
    
    # Match vehicle type to pricing category
    if "luxury" in vehicle_lower or "premium" in vehicle_lower or "mercedes" in vehicle_lower or "bmw" in vehicle_lower:
        pricing = vehicle_multipliers["luxury"]
    elif "van" in vehicle_lower:
        pricing = vehicle_multipliers["van"]
    elif "suv" in vehicle_lower:
        pricing = vehicle_multipliers["suv"]
    elif "economy" in vehicle_lower or "budget" in vehicle_lower:
        pricing = vehicle_multipliers["economy"]
    else:
        # Default to standard sedan pricing
        pricing = vehicle_multipliers["standard"]
    
    # Calculate costs
    adjusted_base = base_rate * pricing["base_multiplier"]
    distance_charge = distance_km * pricing["per_km"]
    time_charge = duration_minutes * pricing["per_min"]
    
    subtotal = adjusted_base + distance_charge + time_charge
    final_cost = subtotal * surge_multiplier
    
    return {
        "estimated_cost": round(final_cost, 2),
        "currency": "LKR",
        "vehicle_category": pricing["comfort"],
        "breakdown": {
            "base_fare": round(adjusted_base, 2),
            "distance_charge": round(distance_charge, 2),
            "time_charge": round(time_charge, 2),
            "subtotal": round(subtotal, 2),
            "surge_multiplier": surge_multiplier,
            "final_total": round(final_cost, 2)
        },
        "pricing_note": f"{pricing['comfort']} vehicle - LKR {pricing['per_km']}/km + LKR {pricing['per_min']}/min"
    }
