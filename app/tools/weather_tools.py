import requests


def get_weather_data(city_name: str) -> dict:
    """
    Retrieve a concise weather summary for a given city.

    Use this tool when the user asks about:
    - current weather conditions
    - temperature, humidity, wind
    - today's sunrise or sunset
    - short-term weather outlook, next 3-day forecast.

    Args:
        city_name: Name of the city or location.

    Returns:
        On success:
            {
              "ok": true,
              "data": {
                "location": "...",
                "current": {...},
                "today_stats": {...},
                "forecast": [...]
              }
            }
        On failure:
            { "ok": false, "error": "Weather data unavailable" }
    """
    try:
        url = f"https://wttr.in/{city_name}?format=j1"
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        full_data = response.json()

        # extracting Current Conditions
        current = full_data['current_condition'][0]
        
        # extracting today's overall forecast
        today = full_data['weather'][0]
        
        # simple multi-day summary
        forecast_summary = []
        for day in full_data['weather']:
            forecast_summary.append({
                "date": day['date'],
                "max_temperature": f"{day['maxtempC']}°C",
                "min_temperature": f"{day['mintempC']}°C",
                "condition": day['hourly'][4]['weatherDesc'][0]['value'] # Mid-day desc
            })

        # costructing the slimmed-down dictionary
        processed_data = {
            "location": f"{full_data['nearest_area'][0]['areaName'][0]['value']}, {full_data['nearest_area'][0]['country'][0]['value']}",
            "current": {
                "temperature": f"{current['temp_C']}°C",
                "feels_like": f"{current['FeelsLikeC']}°C",
                "condition": current['weatherDesc'][0]['value'],
                "humidity": f"{current['humidity']}%",
                "wind": f"{current['windspeedKmph']} km/h",
                "uv_index": current['uvIndex']
            },
            "today_stats": {
                "sunrise": today['astronomy'][0]['sunrise'],
                "sunset": today['astronomy'][0]['sunset'],
                "rain_chance": f"{today['hourly'][0]['chanceofrain']}%", 
            },
            "forecast": forecast_summary,
            "note": "AQI data not available."
        }

        return {'ok': True, 'data': processed_data}

    except requests.exceptions.RequestException as e:
        return {'ok': False, 'error': str(e)}