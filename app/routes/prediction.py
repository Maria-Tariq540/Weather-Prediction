"""
Prediction Routes
Handles ML prediction API endpoints.
"""
from flask import Blueprint, jsonify, request
from app.services.prediction_service import PredictionService
from app.utils.decorators import admin_required

prediction_bp = Blueprint('prediction', __name__)


@prediction_bp.route('/<city>', methods=['GET'])
def get_prediction(city):
    """
    Get ML-based weather prediction for a city.
    
    Args:
        city: City name
    
    Query Parameters:
        days: Number of days to predict (default 7, max 14)
        model: Model type ('linear_regression' or 'random_forest', default 'random_forest')
    
    Returns:
        JSON response with prediction data
    """
    # Get query parameters
    days = request.args.get('days', default=7, type=int)
    model_type = request.args.get('model', default='random_forest', type=str)
    
    # Validate parameters
    if days < 1 or days > 14:
        return jsonify({'error': 'Days must be between 1 and 14'}), 400
    
    if model_type not in ['linear_regression', 'random_forest']:
        return jsonify({'error': 'Invalid model type'}), 400
    
    # Get prediction
    result = PredictionService.predict_weather(city, days, model_type)
    
    if not result['success']:
        return jsonify(result), 500
    
    return jsonify(result), 200


@prediction_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Get model accuracy metrics.
    
    Returns:
        JSON response with model metrics
    """
    result = PredictionService.get_model_metrics()
    
    if not result['success']:
        return jsonify(result), 500
    
    return jsonify(result), 200


@prediction_bp.route('/compare/<city>', methods=['GET'])
def compare_models(city):
    """
    Compare predictions from different models.
    
    Args:
        city: City name
    
    Query Parameters:
        days: Number of days to predict (default 7)
    
    Returns:
        JSON response with predictions from all models
    """
    days = request.args.get('days', default=7, type=int)
    
    if days < 1 or days > 14:
        return jsonify({'error': 'Days must be between 1 and 14'}), 400
    
    result = PredictionService.compare_models(city, days)
    
    return jsonify(result), 200


@prediction_bp.route('/retrain', methods=['POST'])
@admin_required
def retrain_models():
    """
    Trigger model retraining (admin only).
    
    Returns:
        JSON response confirming retraining started
    """
    # In a production environment, this would trigger an async task
    # For now, return a message
    return jsonify({
        'success': True,
        'message': 'Model retraining initiated. This process runs in the background.',
        'note': 'In production, this would trigger an async task using Celery or similar.'
    }), 202
