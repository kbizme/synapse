from app.tools.weather_tools import get_weather_data
from app.tools.time_tools import get_current_time, calculate_date_relative, convert_time_zones
from app.tools.math_tools import scientific_calculator, calculate_statistics
from app.tools.knowledge_base import query_knowledge_base



TOOL_REGISTRY = {
    "get_weather_data": get_weather_data,
    "get_current_time": get_current_time,
    "calculate_date_relative": calculate_date_relative,
    "convert_time_zones": convert_time_zones,
    "scientific_calculator": scientific_calculator,
    "calculate_statistics": calculate_statistics,
    'query_knowledge_base': query_knowledge_base,

}