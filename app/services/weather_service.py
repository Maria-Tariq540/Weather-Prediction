"""
Weather Service
Integrates with OpenWeatherMap API for real-time weather data.
"""
import requests
from datetime import datetime, timedelta
from flask import current_app
from app import db
from app.models.weather_data import WeatherData
from app.utils.helpers import format_temperature, get_weather_icon, get_aqi_category


class WeatherService:
    """Service for fetching and caching weather data."""
    
    BASE_URL = 'https://api.openweathermap.org/data/2.5'
    GEO_URL = 'https://api.openweathermap.org/geo/1.0'
    
    @staticmethod
    def _get_api_key():
        """Get API key from configuration."""
        return current_app.config['OPENWEATHER_API_KEY']
    
    @staticmethod
    def _get_cached_data(city_name, data_type):
        """
        Retrieve cached weather data if available and not expired.
        
        Args:
            city_name: Name of the city
            data_type: Type of data ('current', 'forecast', 'aqi')
        
        Returns:
            Cached data dictionary or None
        """
        cached = WeatherData.query.filter_by(
            city_name=city_name.lower(),
            data_type=data_type
        ).first()
        
        if cached and not cached.is_expired():
            return cached.get_data()
        
        # Delete expired cache
        if cached:
            db.session.delete(cached)
            db.session.commit()
        
        return None
    
    @staticmethod
    def _cache_data(city_name, lat, lon, data_type, data):
        """
        Cache weather data in database.
        
        Args:
            city_name: Name of the city
            lat: Latitude
            lon: Longitude
            data_type: Type of data
            data: Data dictionary to cache
        """
        cache_timeout = current_app.config['WEATHER_CACHE_TIMEOUT']
        expires_at = datetime.utcnow() + timedelta(seconds=cache_timeout)
        
        cached = WeatherData(
            city_name=city_name.lower(),
            latitude=lat,
            longitude=lon,
            data_type=data_type,
            expires_at=expires_at
        )
        cached.set_data(data)
        
        db.session.add(cached)
        db.session.commit()
    
    @classmethod
    def get_current_weather(cls, city_name):
        """
        Get current weather for a city.
        
        Args:
            city_name: Name of the city
        
        Returns:
            Dictionary with current weather data
        """
        # Check cache first
        cached = cls._get_cached_data(city_name, 'current')
        if cached:
            return {'success': True, 'data': cached, 'cached': True}
        
        # Fetch from API
        api_key = cls._get_api_key()
        url = f'{cls.BASE_URL}/weather'
        params = {
            'q': city_name,
            'appid': api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check if city was found
            if 'cod' in data and data['cod'] == '404':
                return {'success': False, 'error': f'City "{city_name}" not found. Please check the spelling and try again.'}
            
            # Process and format data
            processed_data = {
                'city': data.get('name', city_name),
                'country': data.get('sys', {}).get('country', 'Unknown'),
                'latitude': data.get('coord', {}).get('lat', 0),
                'longitude': data.get('coord', {}).get('lon', 0),
                'temperature': format_temperature(data.get('main', {}).get('temp', 0)),
                'feels_like': format_temperature(data.get('main', {}).get('feels_like', 0)),
                'temp_min': format_temperature(data.get('main', {}).get('temp_min', 0)),
                'temp_max': format_temperature(data.get('main', {}).get('temp_max', 0)),
                'humidity': data.get('main', {}).get('humidity', 0),
                'pressure': data.get('main', {}).get('pressure', 0),
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'wind_deg': data.get('wind', {}).get('deg', 0),
                'clouds': data.get('clouds', {}).get('all', 0),
                'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                'weather': {
                    'main': data.get('weather', [{}])[0].get('main', 'Unknown'),
                    'description': data.get('weather', [{}])[0].get('description', 'No description').title(),
                    'icon': get_weather_icon(data.get('weather', [{}])[0].get('icon', '01d'))
                },
                'sunrise': datetime.fromtimestamp(data.get('sys', {}).get('sunrise', 0)).strftime('%H:%M') if data.get('sys', {}).get('sunrise') else 'N/A',
                'sunset': datetime.fromtimestamp(data.get('sys', {}).get('sunset', 0)).strftime('%H:%M') if data.get('sys', {}).get('sunset') else 'N/A',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Cache the data
            cls._cache_data(
                city_name,
                processed_data['latitude'],
                processed_data['longitude'],
                'current',
                processed_data
            )
            
            return {'success': True, 'data': processed_data, 'cached': False}
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {'success': False, 'error': f'City "{city_name}" not found. Please check the spelling.'}
            elif e.response.status_code == 401:
                return {'success': False, 'error': 'Invalid API key. Please check your OpenWeatherMap API key in .env file.'}
            else:
                return {'success': False, 'error': f'Weather service error: {str(e)}'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'No internet connection. Please check your network.'}
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timed out. Please try again.'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Failed to fetch weather data: {str(e)}'}
        except KeyError as e:
            return {'success': False, 'error': f'Invalid response format. The city might not be available in the weather database.'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}
    
    @classmethod
    def get_forecast(cls, city_name):
        """
        Get 5-day weather forecast for a city.
        
        Args:
            city_name: Name of the city
        
        Returns:
            Dictionary with forecast data
        """
        # Check cache first
        cached = cls._get_cached_data(city_name, 'forecast')
        if cached:
            return {'success': True, 'data': cached, 'cached': True}
        
        # Fetch from API
        api_key = cls._get_api_key()
        url = f'{cls.BASE_URL}/forecast'
        params = {
            'q': city_name,
            'appid': api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Process forecast data (group by day)
            daily_forecasts = {}
            
            for item in data['list']:
                date = datetime.fromtimestamp(item['dt']).date()
                date_str = date.strftime('%Y-%m-%d')
                
                if date_str not in daily_forecasts:
                    daily_forecasts[date_str] = {
                        'date': date_str,
                        'day_name': date.strftime('%A'),
                        'temps': [],
                        'humidity': [],
                        'weather': [],
                        'wind_speed': [],
                        'rain': 0
                    }
                
                daily_forecasts[date_str]['temps'].append(format_temperature(item['main']['temp']))
                daily_forecasts[date_str]['humidity'].append(item['main']['humidity'])
                daily_forecasts[date_str]['weather'].append({
                    'main': item['weather'][0]['main'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon']
                })
                daily_forecasts[date_str]['wind_speed'].append(item['wind']['speed'])
                
                if 'rain' in item:
                    daily_forecasts[date_str]['rain'] += item['rain'].get('3h', 0)
            
            # Calculate daily averages
            forecast_list = []
            for date_str, day_data in sorted(daily_forecasts.items())[:7]:
                forecast_list.append({
                    'date': day_data['date'],
                    'day_name': day_data['day_name'],
                    'temp_avg': round(sum(day_data['temps']) / len(day_data['temps']), 1),
                    'temp_min': round(min(day_data['temps']), 1),
                    'temp_max': round(max(day_data['temps']), 1),
                    'humidity': round(sum(day_data['humidity']) / len(day_data['humidity'])),
                    'wind_speed': round(sum(day_data['wind_speed']) / len(day_data['wind_speed']), 1),
                    'rainfall': round(day_data['rain'], 1),
                    'weather': {
                        'main': day_data['weather'][len(day_data['weather'])//2]['main'],
                        'description': day_data['weather'][len(day_data['weather'])//2]['description'].title(),
                        'icon': get_weather_icon(day_data['weather'][len(day_data['weather'])//2]['icon'])
                    }
                })
            
            processed_data = {
                'city': data['city']['name'],
                'country': data['city']['country'],
                'latitude': data['city']['coord']['lat'],
                'longitude': data['city']['coord']['lon'],
                'forecast': forecast_list,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Cache the data
            cls._cache_data(
                city_name,
                data['city']['coord']['lat'],
                data['city']['coord']['lon'],
                'forecast',
                processed_data
            )
            
            return {'success': True, 'data': processed_data, 'cached': False}
            
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Failed to fetch forecast data: {str(e)}'}
        except KeyError as e:
            return {'success': False, 'error': f'Invalid response format: {str(e)}'}
    
    @classmethod
    def get_air_quality(cls, city_name):
        """
        Get Air Quality Index for a city.
        
        Args:
            city_name: Name of the city
        
        Returns:
            Dictionary with AQI data
        """
        # Check cache first
        cached = cls._get_cached_data(city_name, 'aqi')
        if cached:
            return {'success': True, 'data': cached, 'cached': True}
        
        # First get coordinates
        coords = cls.get_coordinates(city_name)
        if not coords['success']:
            return coords
        
        lat = coords['data']['lat']
        lon = coords['data']['lon']
        
        # Fetch AQI from API
        api_key = cls._get_api_key()
        url = f'{cls.BASE_URL}/air_pollution'
        params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            aqi_value = data['list'][0]['main']['aqi']
            aqi_info = get_aqi_category(aqi_value)
            
            processed_data = {
                'city': city_name,
                'aqi': aqi_value,
                'category': aqi_info['category'],
                'color': aqi_info['color'],
                'components': data['list'][0]['components'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Cache the data
            cls._cache_data(city_name, lat, lon, 'aqi', processed_data)
            
            return {'success': True, 'data': processed_data, 'cached': False}
            
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Failed to fetch AQI data: {str(e)}'}
        except KeyError as e:
            return {'success': False, 'error': f'Invalid response format: {str(e)}'}
    
    @classmethod
    def get_coordinates(cls, city_name):
        """
        Get coordinates for a city using geocoding API.
        
        Args:
            city_name: Name of the city
        
        Returns:
            Dictionary with coordinates
        """
        api_key = cls._get_api_key()
        url = f'{cls.GEO_URL}/direct'
        params = {
            'q': city_name,
            'limit': 1,
            'appid': api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return {'success': False, 'error': 'City not found'}
            
            return {
                'success': True,
                'data': {
                    'name': data[0]['name'],
                    'country': data[0]['country'],
                    'lat': data[0]['lat'],
                    'lon': data[0]['lon']
                }
            }
            
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Failed to fetch coordinates: {str(e)}'}
    
    @classmethod
    def search_cities(cls, query):
        """
        Search for cities matching the query (for auto-suggest).
        
        Args:
            query: Search query
        
        Returns:
            List of matching cities
        """
        api_key = cls._get_api_key()
        url = f'{cls.GEO_URL}/direct'
        params = {
            'q': query,
            'limit': 5,
            'appid': api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            cities = []
            for item in data:
                cities.append({
                    'name': item['name'],
                    'country': item['country'],
                    'state': item.get('state', ''),
                    'lat': item['lat'],
                    'lon': item['lon']
                })
            
            return {'success': True, 'data': cities}
            
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Failed to search cities: {str(e)}'}
