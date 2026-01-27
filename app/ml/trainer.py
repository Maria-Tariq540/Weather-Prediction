"""
Model Trainer
Orchestrates the complete ML training pipeline.
"""
import os
import sys
import pandas as pd
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.ml.data_collector import DataCollector
from app.ml.preprocessor import WeatherPreprocessor
from app.ml.models import WeatherModel


class ModelTrainer:
    """Orchestrates the complete ML training pipeline."""
    
    def __init__(self, api_key, model_dir='app/ml/saved_models'):
        """
        Initialize model trainer.
        
        Args:
            api_key: OpenWeatherMap API key
            model_dir: Directory to save trained models
        """
        self.api_key = api_key
        self.model_dir = model_dir
        self.preprocessor = WeatherPreprocessor()
        self.models = {}
    
    def collect_training_data(self, cities, days=90):
        """
        Collect training data for specified cities.
        
        Args:
            cities: List of city names
            days: Number of days of historical data
        
        Returns:
            Combined DataFrame with all cities' data
        """
        print("=" * 60)
        print("STEP 1: COLLECTING TRAINING DATA")
        print("=" * 60)
        
        collector = DataCollector(self.api_key)
        all_data = []
        
        for city in cities:
            print(f"\nCollecting data for {city}...")
            df = collector.collect_historical_data(city, days)
            all_data.append(df)
        
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        print(f"\nTotal data points collected: {len(combined_df)}")
        print(f"Date range: {combined_df['date'].min()} to {combined_df['date'].max()}")
        
        # Save combined data
        os.makedirs('data', exist_ok=True)
        combined_df.to_csv('data/training_data.csv', index=False)
        print("Training data saved to data/training_data.csv")
        
        return combined_df
    
    def preprocess_data(self, df):
        """
        Preprocess data for training.
        
        Args:
            df: Raw data DataFrame
        
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        print("\n" + "=" * 60)
        print("STEP 2: PREPROCESSING DATA")
        print("=" * 60)
        
        # Prepare features
        print("\nEngineering features...")
        df_prepared = self.preprocessor.prepare_features(df)
        print(f"Features created: {len(df_prepared.columns)} columns")
        
        # Split data
        print("\nSplitting into train/test sets...")
        X_train, X_test, y_train, y_test = self.preprocessor.split_data(df_prepared)
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        print(f"Features: {len(X_train.columns)}")
        print(f"Targets: {list(y_train.columns)}")
        
        # Scale features
        print("\nScaling features...")
        X_train_scaled = self.preprocessor.fit_transform(X_train)
        X_test_scaled = self.preprocessor.transform(X_test)
        
        # Save preprocessor
        preprocessor_path = os.path.join(self.model_dir, 'preprocessor.pkl')
        self.preprocessor.save(preprocessor_path)
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_models(self, X_train, X_test, y_train, y_test):
        """
        Train multiple ML models.
        
        Args:
            X_train: Training features
            X_test: Test features
            y_train: Training targets
            y_test: Test targets
        
        Returns:
            Dictionary of trained models
        """
        print("\n" + "=" * 60)
        print("STEP 3: TRAINING MODELS")
        print("=" * 60)
        
        target_columns = list(y_train.columns)
        model_types = ['linear_regression', 'random_forest']
        
        for model_type in model_types:
            print(f"\n{'=' * 60}")
            print(f"Training {model_type.upper().replace('_', ' ')} model")
            print(f"{'=' * 60}")
            
            model = WeatherModel(model_type)
            
            # Train
            model.train(X_train, y_train, target_columns)
            
            # Evaluate
            model.evaluate(X_test, y_test, target_columns)
            
            # Save
            model.save(self.model_dir)
            
            # Store
            self.models[model_type] = model
        
        return self.models
    
    def display_summary(self):
        """Display training summary and model comparison."""
        print("\n" + "=" * 60)
        print("TRAINING SUMMARY")
        print("=" * 60)
        
        for model_type, model in self.models.items():
            print(f"\n{model_type.upper().replace('_', ' ')} Model:")
            print("-" * 60)
            
            for metric_key, metric_values in model.metrics.items():
                if '_test' in metric_key:
                    target = metric_key.replace('_test', '')
                    print(f"\n{target.upper()}:")
                    print(f"  MAE:  {metric_values['mae']:.2f}")
                    print(f"  RMSE: {metric_values['rmse']:.2f}")
                    print(f"  R²:   {metric_values['r2']:.4f}")
        
        print("\n" + "=" * 60)
        print("Models saved to:", self.model_dir)
        print("=" * 60)
    
    def run_full_pipeline(self, cities=None, days=90):
        """
        Run the complete training pipeline.
        
        Args:
            cities: List of cities for training data
            days: Number of days of historical data
        """
        if cities is None:
            cities = ['London', 'New York', 'Tokyo', 'Paris', 'Mumbai']
        
        print("\n" + "=" * 60)
        print("WEATHER PREDICTION MODEL TRAINING PIPELINE")
        print("=" * 60)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Cities: {', '.join(cities)}")
        print(f"Historical data: {days} days")
        
        # Step 1: Collect data
        df = self.collect_training_data(cities, days)
        
        # Step 2: Preprocess
        X_train, X_test, y_train, y_test = self.preprocess_data(df)
        
        # Step 3: Train models
        self.train_models(X_train, X_test, y_train, y_test)
        
        # Display summary
        self.display_summary()
        
        print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✓ Training pipeline completed successfully!")


def main():
    """Main function to run training."""
    # Get API key from environment
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    if not api_key:
        print("Error: OPENWEATHER_API_KEY environment variable not set")
        print("Please set it in your .env file or environment")
        sys.exit(1)
    
    # Create trainer
    trainer = ModelTrainer(api_key)
    
    # Run training pipeline
    cities = ['London', 'New York', 'Tokyo', 'Paris', 'Mumbai', 'Sydney', 'Dubai']
    trainer.run_full_pipeline(cities=cities, days=90)


if __name__ == '__main__':
    main()
