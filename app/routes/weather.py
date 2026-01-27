"""
Weather Routes
Handles weather data API endpoints.
"""
from flask import Blueprint, jsonify, request
from app.services.weather_service import WeatherService
from app.services.notification_service import NotificationService

weather_bp = Blueprint('weather', __name__)


@weather_bp.route('/current/<city>', methods=['GET'])
def get_current_weather(city):
    """
    Get current weather for a city.
    
    Args:
        city: City name
    
    Returns:
        JSON response with current weather data
    """
    result = WeatherService.get_current_weather(city)
    
    if not result['success']:
        return jsonify(result), 404
    
    # Generate alerts
    alerts = NotificationService.generate_alerts(result['data'])
    
    # Get recommendations
    recommendations = NotificationService.get_weather_recommendation(result['data'])
    
    return jsonify({
        'success': True,
        'data': result['data'],
        'alerts': alerts,
        'recommendations': recommendations,
        'cached': result.get('cached', False)
    }), 200


@weather_bp.route('/forecast/<city>', methods=['GET'])
def get_forecast(city):
    """
    Get 5-day weather forecast for a city.
    
    Args:
        city: City name
    
    Returns:
        JSON response with forecast data
    """
    result = WeatherService.get_forecast(city)
    
    if not result['success']:
        return jsonify(result), 404
    
    # Get current weather for alerts
    current_result = WeatherService.get_current_weather(city)
    current_data = current_result['data'] if current_result['success'] else None
    
    # Generate alerts including forecast
    alerts = NotificationService.generate_alerts(current_data, result['data'])
    
    return jsonify({
        'success': True,
        'data': result['data'],
        'alerts': alerts,
        'cached': result.get('cached', False)
    }), 200


@weather_bp.route('/aqi/<city>', methods=['GET'])
def get_air_quality(city):
    """
    Get Air Quality Index for a city.
    
    Args:
        city: City name
    
    Returns:
        JSON response with AQI data
    """
    result = WeatherService.get_air_quality(city)
    
    if not result['success']:
        return jsonify(result), 404
    
    return jsonify({
        'success': True,
        'data': result['data'],
        'cached': result.get('cached', False)
    }), 200


@weather_bp.route('/search/<query>', methods=['GET'])
def search_cities(query):
    """
    Search for cities (auto-suggest).
    
    Args:
        query: Search query
    
    Returns:
        JSON response with list of matching cities
    """
    if len(query) < 2:
        return jsonify({
            'success': False,
            'error': 'Query must be at least 2 characters'
        }), 400
    
    result = WeatherService.search_cities(query)
    
    if not result['success']:
        return jsonify(result), 500
    
    return jsonify(result), 200


@weather_bp.route('/complete/<city>', methods=['GET'])
def get_complete_weather(city):
    """
    Get complete weather data (current + forecast + AQI) for a city.
    
    Args:
        city: City name
    
    Returns:
        JSON response with all weather data
    """
    # Fetch all data
    current = WeatherService.get_current_weather(city)
    forecast = WeatherService.get_forecast(city)
    aqi = WeatherService.get_air_quality(city)
    
    if not current['success']:
        return jsonify(current), 404
    
    # Generate comprehensive alerts
    alerts = NotificationService.generate_alerts(
        current['data'],
        forecast['data'] if forecast['success'] else None
    )
    
    # Get recommendations
    recommendations = NotificationService.get_weather_recommendation(current['data'])
    
    return jsonify({
        'success': True,
        'current': current['data'],
        'forecast': forecast['data'] if forecast['success'] else None,
        'aqi': aqi['data'] if aqi['success'] else None,
        'alerts': alerts,
        'recommendations': recommendations
    }), 200
