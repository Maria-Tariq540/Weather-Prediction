"""
Data Preprocessor
Prepares weather data for machine learning models.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os


class WeatherPreprocessor:
    """Preprocesses weather data for ML models."""
    
    def __init__(self):
        """Initialize preprocessor."""
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.target_columns = None
    
    def prepare_features(self, df):
        """
        Prepare features from raw weather data.
        
        Args:
            df: DataFrame with weather data
        
        Returns:
            DataFrame with engineered features
        """
        df = df.copy()
        
        # Ensure date column is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            
            # Extract time-based features
            df['day_of_year'] = df['date'].dt.dayofyear
            df['month'] = df['date'].dt.month
            df['day'] = df['date'].dt.day
            df['week_of_year'] = df['date'].dt.isocalendar().week
            
            # Cyclical encoding for seasonal patterns
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
            df['day_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365)
            df['day_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365)
        
        # Create lag features (previous days' data)
        for col in ['temperature', 'humidity', 'pressure']:
            if col in df.columns:
                df[f'{col}_lag1'] = df[col].shift(1)
                df[f'{col}_lag2'] = df[col].shift(2)
                df[f'{col}_lag3'] = df[col].shift(3)
        
        # Rolling averages
        for col in ['temperature', 'humidity']:
            if col in df.columns:
                df[f'{col}_rolling_mean_3'] = df[col].rolling(window=3, min_periods=1).mean()
                df[f'{col}_rolling_mean_7'] = df[col].rolling(window=7, min_periods=1).mean()
        
        # Drop rows with NaN values from lag features
        df = df.dropna()
        
        return df
    
    def split_data(self, df, target_cols=['temperature', 'humidity', 'rainfall'], test_size=0.2):
        """
        Split data into features and targets, then train/test sets.
        
        Args:
            df: DataFrame with prepared features
            target_cols: List of target column names
            test_size: Proportion of test set
        
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Define feature columns (exclude targets and date)
        exclude_cols = target_cols + ['date']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        self.feature_columns = feature_cols
        self.target_columns = target_cols
        
        X = df[feature_cols]
        y = df[target_cols]
        
        # Split into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, shuffle=False
        )
        
        return X_train, X_test, y_train, y_test
    
    def fit_transform(self, X_train):
        """
        Fit scaler on training data and transform.
        
        Args:
            X_train: Training features
        
        Returns:
            Scaled training features
        """
        X_train_scaled = self.scaler.fit_transform(X_train)
        return pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
    
    def transform(self, X):
        """
        Transform data using fitted scaler.
        
        Args:
            X: Features to transform
        
        Returns:
            Scaled features
        """
        X_scaled = self.scaler.transform(X)
        return pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
    
    def inverse_transform_targets(self, y_scaled, target_name):
        """
        Inverse transform predictions back to original scale.
        Note: This is a simplified version. For proper inverse transform,
        you'd need to scale targets separately.
        
        Args:
            y_scaled: Scaled predictions
            target_name: Name of the target variable
        
        Returns:
            Original scale predictions
        """
        # For simplicity, we're not scaling targets in this implementation
        return y_scaled
    
    def save(self, filepath):
        """
        Save preprocessor (scaler and metadata).
        
        Args:
            filepath: Path to save the preprocessor
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        preprocessor_data = {
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'target_columns': self.target_columns
        }
        
        joblib.dump(preprocessor_data, filepath)
        print(f"Preprocessor saved to {filepath}")
    
    @classmethod
    def load(cls, filepath):
        """
        Load preprocessor from file.
        
        Args:
            filepath: Path to saved preprocessor
        
        Returns:
            WeatherPreprocessor instance
        """
        preprocessor_data = joblib.load(filepath)
        
        preprocessor = cls()
        preprocessor.scaler = preprocessor_data['scaler']
        preprocessor.feature_columns = preprocessor_data['feature_columns']
        preprocessor.target_columns = preprocessor_data['target_columns']
        
        return preprocessor
    
    def prepare_prediction_input(self, current_data):
        """
        Prepare current weather data for prediction.
        
        Args:
            current_data: Dictionary with current weather data
        
        Returns:
            DataFrame ready for prediction
        """
        # Create DataFrame from current data
        df = pd.DataFrame([current_data])
        
        # Add time-based features
        df = self.prepare_features(df)
        
        # Select only the features used in training
        if self.feature_columns:
            # Fill missing features with 0 or mean values
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0
            
            df = df[self.feature_columns]
        
        return df
