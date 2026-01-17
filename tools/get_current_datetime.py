"""Tool to get current date and time in Sri Lanka timezone."""

from datetime import datetime, timedelta
import pytz
from strands import tool


@tool
def get_current_datetime() -> dict:
    """
    Get the REAL-TIME current date and time in Sri Lanka timezone (Asia/Colombo).
    
    ⚠️ CRITICAL: ALWAYS call this tool when:
    - User asks "what is the time now", "what's the current time", "tell me the time"
    - User asks "what is today's date"
    - Starting any trip booking to get current time reference
    - User says "I need a ride now" (to know what "now" means)
    - User says "Book for tomorrow at 10 AM" (to calculate tomorrow's date)
    - User says "Pick me up in 2 hours" (to calculate future time)
    - User says "Schedule for next Monday" (to find next Monday's date)
    
    🚨 DO NOT respond with cached or remembered time - ALWAYS call this tool fresh!
    
    This tool is CRITICAL for handling time-based requests like:
    - "I need a ride now"
    - "Book for tomorrow at 10 AM"
    - "Pick me up in 2 hours"
    - "Schedule for next Monday"
    
    Always call this tool at the start of any trip booking to establish
    the current time reference.
    
    Returns:
        dict: Current datetime information including:
            - current_datetime: ISO format datetime string
            - date: Current date (YYYY-MM-DD)
            - time: Current time (HH:MM:SS)
            - day_of_week: Day name (Monday, Tuesday, etc.)
            - timezone: Asia/Colombo
            - timestamp: Unix timestamp
            - formatted: Human-readable format
    
    Example usage:
        - User: "I need a ride now"
          Agent: Calls get_current_datetime() → knows current time
        
        - User: "Book for tomorrow at 10 AM"
          Agent: Calls get_current_datetime() → calculates tomorrow's date
    """
    try:
        # Get current time in Sri Lanka timezone
        sri_lanka_tz = pytz.timezone('Asia/Colombo')
        now = datetime.now(sri_lanka_tz)
        
        return {
            "success": True,
            "current_datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "timezone": "Asia/Colombo",
            "timestamp": int(now.timestamp()),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "message": f"Current time in Sri Lanka: {now.strftime('%A, %B %d, %Y at %I:%M %p')}"
        }
    except Exception as e:
        # Fallback to UTC if timezone fails
        now = datetime.utcnow()
        return {
            "success": True,
            "current_datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "timezone": "UTC",
            "timestamp": int(now.timestamp()),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "message": f"Current time (UTC): {now.strftime('%Y-%m-%d %H:%M:%S')}",
            "warning": f"Could not get Sri Lanka timezone: {str(e)}"
        }


@tool
def calculate_future_datetime(
    hours_from_now: int = 0,
    days_from_now: int = 0,
    target_time: str = None
) -> dict:
    """
    Calculate a future datetime based on current time in Sri Lanka.
    
    Useful for handling relative time requests like:
    - "in 2 hours"
    - "tomorrow"
    - "tomorrow at 10 AM"
    - "next Monday at 3 PM"
    
    Args:
        hours_from_now: Number of hours from now (e.g., 2 for "in 2 hours")
        days_from_now: Number of days from now (e.g., 1 for "tomorrow")
        target_time: Specific time if mentioned (e.g., "10:00", "15:30")
    
    Returns:
        dict: Future datetime information with ISO format for booking
    
    Example usage:
        - "in 2 hours" → calculate_future_datetime(hours_from_now=2)
        - "tomorrow" → calculate_future_datetime(days_from_now=1)
        - "tomorrow at 10 AM" → calculate_future_datetime(days_from_now=1, target_time="10:00")
    """
    try:
        sri_lanka_tz = pytz.timezone('Asia/Colombo')
        now = datetime.now(sri_lanka_tz)
        
        # Calculate future datetime
        future_dt = now + timedelta(hours=hours_from_now, days=days_from_now)
        
        # If specific time is provided, set it
        if target_time:
            try:
                # Parse time (supports "10:00", "10:00:00", "15:30")
                time_parts = target_time.split(":")
                hour = int(time_parts[0])
                minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                second = int(time_parts[2]) if len(time_parts) > 2 else 0
                
                future_dt = future_dt.replace(hour=hour, minute=minute, second=second)
            except:
                pass  # Use calculated time if parsing fails
        
        return {
            "success": True,
            "datetime": future_dt.isoformat(),
            "date": future_dt.strftime("%Y-%m-%d"),
            "time": future_dt.strftime("%H:%M:%S"),
            "day_of_week": future_dt.strftime("%A"),
            "timezone": "Asia/Colombo",
            "timestamp": int(future_dt.timestamp()),
            "formatted": future_dt.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "message": f"Calculated time: {future_dt.strftime('%A, %B %d, %Y at %I:%M %p')}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Could not calculate future datetime"
        }
