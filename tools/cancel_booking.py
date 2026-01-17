"""Tool to cancel bookings and remove calendar events."""

import os
import sqlite3
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from strands import tool
from db.database import get_booking_by_id, cancel_booking as cancel_booking_db, get_db_connection

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


def _get_booking_by_calendar_event_id(event_id: str):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM bookings WHERE calendar_event_id = ?",
        (event_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


@tool(description="Cancel a booking and remove it from calendar")
def cancel_booking(event_id: str, reason: str = "User requested cancellation") -> dict:
    """
    Cancel a ride booking and remove the calendar event.
    
    This will:
    1. Delete the calendar event
    2. Free up the driver's time slot
    3. Make the vehicle available again
    
    Args:
        event_id: Google Calendar event ID to cancel
        reason: Reason for cancellation (optional)
        
    Returns:
        dict: Cancellation confirmation with status
    """
    try:
        booking = None
        booking_id = None
        calendar_event_id = None

        if event_id.upper().startswith("BK-"):
            booking = get_booking_by_id(event_id)
            if not booking:
                return {
                    "success": False,
                    "error": "Booking not found",
                    "message": "❌ Could not find booking to cancel. It may already be deleted."
                }
            booking_id = event_id
            calendar_event_id = booking.get("calendar_event_id")
        else:
            booking = _get_booking_by_calendar_event_id(event_id)
            if booking:
                booking_id = booking.get("booking_id")
                calendar_event_id = event_id
            else:
                calendar_event_id = event_id

        if booking_id and not cancel_booking_db(booking_id):
            return {
                "success": False,
                "error": "Database update failed",
                "message": "❌ Failed to cancel booking in the system."
            }

        event_summary = None
        start_time = None
        calendar_warning = None

        if calendar_event_id:
            try:
                service = get_calendar_service()
                event = service.events().get(
                    calendarId="primary",
                    eventId=calendar_event_id
                ).execute()
                event_summary = event.get("summary", "Unknown")
                start_time = event["start"].get("dateTime", event["start"].get("date"))
                service.events().delete(
                    calendarId="primary",
                    eventId=calendar_event_id
                ).execute()
            except FileNotFoundError:
                calendar_warning = "Calendar integration not set up; booking cancelled in system only."
            except Exception as e:
                calendar_warning = f"Booking cancelled, but calendar event could not be removed: {str(e)}"

        message = "✅ Booking cancelled successfully."
        if event_summary:
            message = f"✅ Booking cancelled successfully. The calendar event '{event_summary}' has been removed."
        if calendar_warning:
            message = f"{message} {calendar_warning}"

        return {
            "success": True,
            "event_id": calendar_event_id,
            "event_summary": event_summary,
            "start_time": start_time,
            "reason": reason,
            "message": message
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"❌ Failed to cancel booking: {str(e)}"
        }


@tool(description="Cancel all bookings for a specific time period")
def cancel_bookings_by_date(date: str, cancel_all_day: bool = False) -> dict:
    """
    Cancel all bookings for a specific date.
    
    Useful when user wants to cancel "all my bookings tomorrow" or "my booking on Jan 20th".
    
    Args:
        date: Date in ISO format (YYYY-MM-DD) or "tomorrow", "today"
        cancel_all_day: If True, cancels all bookings for that entire day
        
    Returns:
        dict: List of cancelled bookings
    """
    try:
        service = get_calendar_service()
        
        # Parse date (simplified - in production would handle "tomorrow" etc.)
        from datetime import datetime, timedelta
        
        if date.lower() == "tomorrow":
            target_date = datetime.now() + timedelta(days=1)
        elif date.lower() == "today":
            target_date = datetime.now()
        else:
            target_date = datetime.fromisoformat(date)
        
        # Get events for that day
        start_of_day = target_date.replace(hour=0, minute=0, second=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59)
        
        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_of_day.isoformat() + "Z",
            timeMax=end_of_day.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        events = events_result.get("items", [])
        
        # Filter vehicle dispatch events
        cancelled = []
        for event in events:
            summary = event.get("summary", "")
            if "🚗" in summary or "Vehicle Dispatch" in summary:
                service.events().delete(
                    calendarId="primary",
                    eventId=event["id"]
                ).execute()
                cancelled.append({
                    "event_id": event["id"],
                    "summary": summary,
                    "start_time": event["start"].get("dateTime")
                })
        
        if not cancelled:
            return {
                "success": True,
                "count": 0,
                "message": f"No bookings found for {target_date.strftime('%Y-%m-%d')} to cancel."
            }
        
        return {
            "success": True,
            "count": len(cancelled),
            "cancelled_bookings": cancelled,
            "message": f"✅ Cancelled {len(cancelled)} booking(s) for {target_date.strftime('%Y-%m-%d')}."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"❌ Failed to cancel bookings: {str(e)}"
        }
