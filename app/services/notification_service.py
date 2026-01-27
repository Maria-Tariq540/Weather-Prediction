"""
Notification Service
Generates weather alerts and notifications based on weather conditions.
"""
from datetime import datetime


class NotificationService:
    """Service for generating weather alerts and notifications."""
    
    # Alert thresholds
    THRESHOLDS = {
        'high_temp': 35,  # Celsius
        'low_temp': 0,
        'high_wind': 50,  # km/h
        'low_visibility': 1,  # km
        'high_humidity': 90,  # percentage
        'heavy_rain': 50  # mm
    }
    
    @classmethod
    def generate_alerts(cls, weather_data, forecast_data=None):
        """
        Generate weather alerts based on current and forecast data.
        
        Args:
            weather_data: Current weather data dictionary
            forecast_data: Optional forecast data dictionary
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        # Check current weather conditions
        if weather_data:
            alerts.extend(cls._check_current_weather(weather_data))
        
        # Check forecast for upcoming severe weather
        if forecast_data and 'forecast' in forecast_data:
            alerts.extend(cls._check_forecast(forecast_data['forecast']))
        
        return alerts
    
    @classmethod
    def _check_current_weather(cls, data):
        """Check current weather for alert conditions."""
        alerts = []
        
        # High temperature alert
        if data.get('temperature', 0) >= cls.THRESHOLDS['high_temp']:
            alerts.append({
                'type': 'heat_wave',
                'severity': 'warning',
                'title': 'Heat Wave Warning',
                'message': f"Very high temperature: {data['temperature']}°C. Stay hydrated and avoid prolonged sun exposure.",
                'icon': '🌡️'
            })
        
        # Low temperature alert
        if data.get('temperature', 100) <= cls.THRESHOLDS['low_temp']:
            alerts.append({
                'type': 'cold_wave',
                'severity': 'warning',
                'title': 'Cold Wave Warning',
                'message': f"Freezing temperature: {data['temperature']}°C. Dress warmly and protect exposed skin.",
                'icon': '❄️'
            })
        
        # High wind alert
        wind_speed_kmh = data.get('wind_speed', 0) * 3.6  # Convert m/s to km/h
        if wind_speed_kmh >= cls.THRESHOLDS['high_wind']:
            alerts.append({
                'type': 'high_wind',
                'severity': 'warning',
                'title': 'High Wind Warning',
                'message': f"Strong winds: {round(wind_speed_kmh, 1)} km/h. Secure loose objects and avoid outdoor activities.",
                'icon': '💨'
            })
        
        # Low visibility alert
        if data.get('visibility', 100) <= cls.THRESHOLDS['low_visibility']:
            alerts.append({
                'type': 'low_visibility',
                'severity': 'caution',
                'title': 'Low Visibility',
                'message': f"Poor visibility: {data['visibility']} km. Drive carefully and use fog lights.",
                'icon': '🌫️'
            })
        
        # High humidity alert
        if data.get('humidity', 0) >= cls.THRESHOLDS['high_humidity']:
            alerts.append({
                'type': 'high_humidity',
                'severity': 'info',
                'title': 'High Humidity',
                'message': f"Very humid conditions: {data['humidity']}%. May feel uncomfortable.",
                'icon': '💧'
            })
        
        # Thunderstorm alert
        if data.get('weather', {}).get('main', '').lower() == 'thunderstorm':
            alerts.append({
                'type': 'thunderstorm',
                'severity': 'warning',
                'title': 'Thunderstorm Alert',
                'message': "Thunderstorm detected. Stay indoors and avoid using electronic devices.",
                'icon': '⛈️'
            })
        
        # Snow alert
        if data.get('weather', {}).get('main', '').lower() == 'snow':
            alerts.append({
                'type': 'snow',
                'severity': 'caution',
                'title': 'Snow Alert',
                'message': "Snowfall detected. Roads may be slippery. Drive with caution.",
                'icon': '🌨️'
            })
        
        return alerts
    
    @classmethod
    def _check_forecast(cls, forecast_list):
        """Check forecast for upcoming severe weather."""
        alerts = []
        
        # Check next 3 days for heavy rain
        for day in forecast_list[:3]:
            if day.get('rainfall', 0) >= cls.THRESHOLDS['heavy_rain']:
                alerts.append({
                    'type': 'heavy_rain',
                    'severity': 'warning',
                    'title': 'Heavy Rain Expected',
                    'message': f"Heavy rainfall expected on {day['day_name']}: {day['rainfall']} mm. Flooding possible.",
                    'icon': '🌧️',
                    'date': day['date']
                })
        
        return alerts
    
    @classmethod
    def get_weather_recommendation(cls, weather_data):
        """
        Get personalized recommendations based on weather.
        
        Args:
            weather_data: Current weather data dictionary
        
        Returns:
            Dictionary with recommendations
        """
        recommendations = {
            'clothing': [],
            'activities': [],
            'health': []
        }
        
        temp = weather_data.get('temperature', 20)
        weather_main = weather_data.get('weather', {}).get('main', '').lower()
        
        # Clothing recommendations
        if temp >= 30:
            recommendations['clothing'].append("Wear light, breathable clothing")
            recommendations['clothing'].append("Don't forget sunscreen and sunglasses")
        elif temp >= 20:
            recommendations['clothing'].append("Light clothing is suitable")
        elif temp >= 10:
            recommendations['clothing'].append("Wear a light jacket")
        else:
            recommendations['clothing'].append("Dress warmly with layers")
            recommendations['clothing'].append("Wear a warm coat and gloves")
        
        # Activity recommendations
        if weather_main in ['clear', 'clouds']:
            recommendations['activities'].append("Great day for outdoor activities")
        elif weather_main == 'rain':
            recommendations['activities'].append("Indoor activities recommended")
            recommendations['activities'].append("Carry an umbrella if going out")
        elif weather_main == 'snow':
            recommendations['activities'].append("Perfect for winter sports")
            recommendations['activities'].append("Drive carefully on icy roads")
        
        # Health recommendations
        if temp >= 35:
            recommendations['health'].append("Stay hydrated - drink plenty of water")
            recommendations['health'].append("Avoid strenuous outdoor activities")
        elif weather_data.get('humidity', 0) >= 80:
            recommendations['health'].append("High humidity - stay in ventilated areas")
        
        return recommendations
