from langchain.tools import tool
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta 
from typing import Literal



@tool('get_current_time')
def get_current_time(timezone: str = 'Asia/Kolkata') -> dict:
    """
    Get current date and time for an IANA timezone (e.g., 'UTC', 'America/New_York').
    Defaults to 'Asia/Kolkata'. Use for 'What time is it?' or current date queries.
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



@tool('calculate_date_relative')
def calculate_date_relative(base_date: str | None = None, 
                            value: int = 0, 
                            unit: Literal['days', 'weeks', 'months', 'years'] = 'days',
                            direction: Literal['future', 'past'] = 'future') -> dict:
    """
    Calculate a past or future date relative to 'base_date' (ISO YYYY-MM-DD).
    'base_date' defaults to today. Use for '10 days from now' or '3 weeks ago'.
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
    Convert an ISO timestamp from a source timezone to a target timezone.
    Use for queries like 'What time is 3 PM in New York in London?'.
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