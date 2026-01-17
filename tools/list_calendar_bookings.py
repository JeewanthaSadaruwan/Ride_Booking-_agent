"""Tool to list and retrieve calendar bookings."""

import os
from datetime import datetime, timedelta
import pytz
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


@tool(description="List upcoming ride bookings from Google Calendar")
def list_calendar_bookings(days_ahead: int = 7) -> dict:
    """
    List all upcoming ride bookings from Google Calendar.
    
    Shows all vehicle dispatch events scheduled in the next N days.
    Useful when user asks "What are my bookings?", "Show my rides", "Do I have any trips?"
    
    Args:
        days_ahead: Number of days to look ahead (default: 7 days)
        
    Returns:
        dict: List of upcoming bookings with details
    """
    try:
        service = get_calendar_service()
        
        # Get current time in UTC (Google Calendar uses UTC)
        now = datetime.utcnow()
        end_time = now + timedelta(days=days_ahead)
        
        print(f"🔍 Searching for calendar bookings from {now.isoformat()}Z to {end_time.isoformat()}Z")
        
        # Query calendar events
        events_result = service.events().list(
            calendarId="primary",
            timeMin=now.isoformat() + "Z",
            timeMax=end_time.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
            maxResults=50
        ).execute()
        
        events = events_result.get("items", [])
        
        print(f"📅 Found {len(events)} total calendar events")
        
        # Filter only vehicle dispatch events
        bookings = []
        for event in events:
            summary = event.get("summary", "")
            print(f"  - Event: '{summary}'")
            
            if "🚗" in summary or "Vehicle Dispatch" in summary:
                print(f"    ✅ Matched as vehicle dispatch event")
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                
                # Parse description for details
                description = event.get("description", "")
                
                booking = {
                    "event_id": event["id"],
                    "summary": summary,
                    "start_time": start,
                    "end_time": end,
                    "description": description,
                    "link": event.get("htmlLink")
                }
                bookings.append(booking)
        
        print(f"✅ Filtered to {len(bookings)} vehicle dispatch bookings")
        
        if not bookings:
            return {
                "success": True,
                "count": 0,
                "bookings": [],
                "message": f"No upcoming ride bookings found in the next {days_ahead} days."
            }
        
        return {
            "success": True,
            "count": len(bookings),
            "bookings": bookings,
            "message": f"Found {len(bookings)} upcoming ride booking(s)."
        }
        
    except FileNotFoundError:
        return {
            "success": False,
            "error": "Calendar not configured",
            "message": "⚠️ Calendar integration not set up. No bookings to retrieve."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"❌ Failed to retrieve bookings: {str(e)}"
        }


@tool(description="Get details of a specific booking by event ID")
def get_booking_details(event_id: str) -> dict:
    """
    Get detailed information about a specific booking.
    
    Args:
        event_id: Google Calendar event ID
        
    Returns:
        dict: Detailed booking information
    """
    try:
        service = get_calendar_service()
        
        event = service.events().get(
            calendarId="primary",
            eventId=event_id
        ).execute()
        
        return {
            "success": True,
            "event_id": event["id"],
            "summary": event.get("summary"),
            "description": event.get("description"),
            "start_time": event["start"].get("dateTime"),
            "end_time": event["end"].get("dateTime"),
            "link": event.get("htmlLink"),
            "status": event.get("status")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"❌ Could not retrieve booking details: {str(e)}"
        }
