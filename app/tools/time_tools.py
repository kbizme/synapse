from langchain.tools import tool
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta 
from typing import Literal



@tool('get_current_time')
def get_current_time(timezone: str = 'UTC') -> dict:
    """
    Get the current date and time for a specified timezone.

    Use this tool when the user asks:
    - "What time is it?"
    - "What is the current date?"
    - "What time is it in a specific country or city?"

    Args:
        timezone: An IANA timezone string (e.g., "UTC", "Asia/Kolkata").

    Returns:
        On success:
            {
              "ok": true,
              "data": {
                "iso": "...",
                "readable": "...",
                "timezone": "...",
                "is_dst": true | false
              }
            }
        On failure:
            { "ok": false, "error": "Invalid or unsupported timezone" }
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
        processed_data =  {
            'iso': now.isoformat(),
            'readable': now.strftime('%A, %B %d, %Y %I:%M %p'),
            'timezone': timezone,
            'is_dst': bool(now.dst())
        }
        return {'ok': True, 'data': processed_data}
    except Exception as e:
        return {'ok': False, 'error': f'Invalid timezone: {str(e)}'}



# @tool('calculate_date_relative')
def calculate_date_relative(base_date: str | None = None, 
                            value: int = 0, 
                            unit: Literal['days', 'weeks', 'months', 'years'] = 'days',
                            direction: Literal['future', 'past'] = 'future') -> dict:
    """
    Calculate a date in the past or future relative to a base date.

    Use this tool when the user asks:
    - "What date is 10 days from now?"
    - "What was the date 2 months ago?"
    - "What date will it be 3 years after a given date?"

    Args:
        base_date: Base date in ISO format (YYYY-MM-DD). Defaults to today if not passed.
        value: Number of time units to move. Use only positive values.
        unit: Time unit ("days", "weeks", "months", "years").
        direction: "future" to add time, "past" to subtract time.

    Returns:
        On success:
            {
              "ok": true,
              "data": {
                "base_date": "...",
                "target_date": "...",
                "day_of_week": "...",
                "description": "..."
              }
            }
        On failure:
            { "ok": false, "error": "Reason for failure" }
    """
    try:
        # start date
        start = datetime.fromisoformat(base_date) if base_date else datetime.now()
        
        # adjusting value based on direction
        amount = abs(value) if direction == 'future' else -abs(value)
        
        # calculation
        if unit == 'days':
            result = start + relativedelta(days=amount)
        elif unit == 'weeks':
            result = start + relativedelta(weeks=amount)
        elif unit == 'months':
            result = start + relativedelta(months=amount)
        elif unit == 'years':
            result = start + relativedelta(years=amount)
        else:
            return {'ok': False, 'error': f'Invalid unit: {unit}'}
        
        processed_data =  {
            'base_date': start.strftime('%Y-%m-%d'),
            'target_date': result.strftime('%Y-%m-%d'),
            'day_of_week': result.strftime('%A'),
            'direction': direction,
            'description': f'{value} {unit} in the {direction}'
        }
        return {'ok': True, 'data': processed_data}
    except Exception as e:
        return {'ok': False, 'error': str(e)}



@tool('convert_time_zones')
def convert_time_zones(timestamp: str, from_tz: str, to_tz: str) -> dict:
    """
    Convert a timestamp from one timezone to another.

    Use this tool when the user asks:
    - "What time is 3 PM in New York in London?"
    - "Convert this timestamp to UTC"
    - "Show this time in my local timezone"

    Args:
        timestamp: ISO-formatted datetime string.
        from_tz: Source IANA timezone.
        to_tz: Target IANA timezone.

    Returns:
        On success:
            {
              "ok": true,
              "data": {
                "source": "...",
                "converted": "...",
                "converted_iso": "...",
                "target_timezone": "..."
              }
            }
        On failure:
            { "ok": false, "error": "Reason for failure" }
    """
    try:
        # parsing the ISO string and attach the source timezone info
        dt = datetime.fromisoformat(timestamp).replace(tzinfo=ZoneInfo(from_tz))
        
        # converting to the target timezone
        converted = dt.astimezone(ZoneInfo(to_tz))
        
        processed_data = {
            'source': f'{timestamp} ({from_tz})',
            'converted': converted.strftime('%Y-%m-%d %H:%M'),
            'converted_iso': converted.isoformat(),
            'target_timezone': to_tz
        }
        return {'ok': True, 'data': processed_data}
    
    except Exception as e:
        return {'ok': False, 'error': str(e)}