"""Tool for recommending the best vehicle option."""

from strands import tool


@tool
def recommend_best_vehicle(
    ranked_vehicles: list,
    trip_details: dict,
    top_n: int = 3
) -> dict:
    """
    Generate final vehicle recommendation with justification.
    
    Args:
        ranked_vehicles: List of ranked vehicle options
        trip_details: Complete trip details
        top_n: Number of top recommendations to include
        
    Returns:
        dict: Recommendation with top options and reasoning
    """
    # Tool implementation placeholder
    # In production, this would generate comprehensive recommendations
    top_vehicles = ranked_vehicles[:top_n]
    
    return {
        "primary_recommendation": top_vehicles[0] if top_vehicles else None,
        "alternatives": top_vehicles[1:] if len(top_vehicles) > 1 else [],
        "reasoning": [
            "Best overall match for requirements",
            "Optimal balance of cost and pickup time",
            "High user preference alignment"
        ],
        "estimated_total_time": 33,
        "estimated_total_cost": 42.50
    }
