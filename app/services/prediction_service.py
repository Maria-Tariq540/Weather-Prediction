"""
Prediction Service
Provides ML-based weather predictions using trained models.
"""
import os
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not installed. ML predictions will not be available.")

from datetime import datetime, timedelta
from flask import current_app
from app.services.weather_service import WeatherService

try:
    from app.ml.models import WeatherModel
    from app.ml.preprocessor import WeatherPreprocessor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML modules not available. Install pandas, numpy, and scikit-learn for ML predictions.")



class PredictionService:
    """Service for generating ML-based weather predictions."""
    
    _preprocessor = None
    _models = {}
    _last_load_time = None
    
    @classmethod
    def _load_models(cls):
        """Load trained models and preprocessor."""
        
        # Check if ML dependencies are available
        if not ML_AVAILABLE or not PANDAS_AVAILABLE:
            return False
        
        model_path = current_app.config['MODEL_PATH']
        
        # Check if models need to be reloaded
        if cls._preprocessor is None or cls._models == {}:
            try:
                # Load preprocessor
                preprocessor_path = os.path.join(model_path, 'preprocessor.pkl')
                if os.path.exists(preprocessor_path):
                    cls._preprocessor = WeatherPreprocessor.load(preprocessor_path)
                    print("Preprocessor loaded successfully")
                else:
                    print(f"Warning: Preprocessor not found at {preprocessor_path}")
                    return False
                
                # Load models
                target_columns = ['temperature', 'humidity', 'rainfall']
                
                for model_type in ['linear_regression', 'random_forest']:
                    try:
                        model = WeatherModel.load(model_path, model_type, target_columns)
                        cls._models[model_type] = model
                        print(f"{model_type} model loaded successfully")
                    except Exception as e:
                        print(f"Error loading {model_type} model: {e}")
                
                cls._last_load_time = datetime.now()
                return True
                
            except Exception as e:
                print(f"Error loading models: {e}")
                return False
        
        return True
    
    @classmethod
    def predict_weather(cls, city_name, days=7, model_type='random_forest'):
        """
        Predict weather for a city using ML models.
        
        Args:
            city_name: Name of the city
            days: Number of days to predict (default 7)
            model_type: Type of model to use
        
        Returns:
            Dictionary with prediction results
        """
        # Check if ML is available
        if not ML_AVAILABLE or not PANDAS_AVAILABLE:
            return {
                'success': False,
                'error': 'ML predictions not available. Please install pandas, numpy, and scikit-learn: pip install pandas numpy scikit-learn joblib'
            }
        
        # Load models if not already loaded
        if not cls._load_models():
            return {
                'success': False,
                'error': 'ML models not available. Please train models first.'
            }
        
        # Check if requested model exists
        if model_type not in cls._models:
            return {
                'success': False,
                'error': f'Model type {model_type} not available'
            }
        
        try:
            # Get current weather data
            current_result = WeatherService.get_current_weather(city_name)
            
            if not current_result['success']:
                return current_result
            
            current_data = current_result['data']
            
            # Prepare input data for prediction
            input_data = {
                'date': datetime.now(),
                'temperature': current_data['temperature'],
                'humidity': current_data['humidity'],
                'pressure': current_data['pressure'],
                'wind_speed': current_data['wind_speed'],
                'rainfall': 0  # Current doesn't have rainfall, use 0
            }
            
            # Create DataFrame and prepare features
            df = pd.DataFrame([input_data])
            df_prepared = cls._preprocessor.prepare_features(df)
            
            # Ensure all required features are present
            for col in cls._preprocessor.feature_columns:
                if col not in df_prepared.columns:
                    df_prepared[col] = 0
            
            df_prepared = df_prepared[cls._preprocessor.feature_columns]
            
            # Scale features
            df_scaled = cls._preprocessor.transform(df_prepared)
            
            # Make predictions
            model = cls._models[model_type]
            predictions = model.predict_future(df_scaled, days=days)
            
            # Format predictions with dates
            forecast = []
            for i, pred in enumerate(predictions):
                pred_date = datetime.now() + timedelta(days=i+1)
                forecast.append({
                    'date': pred_date.strftime('%Y-%m-%d'),
                    'day_name': pred_date.strftime('%A'),
                    'temperature': round(pred['temperature'], 1),
                    'humidity': max(0, min(100, round(pred['humidity'], 1))),
                    'rainfall': max(0, round(pred['rainfall'], 1)),
                    'temp_min': round(pred['temperature'] - 3, 1),  # Estimate
                    'temp_max': round(pred['temperature'] + 3, 1),  # Estimate
                })
            
            return {
                'success': True,
                'city': current_data['city'],
                'country': current_data['country'],
                'model_type': model_type,
                'forecast': forecast,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Prediction failed: {str(e)}'
            }
    
    @classmethod
    def get_model_metrics(cls):
        """
        Get accuracy metrics for all trained models.
        
        Returns:
            Dictionary with model metrics
        """
        if not ML_AVAILABLE or not PANDAS_AVAILABLE:
            return {
                'success': False,
                'error': 'ML models not available'
            }
        
        if not cls._load_models():
            return {
                'success': False,
                'error': 'ML models not available'
            }
        
        metrics_summary = {}
        
        for model_type, model in cls._models.items():
            metrics_summary[model_type] = {}
            
            for metric_key, metric_values in model.metrics.items():
                if '_test' in metric_key:
                    target = metric_key.replace('_test', '')
                    metrics_summary[model_type][target] = {
                        'mae': round(metric_values['mae'], 2),
                        'rmse': round(metric_values['rmse'], 2),
                        'r2': round(metric_values['r2'], 4),
                        'accuracy_percentage': round(max(0, metric_values['r2'] * 100), 1)
                    }
        
        return {
            'success': True,
            'metrics': metrics_summary,
            'last_trained': cls._last_load_time.isoformat() if cls._last_load_time else None
        }
    
    @classmethod
    def compare_models(cls, city_name, days=7):
        """
        Compare predictions from different models.
        
        Args:
            city_name: Name of the city
            days: Number of days to predict
        
        Returns:
            Dictionary with predictions from all models
        """
        results = {}
        
        for model_type in ['linear_regression', 'random_forest']:
            prediction = cls.predict_weather(city_name, days, model_type)
            if prediction['success']:
                results[model_type] = prediction['forecast']
        
        return {
            'success': True,
            'city': city_name,
            'predictions': results
        }
