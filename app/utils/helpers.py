"""Utility functions and helpers."""

def format_temperature(temp_kelvin, unit='celsius'):
    """
    Convert temperature from Kelvin to Celsius or Fahrenheit.
    
    Args:
        temp_kelvin: Temperature in Kelvin
        unit: 'celsius' or 'fahrenheit'
    
    Returns:
        Converted temperature
    """
    if unit == 'celsius':
        return round(temp_kelvin - 273.15, 1)
    elif unit == 'fahrenheit':
        return round((temp_kelvin - 273.15) * 9/5 + 32, 1)
    return temp_kelvin


def get_weather_icon(weather_code):
    """
    Map weather condition code to icon name.
    
    Args:
        weather_code: OpenWeatherMap weather condition code
    
    Returns:
        Icon filename
    """
    icon_map = {
        '01d': 'clear-day.svg',
        '01n': 'clear-night.svg',
        '02d': 'partly-cloudy-day.svg',
        '02n': 'partly-cloudy-night.svg',
        '03d': 'cloudy.svg',
        '03n': 'cloudy.svg',
        '04d': 'overcast.svg',
        '04n': 'overcast.svg',
        '09d': 'rain.svg',
        '09n': 'rain.svg',
        '10d': 'rain-day.svg',
        '10n': 'rain-night.svg',
        '11d': 'thunderstorm.svg',
        '11n': 'thunderstorm.svg',
        '13d': 'snow.svg',
        '13n': 'snow.svg',
        '50d': 'fog.svg',
        '50n': 'fog.svg',
    }
    return icon_map.get(weather_code, 'cloudy.svg')


def validate_coordinates(lat, lon):
    """
    Validate latitude and longitude values.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Boolean indicating if coordinates are valid
    """
    try:
        lat = float(lat)
        lon = float(lon)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except (ValueError, TypeError):
        return False


def get_aqi_category(aqi):
    """
    Get Air Quality Index category and color.
    
    Args:
        aqi: AQI value (1-5)
    
    Returns:
        Dictionary with category and color
    """
    categories = {
        1: {'category': 'Good', 'color': '#00e400'},
        2: {'category': 'Fair', 'color': '#ffff00'},
        3: {'category': 'Moderate', 'color': '#ff7e00'},
        4: {'category': 'Poor', 'color': '#ff0000'},
        5: {'category': 'Very Poor', 'color': '#8f3f97'}
    }
    return categories.get(aqi, {'category': 'Unknown', 'color': '#999999'})
