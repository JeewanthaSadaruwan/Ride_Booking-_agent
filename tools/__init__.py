"""Tools module for the vehicle dispatch agent."""

# Import all tools to make them accessible
from .get_current_datetime import get_current_datetime, calculate_future_datetime
from .geocode_location import geocode_location
from .calculate_route import calculate_route
from .list_available_vehicles import list_available_vehicles
from .filter_vehicles_by_constraints import filter_vehicles_by_constraints
from .estimate_trip_cost import estimate_trip_cost
from .recommend_best_vehicle import recommend_best_vehicle
from .book_vehicle import book_vehicle
from .create_calendar_booking import create_calendar_booking, check_calendar_availability
from .list_calendar_bookings import list_calendar_bookings, get_booking_details
from .cancel_booking import cancel_booking, cancel_bookings_by_date
from .get_my_bookings import get_my_bookings

# List of all available tools
ALL_TOOLS = [
    get_current_datetime,
    calculate_future_datetime,
    geocode_location,
    calculate_route,
    list_available_vehicles,
    filter_vehicles_by_constraints,
    estimate_trip_cost,
    recommend_best_vehicle,
    book_vehicle,
    create_calendar_booking,
    check_calendar_availability,
    list_calendar_bookings,
    get_booking_details,
    cancel_booking,
    cancel_bookings_by_date,
    get_my_bookings,
]

__all__ = [
    "get_current_datetime",
    "calculate_future_datetime",
    "geocode_location",
    "calculate_route",
    "list_available_vehicles",
    "filter_vehicles_by_constraints",
    "estimate_trip_cost",
    "recommend_best_vehicle",
    "book_vehicle",
    "create_calendar_booking",
    "check_calendar_availability",
    "cancel_booking",
    "cancel_bookings_by_date",
    "list_calendar_bookings",
    "get_booking_details",
    "get_my_bookings",
    "ALL_TOOLS",
]
