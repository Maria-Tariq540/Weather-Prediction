"""
ML Models
Defines and trains machine learning models for weather prediction.
"""
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import joblib
import os


class WeatherModel:
    """Base class for weather prediction models."""
    
    def __init__(self, model_type='random_forest'):
        """
        Initialize weather model.
        
        Args:
            model_type: Type of model ('linear_regression' or 'random_forest')
        """
        self.model_type = model_type
        self.models = {}  # Separate model for each target
        self.metrics = {}
    
    def create_model(self):
        """Create a new model instance based on model_type."""
        if self.model_type == 'linear_regression':
            return LinearRegression()
        elif self.model_type == 'random_forest':
            return RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def train(self, X_train, y_train, target_columns):
        """
        Train separate models for each target variable.
        
        Args:
            X_train: Training features
            y_train: Training targets
            target_columns: List of target column names
        
        Returns:
            Dictionary with training metrics
        """
        print(f"\nTraining {self.model_type} models...")
        
        for target in target_columns:
            print(f"Training model for {target}...")
            
            model = self.create_model()
            model.fit(X_train, y_train[target])
            
            self.models[target] = model
            
            # Calculate training metrics
            y_pred = model.predict(X_train)
            self.metrics[f'{target}_train'] = {
                'mae': mean_absolute_error(y_train[target], y_pred),
                'rmse': np.sqrt(mean_squared_error(y_train[target], y_pred)),
                'r2': r2_score(y_train[target], y_pred)
            }
        
        return self.metrics
    
    def evaluate(self, X_test, y_test, target_columns):
        """
        Evaluate models on test data.
        
        Args:
            X_test: Test features
            y_test: Test targets
            target_columns: List of target column names
        
        Returns:
            Dictionary with evaluation metrics
        """
        print(f"\nEvaluating {self.model_type} models...")
        
        for target in target_columns:
            y_pred = self.models[target].predict(X_test)
            
            self.metrics[f'{target}_test'] = {
                'mae': mean_absolute_error(y_test[target], y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test[target], y_pred)),
                'r2': r2_score(y_test[target], y_pred)
            }
            
            print(f"\n{target.upper()} - Test Metrics:")
            print(f"  MAE:  {self.metrics[f'{target}_test']['mae']:.2f}")
            print(f"  RMSE: {self.metrics[f'{target}_test']['rmse']:.2f}")
            print(f"  R²:   {self.metrics[f'{target}_test']['r2']:.4f}")
        
        return self.metrics
    
    def predict(self, X):
        """
        Make predictions for all targets.
        
        Args:
            X: Features for prediction
        
        Returns:
            Dictionary with predictions for each target
        """
        predictions = {}
        
        for target, model in self.models.items():
            predictions[target] = model.predict(X)
        
        return predictions
    
    def predict_future(self, current_data, days=7):
        """
        Predict weather for future days.
        Note: This is a simplified iterative prediction.
        
        Args:
            current_data: Current weather data (DataFrame)
            days: Number of days to predict
        
        Returns:
            List of prediction dictionaries
        """
        predictions = []
        
        # Use the last available data as starting point
        last_data = current_data.iloc[-1:].copy()
        
        for day in range(1, days + 1):
            # Predict next day
            pred = self.predict(last_data)
            
            prediction_dict = {
                'day': day,
                'temperature': float(pred['temperature'][0]) if 'temperature' in pred else 0,
                'humidity': float(pred['humidity'][0]) if 'humidity' in pred else 0,
                'rainfall': max(0, float(pred['rainfall'][0])) if 'rainfall' in pred else 0
            }
            
            predictions.append(prediction_dict)
            
            # Update last_data with predictions for next iteration
            # This is a simplified approach; in practice, you'd update all lag features
            if 'temperature' in pred:
                last_data['temperature'] = pred['temperature'][0]
            if 'humidity' in pred:
                last_data['humidity'] = pred['humidity'][0]
        
        return predictions
    
    def save(self, directory):
        """
        Save all models and metrics.
        
        Args:
            directory: Directory to save models
        """
        os.makedirs(directory, exist_ok=True)
        
        # Save each model
        for target, model in self.models.items():
            filepath = os.path.join(directory, f'{self.model_type}_{target}_model.pkl')
            joblib.dump(model, filepath)
            print(f"Saved {target} model to {filepath}")
        
        # Save metrics
        metrics_filepath = os.path.join(directory, f'{self.model_type}_metrics.pkl')
        joblib.dump(self.metrics, metrics_filepath)
        print(f"Saved metrics to {metrics_filepath}")
    
    @classmethod
    def load(cls, directory, model_type, target_columns):
        """
        Load models from directory.
        
        Args:
            directory: Directory containing saved models
            model_type: Type of model
            target_columns: List of target column names
        
        Returns:
            WeatherModel instance with loaded models
        """
        model = cls(model_type)
        
        # Load each model
        for target in target_columns:
            filepath = os.path.join(directory, f'{model_type}_{target}_model.pkl')
            if os.path.exists(filepath):
                model.models[target] = joblib.load(filepath)
            else:
                print(f"Warning: Model file not found: {filepath}")
        
        # Load metrics
        metrics_filepath = os.path.join(directory, f'{model_type}_metrics.pkl')
        if os.path.exists(metrics_filepath):
            model.metrics = joblib.load(metrics_filepath)
        
        return model
    
    def get_feature_importance(self, feature_names, top_n=10):
        """
        Get feature importance for Random Forest models.
        
        Args:
            feature_names: List of feature names
            top_n: Number of top features to return
        
        Returns:
            Dictionary with feature importance for each target
        """
        if self.model_type != 'random_forest':
            return None
        
        importance_dict = {}
        
        for target, model in self.models.items():
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1][:top_n]
            
            importance_dict[target] = [
                {
                    'feature': feature_names[i],
                    'importance': float(importances[i])
                }
                for i in indices
            ]
        
        return importance_dict
