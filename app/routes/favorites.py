"""
Favorites Routes
Handles user's favorite cities management.
"""
from flask import Blueprint, jsonify, request
from flask_login import current_user
from app import db
from app.models.favorite_city import FavoriteCity
from app.services.weather_service import WeatherService
from app.utils.decorators import login_required_api

favorites_bp = Blueprint('favorites', __name__)


@favorites_bp.route('/', methods=['GET'])
@login_required_api
def get_favorites():
    """
    Get user's favorite cities.
    
    Returns:
        JSON response with list of favorite cities
    """
    favorites = current_user.favorite_cities.all()
    
    return jsonify({
        'success': True,
        'favorites': [fav.to_dict() for fav in favorites]
    }), 200


@favorites_bp.route('/', methods=['POST'])
@login_required_api
def add_favorite():
    """
    Add a city to favorites.
    
    Request JSON:
        - city_name: str
    
    Returns:
        JSON response confirming addition
    """
    data = request.get_json()
    
    if not data or 'city_name' not in data:
        return jsonify({'error': 'City name is required'}), 400
    
    city_name = data['city_name'].strip()
    
    # Check if already in favorites
    existing = FavoriteCity.query.filter_by(
        user_id=current_user.id,
        city_name=city_name
    ).first()
    
    if existing:
        return jsonify({'error': 'City already in favorites'}), 400
    
    # Check maximum favorites limit
    max_favorites = 10
    if current_user.favorite_cities.count() >= max_favorites:
        return jsonify({'error': f'Maximum {max_favorites} favorite cities allowed'}), 400
    
    # Get city coordinates
    coords_result = WeatherService.get_coordinates(city_name)
    
    if not coords_result['success']:
        return jsonify({'error': 'City not found'}), 404
    
    coords = coords_result['data']
    
    # Add to favorites
    try:
        favorite = FavoriteCity(
            user_id=current_user.id,
            city_name=coords['name'],
            country=coords['country'],
            latitude=coords['lat'],
            longitude=coords['lon']
        )
        
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'City added to favorites',
            'favorite': favorite.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add favorite: {str(e)}'}), 500


@favorites_bp.route('/<int:favorite_id>', methods=['DELETE'])
@login_required_api
def remove_favorite(favorite_id):
    """
    Remove a city from favorites.
    
    Args:
        favorite_id: ID of the favorite city
    
    Returns:
        JSON response confirming removal
    """
    favorite = FavoriteCity.query.filter_by(
        id=favorite_id,
        user_id=current_user.id
    ).first()
    
    if not favorite:
        return jsonify({'error': 'Favorite city not found'}), 404
    
    try:
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'City removed from favorites'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove favorite: {str(e)}'}), 500


@favorites_bp.route('/weather', methods=['GET'])
@login_required_api
def get_favorites_weather():
    """
    Get current weather for all favorite cities.
    
    Returns:
        JSON response with weather data for all favorites
    """
    favorites = current_user.favorite_cities.all()
    
    weather_data = []
    
    for favorite in favorites:
        result = WeatherService.get_current_weather(favorite.city_name)
        
        if result['success']:
            weather_data.append({
                'favorite_id': favorite.id,
                'city': favorite.to_dict(),
                'weather': result['data']
            })
    
    return jsonify({
        'success': True,
        'data': weather_data
    }), 200
