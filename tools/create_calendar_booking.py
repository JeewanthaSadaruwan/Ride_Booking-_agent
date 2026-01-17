"""
Google Calendar integration tool for vehicle dispatch time blocking.

This tool creates calendar events to block driver time when a vehicle is dispatched.
"""

import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from strands import tool

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = "token.json"


def get_calendar_service():
    """Get authenticated Google Calendar service."""
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(
            f"{TOKEN_FILE} not found. Run google_calendar_auth.py first to authenticate."
        )
    
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        service = build("calendar", "v3", credentials=creds)
        return service
    except RefreshError:
        raise Exception(
            "Token expired or invalid. Run google_calendar_auth.py to re-authenticate."
        )


@tool(description="Create Google Calendar event to block time for vehicle booking")
def create_calendar_booking(
    dispatch_id: str,
    vehicle_id: str,
    driver_name: str,
    pickup_location: str,
    dropoff_location: str,
    pickup_time: str,
    trip_duration_minutes: int,
    estimated_cost: float,
    passenger_count: int = 1
) -> dict:
    """
    Create a Google Calendar event to block time for a vehicle booking.
    
    This ensures the driver's time is reserved and prevents double-booking.
    
    Args:
        dispatch_id: Unique booking identifier
        vehicle_id: Vehicle ID (e.g., SLV001)
        driver_name: Driver's name
        pickup_location: Starting location
        dropoff_location: Destination location
        pickup_time: Pickup time in ISO format (e.g., "2026-01-15T09:00:00")
        trip_duration_minutes: Expected trip duration in minutes
        estimated_cost: Trip cost estimate
        passenger_count: Number of passengers
        
    Returns:
        dict: Calendar event details including event ID and link
    """
    try:
        service = get_calendar_service()
        
        # Parse pickup time
        start_time = datetime.fromisoformat(pickup_time)
        
        # Calculate end time
        end_time = start_time + timedelta(minutes=trip_duration_minutes)
        
        # Create event description
        description = f"""🚗 Vehicle Dispatch Details

📋 Dispatch ID: {dispatch_id}
🚙 Vehicle: {vehicle_id}
👤 Driver: {driver_name}
👥 Passengers: {passenger_count}

📍 Route:
   Pickup: {pickup_location}
   Dropoff: {dropoff_location}

⏱️ Duration: {trip_duration_minutes} minutes
💰 Cost: ${estimated_cost:.2f}

Status: Dispatched
"""
        
        # Create event
        event = {
            "summary": f"🚗 Vehicle Dispatch – {vehicle_id}",
            "description": description,
            "start": {
                "dateTime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "Asia/Colombo"  # Sri Lanka timezone
            },
            "end": {
                "dateTime": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "Asia/Colombo"
            },
            "colorId": "9",  # Blue color for dispatch events
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 30},  # 30 min before
                    {"method": "popup", "minutes": 10},  # 10 min before
                ]
            }
        }
        
        # Insert event into calendar
        created_event = service.events().insert(
            calendarId="primary",
            body=event
        ).execute()
        
        return {
            "success": True,
            "event_id": created_event["id"],
            "event_link": created_event.get("htmlLink"),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "message": f"✅ Calendar event created for {driver_name}'s dispatch from {pickup_location} to {dropoff_location}"
        }
        
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": str(e),
            "message": "⚠️ Calendar integration not set up. Authentication required."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"❌ Failed to create calendar event: {str(e)}"
        }


@tool(description="Check if a time slot is available in the calendar")
def check_calendar_availability(
    start_time: str,
    duration_minutes: int
) -> dict:
    """
    Check if a time slot is available in the calendar.
    
    Useful for preventing double-booking before dispatching a vehicle.
    
    Args:
        start_time: Start time in ISO format (e.g., "2026-01-15T09:00:00")
        duration_minutes: Duration to check in minutes
        
    Returns:
        dict: Availability status and conflicting events if any
    """
    try:
        service = get_calendar_service()
        
        start_dt = datetime.fromisoformat(start_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # Query events in the time range
        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_dt.isoformat() + "Z",
            timeMax=end_dt.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        events = events_result.get("items", [])
        
        if not events:
            return {
                "available": True,
                "message": f"✅ Time slot available: {start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%H:%M')}"
            }
        else:
            conflicts = [
                {
                    "summary": event.get("summary"),
                    "start": event["start"].get("dateTime"),
                    "end": event["end"].get("dateTime")
                }
                for event in events
            ]
            return {
                "available": False,
                "conflicts": conflicts,
                "message": f"⚠️ {len(conflicts)} conflicting event(s) found in this time slot"
            }
            
    except FileNotFoundError:
        return {
            "available": True,  # Assume available if calendar not set up
            "message": "⚠️ Calendar not configured - availability check skipped"
        }
    except Exception as e:
        return {
            "available": True,  # Fail open
            "error": str(e),
            "message": f"⚠️ Could not check availability: {str(e)}"
        }
